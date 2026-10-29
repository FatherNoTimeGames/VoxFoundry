import argparse
import threading
import webbrowser
from urllib.parse import urlencode

import uvicorn

from voxfoundry.api.app import create_app
from voxfoundry.config import load_settings


def main():
    parser = argparse.ArgumentParser(description="VoxFoundry local library (no model downloads)")
    parser.add_argument("--library", help="Absolute library location outside the application")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--no-browser", action="store_true", help="Do not open a browser (API health only)"
    )
    args = parser.parse_args()
    try:
        settings = load_settings(args.library, args.port)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    app = create_app(settings)
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=settings.port, access_log=False)
    )
    if not args.no_browser:
        url = f"http://127.0.0.1:{settings.port}/#" + urlencode({"token": app.state.bootstrap})

        def open_when_ready():
            import time

            while not server.started and not server.should_exit:
                time.sleep(0.1)
            if server.started:
                webbrowser.open(url)

        threading.Thread(target=open_when_ready, daemon=True).start()
    # The one-time token is passed directly to the browser, never printed to logs.
    server.run()


if __name__ == "__main__":
    main()
