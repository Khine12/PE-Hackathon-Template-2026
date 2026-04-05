import requests
import time
import json
from datetime import datetime

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1490148939364569160/hcvy5d9Wg-PJeAXTNTfTmty1h3-Yb4edgkHBr1U698mBGDVWtWMBm1DRBUzcHEt6Mzcx"
HEALTH_URL = "http://nginx:80/health"
PRODUCTS_URL = "http://nginx:80/products"
CHECK_INTERVAL = 30

consecutive_failures = 0
error_count = 0
total_checks = 0

def send_discord_alert(title, description, color=16711680):
    """Send alert to Discord. Red=16711680, Green=65280, Orange=16753920"""
    payload = {
        "embeds": [{
            "title": f"🚨 ALERT: {title}",
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "PE Hackathon Monitor"}
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
        print(f"[ALERT SENT] {title}")
    except Exception as e:
        print(f"[ALERT FAILED] {e}")

def send_recovery(title, description):
    send_discord_alert(f"✅ RECOVERED: {title}", description, color=65280)

def check_health():
    global consecutive_failures
    try:
        resp = requests.get(HEALTH_URL, timeout=5)
        if resp.status_code == 200:
            if consecutive_failures >= 2:
                send_recovery("Service Back Online",
                    f"Health check passing again after {consecutive_failures} failures.")
            consecutive_failures = 0
            print(f"[{datetime.now().isoformat()}] Health OK")
            return True
        else:
            consecutive_failures += 1
            print(f"[{datetime.now().isoformat()}] Health FAIL (status {resp.status_code}) - streak: {consecutive_failures}")
    except requests.exceptions.RequestException as e:
        consecutive_failures += 1
        print(f"[{datetime.now().isoformat()}] Health FAIL (unreachable) - streak: {consecutive_failures}")

    if consecutive_failures == 2:
        send_discord_alert("Service Down",
            f"Health check has failed {consecutive_failures} consecutive times.\n"
            f"Endpoint: {HEALTH_URL}\n"
            f"Time: {datetime.now().isoformat()}")
    return False

def check_error_rate():
    global error_count, total_checks
    total_checks += 1
    try:
        resp = requests.get(PRODUCTS_URL, timeout=5)
        if resp.status_code >= 500:
            error_count += 1
    except:
        error_count += 1

    if total_checks >= 5:
        rate = (error_count / total_checks) * 100
        if rate > 10:
            send_discord_alert("High Error Rate",
                f"Error rate is {rate:.1f}% ({error_count}/{total_checks} requests failed).\n"
                f"Time: {datetime.now().isoformat()}")
        error_count = 0
        total_checks = 0

if __name__ == "__main__":
    print("🔍 PE Hackathon Monitor started...")
    print(f"   Checking every {CHECK_INTERVAL}s")
    print(f"   Alerts → Discord webhook")
    send_discord_alert("Monitor Started",
        "Health check monitoring is now active.", color=3447003)

    while True:
        check_health()
        check_error_rate()
        time.sleep(CHECK_INTERVAL)