import os

from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_file_name(prefix: str) -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log_message(msg, log_file):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    log_file = os.path.join(LOG_DIR, log_file)
    with open(log_file, "a") as f:
        f.write(full_msg + "\n")