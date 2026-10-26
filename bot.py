import base64
import os
import random
import re
import sys
import time
import uuid
import requests

# 15 common User-Agents
USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/148.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/145.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/146.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101"
        " Firefox/137.0"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101"
        " Firefox/135.0"
    ),
    (
        "Mozilla/5.0 (Linux; Android 14; K) AppleWebKit/537.36 (KHTML, like"
        " Gecko) Chrome/148.0.0.0 Mobile Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/148.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Android 14; Mobile; rv:137.0) Gecko/137.0 Firefox/137.0"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
        " (KHTML, like Gecko) Version/18.3 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3 like Mac OS X) AppleWebKit/605.1.15"
        " (KHTML, like Gecko) Version/18.3 Mobile/15E148 Safari/604.1"
    ),
]

# Load confidential values securely from Environment Variables
PROXY_USER = os.getenv("PROXY_USER", "")
PROXY_PASS = os.getenv("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT = "823"


def run_sequence():
    if not PROXY_USER or not PROXY_PASS:
        print("[-] Error: PROXY_USER or PROXY_PASS environment variables are not set!")
        return

    # 1. Generate a unique session ID to force a brand new IP address on every request
    session_id = str(uuid.uuid4())
    dynamic_proxy_user = f"{PROXY_USER};sessid.{session_id}"

    proxy_url = f"http://{dynamic_proxy_user}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    proxies = {"http": proxy_url, "https": proxy_url}

    session = requests.Session()
    session.proxies.update(proxies)

    # 2. Generate 1st tracking URL
    base_prefix = "https://p.asdfix.com/go/506570/758963/"
    target_url = (
        "https://makrori.xyz/" if random.random() < 0.60 else "https://makrori.xyz"
    )
    encoded_url = (
        base64.b64encode(target_url.encode("utf-8")).decode("utf-8").strip()
    )
    cookie_buster = f"{random.randint(1000000000000000, 9999999999999999)}.{random.randint(0, 9)}"
    first_url = f"{base_prefix}{encoded_url}?cb={cookie_buster}"

    selected_ua = random.choice(USER_AGENTS)
    headers = {
        "Host": "p.asdfix.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": selected_ua,
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        ),
        "X-Requested-With": "mark.via.gp",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
    }

    print(f"\n----------------------------------------")
    print(f"[*] New Request Initiated | Session IP: {session_id[:8]}...")
    try:
        print(f"[*] Connecting via proxy and requesting 1st URL...")
        res1 = session.get(first_url, headers=headers, allow_redirects=True, timeout=30)
    except Exception as e:
        print(f"Process Failed (Proxy/Network Error: {e})")
        return

    # Extract href location from JS redirect script
    match = re.search(r'top\.location\.href\s*=\s*"([^"]+)"', res1.text)
    if not match:
        match = re.search(r"top\.location\.href\s*=\s*'([^']+)'", res1.text)

    if not match:
        print("Process Failed (Could not extract redirect href from script)")
        return

    extracted_path = match.group(1)
    second_url = f"http://p.asdfix.com{extracted_path}"

    # 3. Make GET request to 2nd link with Referer header pointing to 1st link
    headers_2nd = headers.copy()
    headers_2nd["Referer"] = first_url

    try:
        print("[*] Requesting 2nd URL...")
        res2 = session.get(
            second_url, headers=headers_2nd, allow_redirects=False, timeout=30
        )
    except Exception as e:
        print(f"Process Failed (Proxy/Network Error on 2nd request: {e})")
        return

    if res2.status_code == 302:
        print("Success")
    else:
        print(f"Process Failed (Status Code: {res2.status_code})")


def main():
    start_time = time.time()
    MAX_RUN_TIME = 5.5 * 3600  # 5.5 hours safety timeout (below GitHub's 6h limit)

    print("[*] Starting 24x7 automated sequence loop...")
    print(f"[*] Safety timeout set to {MAX_RUN_TIME / 3600} hours before auto-restart.")

    while True:
        # Check if 5.5 hours have elapsed
        if time.time() - start_time >= MAX_RUN_TIME:
            print("[*] Reached 5.5 hours execution limit. Exiting cleanly for auto-restart.")
            sys.exit(0)

        # Execute the request sequence
        run_sequence()

        # Wait between 40 to 50 seconds before the next loop
        wait_time = random.randint(40, 50)
        print(f"[*] Waiting {wait_time} seconds before next request...")
        time.sleep(wait_time)


if __name__ == "__main__":
    main()
