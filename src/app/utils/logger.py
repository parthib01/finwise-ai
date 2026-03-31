import json
from datetime import datetime
import time


def log_start(user_input: str):
    print("\n" + "=" * 60)
    print("🚀 NEW REQUEST")
    print(f"User Input: {user_input}")
    print("=" * 60)

    return time.time()  # ⏱️ return start time


def log_step(step_name: str, data: dict = None):
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"\n🟡 [{timestamp}] STEP: {step_name}")

    if data:
        try:
            print(json.dumps(data, indent=2, default=str))
        except Exception:
            print(data)


def log_end(response: str, start_time: float):
    end_time = time.time()
    total_time = end_time - start_time

    print("\n" + "=" * 60)
    print("✅ FINAL RESPONSE")
    print(response)

    print("\n⏱️ TOTAL EXECUTION TIME: {:.2f} seconds".format(total_time))
    print("=" * 60)