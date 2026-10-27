# SYREX LAB v1.1

Combined producer workspace featuring **Piano Finder** and **Video BPM Sync**.

## Windows desktop EXE

The project now builds as a single-window Windows desktop app through GitHub Actions:
- No CMD/console window when opening the app.
- The interface runs inside an embedded WebView2 window; it does not open the HTML file in an external browser tab.
- FFmpeg is bundled inside the one-file EXE and launched without a console.
- MP4 exports and logs are stored under `%LOCALAPPDATA%\SYREX LAB\jobs`.

### Download
1. Open the **Actions** tab.
2. Select **Build SYREX LAB v1.1 Desktop EXE**.
3. Open the successful run's Summary and download `SYREX-LAB-v1.1-Desktop-Windows`.
4. Extract the ZIP and double-click `SYREX_LAB_v1.1.exe`.

### Requirements
Windows 10/11 with Microsoft Edge WebView2 Runtime. Most current Windows installations already have this runtime. If the app shows a WebView2 setup error, install the official Microsoft Edge WebView2 Runtime and try again.

## Build
The workflow `.github/workflows/build-windows.yml` builds automatically on commits to the repository and can also be run manually from Actions. It bundles FFmpeg, retains the FFmpeg license and build metadata alongside the EXE in the downloadable ZIP, and uses a no-console PyInstaller build.

## Video processing notes
The video is retimed using target BPM / original BPM. The original audio can be kept and sped by the same ratio, but pitch is not preserved. Conversion is re-encoded using FFmpeg H.264 with the ultrafast preset. The app's local API binds only to loopback. Review the included FFmpeg license information before redistributing builds.
