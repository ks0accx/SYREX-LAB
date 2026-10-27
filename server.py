from flask import Flask, request, jsonify, send_from_directory, render_template
from pathlib import Path
import subprocess, threading, uuid, os, shutil, math, sys, webbrowser

# PyInstaller extracts bundled templates and ffmpeg.exe into _MEIPASS in --onefile mode.
SOURCE_ROOT = Path(__file__).resolve().parent
RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", SOURCE_ROOT))
APP_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else SOURCE_ROOT

# Persist input/output files outside PyInstaller's temporary extraction directory.
if getattr(sys, "frozen", False):
    DATA_ROOT = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "SYREX LAB"
else:
    DATA_ROOT = APP_ROOT
WORK = DATA_ROOT / "jobs"
WORK.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    template_folder=str(RESOURCE_ROOT / "templates"),
    static_folder=str(RESOURCE_ROOT / "static"),
)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2 GB upload limit
jobs = {}
lock = threading.Lock()


def ffmpeg_path():
    # Prefer FFmpeg bundled into the one-file executable; retain developer PATH fallback.
    exe_name = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
    for candidate in (RESOURCE_ROOT / exe_name, APP_ROOT / exe_name):
        if candidate.is_file():
            return str(candidate)
    path = shutil.which('ffmpeg')
    if not path:
        raise RuntimeError('Bundled FFmpeg was not found. Rebuild the desktop app with ffmpeg.exe included.')
    return path


def worker(job_id, input_path, output_path, ratio, keep_audio):
    log_path = WORK / job_id / 'ffmpeg.log'
    args = [ffmpeg_path(), '-hide_banner', '-y', '-i', str(input_path), '-vf', f'setpts=PTS/{ratio:.12f}', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23', '-pix_fmt', 'yuv420p']
    if keep_audio:
        # The existing interface constrains the ratio to 0.5x..2x for this filter.
        args += ['-af', f'atempo={ratio:.12f}', '-c:a', 'aac', '-b:a', '192k']
    else:
        args += ['-an']
    args += ['-movflags', '+faststart', str(output_path)]
    with lock:
        jobs[job_id]['status'] = 'running'
        jobs[job_id]['log'] = 'Starting FFmpeg…\n'
    try:
        with open(log_path, 'w', encoding='utf-8', errors='replace') as log:
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if os.name == 'nt' else 0
            proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors='replace', bufsize=1, creationflags=creationflags
            )
            for line in proc.stdout:
                log.write(line)
                log.flush()
                with lock:
                    jobs[job_id]['log'] = (jobs[job_id]['log'] + line)[-40000:]
            code = proc.wait()
        with lock:
            if code == 0 and output_path.exists() and output_path.stat().st_size:
                jobs[job_id]['status'] = 'done'
                jobs[job_id]['message'] = 'Conversion completed.'
            else:
                jobs[job_id]['status'] = 'failed'
                jobs[job_id]['message'] = f'FFmpeg exited with code {code}. Check the log.'
    except Exception as e:
        with lock:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['message'] = str(e)
            jobs[job_id]['log'] += '\nERROR: ' + str(e)


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/api/convert')
def convert():
    file = request.files.get('video')
    try:
        source_bpm = float(request.form.get('original_bpm', ''))
        target_bpm = float(request.form.get('remix_bpm', ''))
    except ValueError:
        return jsonify(error='Enter valid numeric BPM values.'), 400
    if not file or not file.filename:
        return jsonify(error='Choose a video file first.'), 400
    if not (math.isfinite(source_bpm) and math.isfinite(target_bpm) and source_bpm > 0 and target_bpm > 0):
        return jsonify(error='BPM values must be positive numbers.'), 400
    ratio = target_bpm / source_bpm
    if not 0.5 <= ratio <= 2.0:
        return jsonify(error='This version supports speed ratios from 0.5× to 2×.'), 400
    keep_audio = request.form.get('keep_audio', 'true').lower() == 'true'
    job_id = uuid.uuid4().hex[:12]
    job_dir = WORK / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.m4v'}:
        suffix = '.mp4'
    input_path = job_dir / ('input' + suffix)
    output_path = job_dir / 'BPM_SYNC.mp4'
    file.save(input_path)
    with lock:
        jobs[job_id] = {'status':'queued','ratio':ratio,'output':str(output_path),'message':'Queued','log':'Upload received.\n'}
    thread = threading.Thread(target=worker, args=(job_id,input_path,output_path,ratio,keep_audio), daemon=True)
    thread.start()
    return jsonify(job_id=job_id, ratio=ratio), 202


@app.get('/api/status/<job_id>')
def status(job_id):
    with lock:
        job = jobs.get(job_id)
        if not job:
            return jsonify(error='Job not found.'), 404
        return jsonify(status=job['status'], ratio=job['ratio'], message=job.get('message',''), log=job.get('log',''), download_url=f'/api/download/{job_id}' if job['status']=='done' else None)


@app.get('/api/download/<job_id>')
def download(job_id):
    with lock:
        job = jobs.get(job_id)
        if not job or job['status'] != 'done':
            return jsonify(error='Output is not ready.'), 404
        path = Path(job['output'])
    return send_from_directory(path.parent, path.name, as_attachment=True, download_name='BPM_SYNC.mp4')


if __name__ == '__main__':
    try:
        ffmpeg_path()
    except RuntimeError as e:
        print('ERROR:', e)
        print('Install FFmpeg, then run this server again.')
        raise SystemExit(1)
    url = 'http://127.0.0.1:5000'
    print('SYREX LAB running at ' + url)
    if getattr(sys, 'frozen', False):
        # If someone explicitly runs server.py as a frozen executable, retain prior behavior.
        threading.Timer(1.2, lambda: webbrowser.open_new(url)).start()
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True, use_reloader=False)
