"""
Shadowprint Stage Demo Trigger: Rug-Pull Flag Simulator.
Simulates a live server mutation by creating/updating the trigger flag file.
When touched, Fixture 5 (rugpull_suite) mutates its tool definitions,
triggering Engine S3's live integrity alert.
"""

import os
import sys
import time

FLAG_PATHS = [
    "/tmp/rugpull_trigger.flag",
    os.path.join(os.environ.get("TEMP", "/tmp"), "rugpull_trigger.flag")
]


def trigger_rugpull():
    print("[*] Simulating live MCP server rug-pull attack...")
    for flag_path in FLAG_PATHS:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(flag_path)), exist_ok=True)
            with open(flag_path, "w", encoding="utf-8") as f:
                f.write(f"TRIGGER_RUGPULL_TIMESTAMP={time.time()}\n")
            print(f"[+] Successfully wrote rugpull trigger flag to: {flag_path}")
        except Exception as e:
            print(f"[-] Could not write to {flag_path}: {e}")

    print("[!] Rug-pull flag is active! Engine S3 watcher should alert in < 1.5 seconds.")


if __name__ == "__main__":
    trigger_rugpull()
