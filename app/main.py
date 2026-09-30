from pathlib import Path

import webview

from api import Api

FRONTEND_DIR = Path(__file__).parent / "frontend"

def main():
    api = Api()
    webview.create_window(
        title="Validador de Arquivo",
        url=str(FRONTEND_DIR / "index.html"),
        js_api=api,
        width=560,
        height=520,
        resizable=True,
        min_size=(440, 420),
    )
    webview.start()

if __name__ == "__main__":
    main()
