import threading
import webview
import webbrowser

from app import app, ensure_data_file


class Api:
    def minimize_window(self):
        webview.windows[0].minimize()
    
    def close_window(self):
        webview.windows[0].destroy()
    
    def open_url(self, url):
        webbrowser.open(url)


def run_flask():
    ensure_data_file()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
    )


if __name__ == "__main__":
    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )
    flask_thread.start()

    api = Api()
    webview.create_window(
        title="Job Tracker",
        url="http://127.0.0.1:5000",
        width=1200,
        height=800,
        resizable=True,
        fullscreen=True,
        on_top=False,
        shadow=True,
        js_api=api
    )

    webview.start()