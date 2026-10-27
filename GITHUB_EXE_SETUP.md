# Get a Windows EXE from GitHub — SYREX LAB

This kit adds a GitHub Actions build to your **existing combined SYREX LAB project**. It does not include your full current UI; keep your current `templates/index.html` and `static/` files.

## 1. Put these files into your current project

Extract the kit ZIP and copy these items into the root of the combined project folder:

- `.github/workflows/build-windows.yml`
- `server.py` (replace the old server.py with this packaged-app-compatible version)
- `FFMPEG-LICENSE-INFO.txt`

Keep your own `templates/index.html`, `requirements.txt`, and `static/` directory. Do not replace your current HTML with the old UI from another project ZIP.

The intended project structure is:

```text
SYREX_LAB/
├── .github/
│   └── workflows/
│       └── build-windows.yml
├── templates/
│   └── index.html         # keep your combined SYREX LAB UI
├── static/
├── server.py
├── requirements.txt
└── FFMPEG-LICENSE-INFO.txt
```

## 2. Upload the project to GitHub

1. Sign in at https://github.com and click **+ → New repository**.
2. Enter `SYREX-LAB`, choose Public or Private, then create the repository.
3. On the repository page, click **Add file → Upload files**.
4. Upload the files and folders from your project, including the `.github/workflows/build-windows.yml` file. Make sure `.github` exists in the repository; it is hidden on some file pickers, so uploading through GitHub Desktop or Git is more reliable if you cannot select it.
5. Click **Commit changes**.

## 3. Download the built EXE

1. Open your repository on GitHub and select **Actions**.
2. Open **Build SYREX LAB for Windows**.
3. Wait for the green check mark; open that workflow run.
4. Under **Artifacts**, download `SYREX-LAB-Windows`.
5. Extract the downloaded ZIP. Keep `SYREX_LAB.exe` and `ffmpeg.exe` side-by-side, then double-click `SYREX_LAB.exe`. It starts the local server and opens the UI in your browser.

The Action creates the EXE on a Windows runner because PyInstaller builds are OS-specific. It also downloads FFmpeg so video conversion works without separately installing Python or FFmpeg. The ZIP contains FFmpeg license/build information.

## 4. Put a permanent download under GitHub Releases (optional)

After a successful commit/build, go to **Code → Releases → Create a new release**, create a tag such as `v1.0.0`, and publish it. Pushing a tag starting with `v` (for example `v1.0.0`) also triggers this workflow to attach `SYREX_LAB-Windows.zip` to a Release automatically.

## Important

- This is a local web app packaged as an EXE, not a native desktop window; it opens in your browser at `http://127.0.0.1:5000`.
- Extract both EXE files to the same folder before running.
- If Windows SmartScreen warns about an unknown publisher, that is expected for an unsigned personal build. Only run builds you trust.
- The workflow uses a GPL FFmpeg build to support the app's H.264/libx264 export. Review FFmpeg's license and corresponding-source requirements before redistributing the built package publicly.
