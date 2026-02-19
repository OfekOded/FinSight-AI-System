import subprocess
import sys
import time

commands = [
    [sys.executable, "server/api_gateway.py"],
    [sys.executable, "server/services/auth_service.py"],
    [sys.executable, "server/services/finance_service.py"],
    [sys.executable, "server/services/ai_service.py"],
    [sys.executable, "client/main.py"]
]

processes = []

try:
    for cmd in commands:
        process = subprocess.Popen(cmd)
        processes.append(process)
        time.sleep(1)

    for process in processes:
        process.wait()

except KeyboardInterrupt:
    for process in processes:
        process.terminate()
    sys.exit(0)