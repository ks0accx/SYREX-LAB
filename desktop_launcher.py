"""SYREX LAB v1.1 desktop launcher.

Runs the existing Flask app privately on loopback and renders it in an embedded
WebView2 window. It does not open an external browser or a console window.
"""
import threading
import tkinter as tk
from tkinter import messagebox


def show_error(title, message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message, parent=root)
    root.destroy()


def main():
    try:
        import webview
        from werkzeug.serving import make_server
        import server
    except Exception as exc:
        show_error("SYREX LAB could not start", f"Desktop components could not be loaded.\n\n{exc}")
        return 1

    try:
        server.ffmpeg_path()
    except Exception as exc:
        show_error("SYREX LAB setup error", str(exc))
        return 1

    httpd = None
    try:
        httpd = make_server("127.0.0.1", 0, server.app, threaded=True)
        port = httpd.server_port
        threading.Thread(target=httpd.serve_forever, name="SYREX-LAB-server", daemon=True).start()

        # Enable download links inside the desktop window; do not launch a browser.
        webview.settings["ALLOW_DOWNLOADS"] = True
        webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
        webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False

        webview.create_window(
            "SYREX LAB v1.1",
            f"http://127.0.0.1:{port}/",
            width=1420,
            height=920,
            min_size=(980, 680),
            resizable=True,
            text_select=True,
            confirm_close=True,
            background_color="#f5f4ed",
        )
        # Requires the Microsoft Edge WebView2 Runtime on Windows.
        webview.start(debug=False, gui="edgechromium")
        return 0
    except Exception as exc:
        show_error(
            "SYREX LAB could not open its desktop window",
            "The embedded WebView2 window could not start. Ensure the Microsoft "
            "Edge WebView2 Runtime is installed, then reopen SYREX LAB.\n\n"
            f"Details: {exc}",
        )
        return 1
    finally:
        if httpd is not None:
            try:
                httpd.shutdown()
                httpd.server_close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
