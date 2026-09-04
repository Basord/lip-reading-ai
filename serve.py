"""Local preview that mimics GitHub Pages URL resolution.

GitHub Pages serves `foo.html` at `/foo` and `dir/index.html` at `/dir/`.
Python's built-in http.server does not, so extensionless links 404 locally
even though they work in production. This adds that one behaviour.

    python serve.py          # http://localhost:8000
    python serve.py 3000     # custom port
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))


class PagesHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        local = super().translate_path(path)
        if os.path.isdir(local) or os.path.isfile(local):
            return local
        # /articles/foo -> /articles/foo.html
        if os.path.isfile(local + ".html"):
            return local + ".html"
        return local

    def send_error(self, code, message=None, explain=None):
        # Serve the real 404.html so the custom page can be checked too.
        custom = os.path.join(ROOT, "404.html")
        if code == 404 and os.path.isfile(custom):
            body = open(custom, "rb").read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return
        super().send_error(code, message, explain)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.chdir(ROOT)
    print("Serving %s at http://localhost:%d  (Ctrl+C to stop)" % (ROOT, port))
    ThreadingHTTPServer(("127.0.0.1", port), PagesHandler).serve_forever()
