import os
import platform
import socket
import sys
from http import HTTPStatus
from http.client import HTTPConnection
from typing import Any, Optional

# noinspection PyBroadException
try:
    from http.server import ThreadingHTTPServer as HTTPServer
except:
    from http.server import HTTPServer

from http.server import BaseHTTPRequestHandler

__product_name__ = "Zotero WSL ProxyServer"
__version__ = "0.1.0.3"
__author__ = "XFY9326"
__website__ = "https://github.com/XFY9326/Zotero-WSL-ProxyServer"

# Consts
ZOTERO_HOST = "127.0.0.1"
ZOTERO_PORT = 23119


def app_error_exit():
    print("\n")
    # Only support Windows
    os.system('pause')
    sys.exit(1)


def check_system_requirements():
    if platform.system().lower() != "windows":
        sys.stderr.write("WSL is a function provided by Windows!\n")
        app_error_exit()
    if os.system("wsl --status >nul 2>nul") != 0:
        sys.stderr.write("WSL is not enabled in current system!\n")
        app_error_exit()
    if os.system("ipconfig >nul 2>nul") != 0:
        sys.stderr.write("Can't read network interface info!\n")
        app_error_exit()


def get_process_name_by_pid(pid: int) -> Optional[str]:
    # noinspection PyBroadException
    try:
        with os.popen(f"tasklist | findstr \"{pid}\"") as p2:
            return p2.readline().split()[0].strip()
    except:
        return None


def check_port_used(host: str):
    with os.popen(f"netstat -ano | findstr \"{host}:{ZOTERO_PORT}\"") as p1:
        line = p1.readline()
        if "LISTENING" in line:
            pid = int(line.split()[-1].strip())
            process_name = get_process_name_by_pid(pid)
            if process_name is not None:
                sys.stderr.write(f"Port {host}:{ZOTERO_PORT} is already used by '{process_name}'!\n")
            else:
                sys.stderr.write(f"Port {host}:{ZOTERO_PORT} is already in use!\n")
            app_error_exit()


def get_wsl_host_ip() -> str:
    ip = None
    with os.popen("ipconfig") as p:
        is_right_adapter = False
        # noinspection PyBroadException
        try:
            for line in p:
                if "vEthernet" in line and "WSL" in line:
                    is_right_adapter = True
                elif is_right_adapter and "IPv4" in line:
                    ip = line.split(":")[1].strip()
                    break
        except:
            sys.stderr.write("Can't recognize WSL host IP address format!\n")
            app_error_exit()
    if ip is None:
        sys.stderr.write("Can't find WSL host IP address!\n")
        app_error_exit()
    else:
        return ip


def check_zotero_connector() -> bool:
    connection = HTTPConnection(host=ZOTERO_HOST, port=ZOTERO_PORT, timeout=2)
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
    sys_version = "Python/" + sys.version.split()[0]
    server_version = "Zotero-WSL-ProxyServer/" + __version__

    # noinspection PyShadowingBuiltins
    def log_error(self, format: str, *args: Any) -> None:
        sys.stderr.write("%s - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))

    # noinspection PyShadowingBuiltins
    def log_message(self, format: str, *args: Any) -> None:
        sys.stdout.write("%s - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))

    def _handle_zotero_request(self, method: str, path: str):
        # Solve "Invalid header" problem
        del self.headers["Host"]

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile if content_length != 0 else None

        connection = HTTPConnection(host=ZOTERO_HOST, port=ZOTERO_PORT)
        # noinspection PyBroadException
        try:
            connection.request(method=method, url=path, body=body, headers=self.headers)
            with connection.getresponse() as response:
                # Remove useless headers
                self.send_response(response.status)
                for k, v in response.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(response.read())
        except BaseException as e:
            if check_zotero_connector():
                self.log_error(f"Unknown proxy request error! Msg: {e}")
            else:
                self.log_error(f"Zotero is not running! Msg: {e}")
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
    print("Loading server ...", end='')
    httpd = HTTPServer(server_address=(host, ZOTERO_PORT), RequestHandlerClass=ZoteroProxyHttpHandler)
    # noinspection HttpUrlsUsage
    wsl_zotero_url = f"http://{socket.gethostname().lower()}.local:{ZOTERO_PORT}"
    serving_socket_info = httpd.socket.getsockname()
    print(f"\rServing on {serving_socket_info[0]}:{serving_socket_info[1]}")
    print(f"Zotero WSL url: {wsl_zotero_url}")
    print(f"Zotero WSL ping check: curl -I {wsl_zotero_url}/connector/ping")
    print("<Press Control-C to exit>")
    print("-------------------- Request Log --------------------")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt or SystemExit:
        print("\nKeyboard interrupt received. Exiting ...")
        httpd.server_close()
        sys.exit(0)


def main():
    check_system_requirements()
    wsl_host_ip = get_wsl_host_ip()
    print(f"{__product_name__}  v{__version__}")
    print(f"Made by {__author__}")
    print(f"Website: {__website__}\n")
    print("Windows host IP in WSL:", wsl_host_ip)
    print("Zotero status:", "Running" if check_zotero_connector() else "Not found")
    print("Server type:", HTTPServer.__name__, "\n")
    check_port_used(wsl_host_ip)
    launch_zotero_proxy_server(wsl_host_ip)


if __name__ == '__main__':
    main()
