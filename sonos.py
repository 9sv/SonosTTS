import argparse
import os
import socket
import sys
import time
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from threading import Thread

import soco
from colorama import Fore, Style
from gtts import gTTS


class HttpServer(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        handler = SimpleHTTPRequestHandler
        self.httpd = TCPServer(("", 5555), handler)

    def run(self):
        print(f"\n[ {Fore.GREEN + Style.BRIGHT}SUCCESS{Fore.RESET} ] -> Starting HTTP server")
        self.httpd.serve_forever()

    def stop(self):
        print(f"\n[ {Fore.GREEN + Style.BRIGHT}SUCCESS{Fore.RESET} ] -> Stopping HTTP server")
        self.httpd.socket.close()

def local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def speak(device: soco.SoCo, text: str):
    device = soco.discovery.any_soco()
    device.volume = 75
    if os.path.exists("data/text.mp3"):
        os.remove("data/text.mp3")
    if not os.path.exists("data"):
        os.mkdir("data")
    gTTS(text, lang='en').save("data/text.mp3")
    time.sleep(1)
    netpath = "http://{0}:5555/data/text.mp3".format(local_ip())
    print("Serving [ {0}{1}{2} ] --> ".format(Fore.RED + Style.BRIGHT, netpath, Fore.RESET))
    device.play_uri(netpath)

def select_device() -> soco.SoCo:
    network = list(soco.discover(allow_network_scan=True))
    if len(network) <= 0:
        sys.exit(1)
    for index, device in enumerate(network):
        print("[ {0} ] \"{1}\" --> {2}\n".format(index, device.player_name, device.ip_address))
    selection = int(input("Which Sonos device would you like to target? - "))
    try:
        return network[selection]
    except (KeyError, TypeError):
        server.stop()
        sys.exit(1)

if __name__ == "__main__":
    server = HttpServer()
    server.start()
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("text", action="store")
        args = parser.parse_args()
        speak(select_device(), args.text)
        time.sleep(25)
        server.stop()
    except KeyboardInterrupt:
        server.stop()
