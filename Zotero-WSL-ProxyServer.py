import os
import socket
import sys
import platform
import argparse
from http import HTTPStatus
from http.client import HTTPConnection

# noinspection PyBroadException
try:
    from http.server import ThreadingHTTPServer as HTTPServer
except:
    from http.server import HTTPServer

from http.server import BaseHTTPRequestHandler

from socketserver import BaseServer
from typing import Tuple

ENABLE_REQUEST_LOG = False


def check_system_requirements():
    if platform.system().lower() != "windows":
        raise RuntimeError("WSL is a function provided by Windows!")
    if os.system("wsl --version >nul 2>nul") != 0:
        raise RuntimeError("WSL is not enabled or installed in current system!")
    if os.system("ipconfig >nul 2>nul") != 0:
        raise RuntimeError("Can't read network interface info!")


def check_port_used(host: str):
    with os.popen(f"netstat -ano | findstr \"{host}:23119\"") as p:
        if "LISTENING" in p.readline():
            raise SystemError(f"Port {host}:23119 is already in use!")


def get_wsl_host_ip() -> str:
    ip = None
    with os.popen("ipconfig") as p:
        is_right_adapter = False
        try:
            for line in p:
                if "vEthernet (WSL)" in line:
                    is_right_adapter = True
                elif is_right_adapter and "IPv4" in line:
                    ip = line.split(":")[1].strip()
                    break
        except:
            raise IOError("Can't recognize WSL host IP address format!")
    if ip is None:
        raise SystemError("Can't find WSL host IP address!")
    else:
        return ip


def check_zotero_connector() -> bool:
    connection = HTTPConnection(host="127.0.0.1", port=23119)
    # noinspection PyBroadException
    try:
        connection.request(method="GET", url="/connector/ping")
        with connection.getresponse() as response:
            return response.status == 200
    except:
        return False
    finally:
        connection.close()


class ZoteroProxyHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: BaseServer):
        super(ZoteroProxyHttpHandler, self).__init__(request, client_address, server)

    def _handle_zotero_request(self, method: str, path: str):
        # Solve "Invalid header" problem
        del self.headers["Host"]
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        connection = HTTPConnection(host="127.0.0.1", port=23119)
        # noinspection PyBroadException
        try:
            connection.request(method=method, url=path, body=body, headers=self.headers)
            with connection.getresponse() as response:
                # Remove useless headers
                if ENABLE_REQUEST_LOG:
                    self.log_request(response.status)
                self.send_response_only(response.status)
                for k, v in response.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(response.read())
        except:
            self.send_error(HTTPStatus.SERVICE_UNAVAILABLE)
        finally:
            connection.close()

    # Ref: BaseHTTPRequestHandler.handle_one_request
    # Handling all requests in one function instead of using reflection
    # noinspection SpellCheckingInspection,PyAttributeOutsideInit
    def handle_one_request(self):
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return
            self._handle_zotero_request(self.command, self.path)
            self.wfile.flush()
        except socket.timeout as e:
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return


def launch_zotero_proxy_server(host: str):
    print("\nPreparing server ... ...", end='')
    try:
        httpd = HTTPServer(server_address=(host, 23119), RequestHandlerClass=ZoteroProxyHttpHandler)
    except BaseException as e:
        print("\nServer start failed!")
        raise e
    # noinspection HttpUrlsUsage
    host_zotero_url = f"http://{host}:23119"
    # noinspection HttpUrlsUsage
    wsl_zotero_url = f"http://{socket.gethostname().lower()}.local:23119"
    print(f"\rServer launched in WSL: {host_zotero_url}")
    print(f"WSL url: {wsl_zotero_url}")
    print(f"WSL ping check: curl -I {wsl_zotero_url}/connector/ping")
    print("<Press Control-C to exit>")
    if ENABLE_REQUEST_LOG:
        print("-------------------- Request Log --------------------")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt or SystemExit:
        print("\nExiting ... ...")
        httpd.server_close()
        sys.exit(0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Zotero WSL proxy server')
    parser.add_argument('--log', help='Show request log in proxy server', action='store_true')
    return parser.parse_args()


def main():
    global ENABLE_REQUEST_LOG
    params = parse_args()
    ENABLE_REQUEST_LOG = params.log

    check_system_requirements()
    wsl_host_ip = get_wsl_host_ip()
    print("WSL host IP:", wsl_host_ip)
    check_port_used(wsl_host_ip)
    print("Zotero status:", "Running" if check_zotero_connector() else "Not found")
    print("Server type:", HTTPServer.__name__)
    launch_zotero_proxy_server(wsl_host_ip)


if __name__ == '__main__':
    main()
