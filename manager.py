import subprocess
import sys
import json
import time
import os
import threading
from datetime import datetime

PYTHON = sys.executable
LOG_FILE = "log.txt"


def write_log(bot_id, text):
    timestamp = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    line = f"[{timestamp}] [{bot_id}] {text}"

    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def clean_log_text(raw_line):
    line = raw_line.strip()
    if line.startswith("[OT"):
        parts = line.split("->", 1)
        if len(parts) == 2:
            return parts[1].strip()
    return line


# ========= THREAD ĐỌC LOG =========

def reader_thread(bot_id, proc):
    try:
        for line in proc.stdout:
            cleaned = clean_log_text(line)
            if cleaned:
                write_log(bot_id, cleaned)
    except Exception as e:
        write_log(bot_id, f"Reader thread error: {e}")


# ========= START BOT =========

def start_bot(bot):
    bot_id = bot["bot_id"]
    uid = bot["uid"]
    password = bot["password"]

    env = os.environ.copy()
    env["BOT_ID"] = bot_id
    env["BOT_UID"] = str(uid)
    env["BOT_PASS"] = password
    env["MANAGER_MODE"] = "1"

    write_log(bot_id, f"Starting main.py with UID {uid} ...")

    p = subprocess.Popen(
        [PYTHON, "-u", "main.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )

    t = threading.Thread(target=reader_thread, args=(bot_id, p), daemon=True)
    t.start()

    return p, t


# ========= MAIN =========

def main():
    with open("bots.json", "r", encoding="utf-8") as f:
        bots = json.load(f)

    processes = []

    for bot in bots:
        p, t = start_bot(bot)
        processes.append((bot["bot_id"], p, t))
        time.sleep(0.10)  # giảm tải khi start hàng loạt bot

    try:
        while True:
            for bot_id, p, t in processes:
                if p.poll() is not None:
                    write_log(bot_id, "Bot stopped. Restarting...")
                    new_p, new_t = start_bot({"bot_id": bot_id, "uid": os.environ["BOT_UID"], "password": os.environ["BOT_PASS"]})
                    processes.append((bot_id, new_p, new_t))
                    processes.remove((bot_id, p, t))
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping all bots...")
        for _, p, _ in processes:
            p.terminate()


if __name__ == "__main__":
    main()
