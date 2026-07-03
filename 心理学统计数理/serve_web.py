#!/usr/bin/env python3
"""构建交互网页并启动本地 HTTP 服务。"""

import importlib
import json
import socket
import subprocess
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
TEMPLATE = WEB_DIR / "index.template.html"
INDEX = WEB_DIR / "index.html"
PORT = 8765


def ensure_numpy():
    try:
        importlib.import_module("numpy")
    except ImportError:
        print("正在安装 numpy ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy", "-q"])


def build_index():
    ensure_numpy()
    import numpy as np

    np.random.seed(42)
    data = np.random.normal(loc=50, scale=10, size=200).tolist()
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__DATA__", json.dumps(data))
    INDEX.write_text(html, encoding="utf-8")


def find_free_port(start=PORT):
    port = start
    while port < start + 20:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    return start


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    if not TEMPLATE.exists():
        # 兼容：若模板不存在则直接使用现有 index.html
        if not INDEX.exists():
            raise SystemExit("缺少 web/index.template.html 或 web/index.html")
    else:
        build_index()

    port = find_free_port()
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    url = f"http://127.0.0.1:{port}/web/index.html"
    print("=" * 56)
    print("在线演示已启动")
    print(f"本地访问: {url}")
    print(f"局域网访问: http://{socket.gethostbyname(socket.gethostname())}:{port}/web/index.html")
    print("按 Ctrl+C 停止服务")
    print("=" * 56)
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()


if __name__ == "__main__":
    main()
