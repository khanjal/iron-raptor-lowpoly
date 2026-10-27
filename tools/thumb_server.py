"""A tiny server for rendering the thumbnails: serves the repo root and takes PNGs POSTed by tools/thumbs.html.

    python tools/thumb_server.py            # then open http://localhost:8766/tools/thumbs.html

POST /save/<id> with a PNG data URL as the body writes site/thumbs/<id>.png.
"""
import base64
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THUMBS = ROOT / "site" / "thumbs"


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        m = re.fullmatch(r"/save/([A-Za-z0-9_.-]+)", self.path)
        if not m:
            self.send_error(404)
            return
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("ascii")
        if not body.startswith("data:image/png;base64,"):
            self.send_error(400)
            return
        THUMBS.mkdir(parents=True, exist_ok=True)
        (THUMBS / f"{m.group(1)}.png").write_bytes(base64.b64decode(body.split(",", 1)[1]))
        self.send_response(204)
        self.end_headers()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(ROOT))).serve_forever()  # NOSONAR: local-only server on 127.0.0.1
