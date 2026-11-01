"""Local preview server that labels text files as UTF-8. usage: serve.py [port] [dir]

Works from any folder; dir defaults to the project root (the folder above scripts/), port to 8000."""
import errno, functools, http.server, pathlib, sys

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                      ".json": "application/json; charset=utf-8"}

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
root = sys.argv[2] if len(sys.argv) > 2 else str(pathlib.Path(__file__).resolve().parent.parent)
try:
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=root))
except OSError as e:
    if e.errno != errno.EADDRINUSE:
        raise
    sys.exit(f"Port {port} is already in use. If the server is already running, open http://localhost:{port}; "
             f"otherwise pick another port: python3 {sys.argv[0]} {port + 1}")
print(f"Serving {root} at http://localhost:{port}  (Ctrl+C to stop)", flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
