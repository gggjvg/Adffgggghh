"""Run the web radio and Highrise chat bot in one Railway service."""
import os, signal, subprocess, sys, time

web = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "webapp:app",
    "--host", "0.0.0.0", "--port", os.getenv("PORT", "8000")
])
bot = subprocess.Popen([sys.executable, "main.py"])

def stop(*_):
    for proc in (bot, web):
        if proc.poll() is None:
            proc.terminate()
    for proc in (bot, web):
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    raise SystemExit(0)

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)

while True:
    if web.poll() is not None or bot.poll() is not None:
        stop()
    time.sleep(2)
