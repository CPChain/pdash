import os

from signal import signal, SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM

def signal_handler(*args):
    os._exit(0)

def install_signal():
    for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
        signal(sig, signal_handler)
