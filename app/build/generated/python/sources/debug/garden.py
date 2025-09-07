#!/usr/bin/env python3
import requests
import time
from datetime import datetime, timedelta

API_URL = "https://gagstock.gleeze.com/grow-a-garden"
REFRESH = 2  # seconds

def parse_cd(cd_str):
    """
    Convert '00h 09m 32s' to timedelta.
    """
    h = m = s = 0
    if 'h' in cd_str:
        h = int(cd_str.split('h')[0])
    if 'm' in cd_str:
        m = int(cd_str.split('h')[-1].split('m')[0])
    if 's' in cd_str:
        s = int(cd_str.split('m')[-1].replace('s', '').strip())
    return timedelta(hours=h, minutes=m, seconds=s)

def format_td(td):
    """
    Format timedelta to '00h 09m 32s'.
    """
    total = int(td.total_seconds())
    if total < 0:
        return "00h 00m 00s"
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}h {m:02d}m {s:02d}s"

def fetch_data():
    resp = requests.get(API_URL)
    resp.raise_for_status()
    return resp.json()

def main():
    print(f"Watching shop API: {API_URL} — refresh every {REFRESH}s\n")
    shops = {}
    while True:
        try:
            payload = fetch_data()
            data = payload.get("data", {})

            print("\n" + "="*60)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Grow a Garden — Shop Tracker")
            print("="*60)

            for key, display in [
                ("egg", "Egg Shop"),
                ("seed", "Seed Shop"),
                ("gear", "Gear Shop"),
                ("travelingmerchant", "Traveling Merchant")
            ]:
                if key in data:
                    section = data[key]
                    items = section.get("items", [])
                    cd_str = section.get("countdown") or section.get("appearIn") or ""
                    cd_td = parse_cd(cd_str)

                    # Initialize or reset if items changed
                    if key not in shops or shops[key]["items"] != items:
                        shops[key] = {"items": items, "cd": cd_td}
                    else:
                        shops[key]["cd"] -= timedelta(seconds=REFRESH)

                    print(f"{display}:")
                    for item in shops[key]["items"]:
                        print(f"  {item.get('emoji', '')} {item.get('name')} x{item.get('quantity')}")
                    print(f"  Countdown: {format_td(shops[key]['cd'])}\n")

            print("="*60)
            time.sleep(REFRESH)

        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(REFRESH)

if __name__ == "__main__":
    main()









