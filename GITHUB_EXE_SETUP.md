# Get the SYREX LAB v1.1 Windows desktop EXE

The project is configured to build a **single-file desktop executable**. You no longer need to open CMD, run Python, or open the HTML in an external browser to use the compiled EXE.

## Build from GitHub
1. Open the repository and click **Actions**.
2. Select **Build SYREX LAB v1.1 Desktop EXE**.
3. Open the most recent run. Commits to `main` start a build automatically; you can also use **Run workflow**.
4. Wait for the green success check.
5. Open the run's **Summary** and download `SYREX-LAB-v1.1-Desktop-Windows`.
6. Extract that artifact ZIP and double-click `SYREX_LAB_v1.1.exe`.

## Runtime
- Windows 10/11.
- Microsoft Edge WebView2 Runtime. If missing, install the official Microsoft Edge WebView2 Runtime.
- No separate Python or FFmpeg installation is required for the compiled EXE.
- The HTML interface is rendered inside the desktop app window. It is still included as app resources, but it does not launch in a separate browser tab.
- FFmpeg's license and exact build information are included in the artifact ZIP. Review those terms before redistributing the app.

## Troubleshooting
If the workflow fails, open the failed Actions run, expand the red step, and inspect the first error. If the EXE opens then immediately closes or shows a WebView2 error, install/repair WebView2 Runtime and try again. For an FFmpeg error, open the app's Video BPM Sync log panel and keep the FFmpeg error text.

## Processing behavior
The original and target BPM fields produce an exact ratio (target/original). When the "keep audio" option is enabled, original audio is sped using the same ratio. This does not preserve the original audio pitch.
