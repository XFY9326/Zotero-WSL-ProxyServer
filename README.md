# Zotero-WSL-ProxyServer

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

Make [Zotero](https://learn.microsoft.com/en-us/windows/wsl/install) on Windows hosts accessible in [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) or [Docker based on WSL2](https://docs.docker.com/desktop/wsl/)

## Introduction

As we all know, writing Latex under WSL is much faster than under Windows. I like to use Zotero to edit paper citations while using VSCode to write Latex. Here is a way to edit paper citations using Zotero on Windows while writing Latex using WSL.

## Features

- Open HTTP proxy only for WSL IP address
- No third-party dependencies are used
- Easy to use out of the box

## Usage

1. Download [latest exe release](https://github.com/XFY9326/Zotero-WSL-ProxyServer/releases/latest) or just use [Python script](https://raw.githubusercontent.com/XFY9326/Zotero-WSL-ProxyServer/master/main.py)

2. Launch proxy server and Zotero

   The output will be as follows:

    ```
   Windows host IP in WSL: [Windows ip in WSL]
   Zotero status: Running
   Server type: ThreadingHTTPServer
   
   Serving on [Windows ip in WSL]:23119
   Zotero WSL url: http://[Windows name in WSL].local:23119
   Zotero WSL ping check: curl -I http://[Windows name in WSL].local:23119/connector/ping
   <Press Control-C to exit>
   -------------------- Request Log --------------------
    ```

3. Modify server url in VSCode Zotero Extension

   Here is how to modify [Zotero LaTeX](https://marketplace.visualstudio.com/items?itemName=bnavetta.zoterolatex) and [Citation Picker for Zotero](https://marketplace.visualstudio.com/items?itemName=mblode.zotero) server in settings.json:

   ```json
   {
      "zotero.serverUrl": "http://[Windows name in WSL].local:23119",
      "zotero-citation-picker.port": "http://[Windows name in WSL].local:23119/better-bibtex/cayw?format=pandoc"
   }
   ```

   If you are using Docker based on WSL2 instead of running Latex directly in WSL, you will need to use the following configuration:

   ```json
   {
      "zotero.serverUrl": "http://[Windows ip in WSL]:23119",
      "zotero-citation-picker.port": "http://[Windows ip in WSL]:23119/better-bibtex/cayw?format=pandoc"
   }
   ```

5. Enjoy citation (or not :P)

## One more thing

You can set the .bib file exported in BetterTex to automatically update and export it directly to ``\\wsl.localhost\Ubuntu\home\``.

## Working principle

The first premise is that WSL2 cannot access the port under 127.0.0.1 of the Windows host. Because the two of them are completely isolated system environments.

The working principle of the proxy server is very simple, that is, it listens to the IP address of the Windows host in WSL and forwards it to the local Zotero.

```
VSCode [WSL] ----> Proxy ----> Zotero [Windows]
```

Although you can directly create port forwarding through netsh.exe and use the New-NetFirewallRule command to allow external access to the port, Zotero will detect the Host header
in the Http request and give an "Invalid header" error.

Therefore, I used the Http server that comes with Python to implement automatic monitoring and modified the requests that need to be forwarded to meet the needs of Zotero.

Since the proxy server is written in Python, a window asking for firewall permissions will pop up automatically when it is run for the first time. So there is no need to manually
configure the firewall anymore.
