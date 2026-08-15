#!/usr/bin/env python3
"""
start.py — start the SynBank backend and frontend together.

Usage:
    python3 start.py                 # start both backend and frontend
    python3 start.py --backend       # start backend only  (http://localhost:8000)
    python3 start.py --frontend      # start frontend only (http://localhost:3000)
"""

import argparse
import os
import shutil
import signal
import subprocess
import sys
import threading

ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT, "frontend")

# ANSI colours
BLUE  = "\033[94m"
GREEN = "\033[92m"
RESET = "\033[0m"
BOLD  = "\033[1m"


def prefix_stream(stream, prefix: str, colour: str):
    """Read lines from a process stream and print them with a coloured prefix."""
    try:
        for line in iter(stream.readline, b""):
            sys.stdout.write(f"{colour}{BOLD}{prefix}{RESET} {line.decode(errors='replace')}")
            sys.stdout.flush()
    except ValueError:
        pass  # stream closed


def start_backend() -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    threading.Thread(target=prefix_stream, args=(proc.stdout, "[backend]", BLUE), daemon=True).start()
    return proc


def start_frontend() -> subprocess.Popen:
    # On Windows npm is a .cmd shim, so the bare name is not an executable
    # Popen can launch. shutil.which resolves it on every platform.
    npm = shutil.which("npm") or ("npm.cmd" if os.name == "nt" else "npm")
    proc = subprocess.Popen(
        [npm, "run", "dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    threading.Thread(target=prefix_stream, args=(proc.stdout, "[frontend]", GREEN), daemon=True).start()
    return proc


def main():
    parser = argparse.ArgumentParser(description="SynBank dev launcher")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--backend", action="store_true")
    group.add_argument("--frontend", action="store_true")
    args = parser.parse_args()

    procs: list[subprocess.Popen] = []

    if not args.frontend:
        print(f"{BLUE}{BOLD}[backend]{RESET} starting on http://localhost:8000")
        procs.append(start_backend())

    if not args.backend:
        print(f"{GREEN}{BOLD}[frontend]{RESET} starting on http://localhost:3000")
        procs.append(start_frontend())

    def shutdown(sig, frame):
        print("\nShutting down...")
        for p in procs:
            p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Wait — if any process dies unexpectedly, kill the rest and exit.
    while True:
        for p in procs:
            if p.poll() is not None:
                print(f"\nProcess (pid={p.pid}) exited with code {p.returncode}. Shutting down.")
                for other in procs:
                    other.terminate()
                sys.exit(p.returncode)
        threading.Event().wait(1)


if __name__ == "__main__":
    main()
