import requests
import json
import os

CATEGORY_ID = "men_trousers"
API_URL = f"https://www2.hm.com/hmwebservices/service/productlist/pl_pl/category/{CATEGORY_ID}.json"
HISTORY_FILE = "/data/history.json"  # Railway Volume

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


import requests

SCRAPER_API_KEY = "1bbcc17ee6175043f79329cce2ac4263"  # <-- wklej tu swój klucz ScraperAPI

def fetch_test():
    url = "https://www2.hm.com/pl_pl/on/produkty/spodnie.html"
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"

    r = requests.get(proxy_url)
    print("STATUS:", r.status_code)
    print("BODY:", r.text[:500])  # pierwsze 500 znaków HTML





def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def notify(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    })


def detect_changes(products, history):
    changes = []

    for p in products:
        pid = p["code"]
        name = p["name"]
        url = "https://www2.hm.com" + p["url"]

        price = float(p["price"]["value"])
        promo = None

        if "redPrice" in p["price"]:
            promo = float(p["price"]["redPrice"]["value"])

        old = history.get(pid)

        # Nowy produkt
        if not old:
            changes.append(f"🆕 Nowy produkt: {name}\n{url}")
        else:
            # Zmiana ceny regularnej
            if old["price"] != price:
                changes.append(
                    f"💰 Zmiana ceny: {name}\n"
                    f"{old['price']} zł → {price} zł\n{url}"
                )

            # Nowa promocja
            if promo and not old.get("promo"):
                changes.append(
                    f"🔥 Nowa promocja: {name}\n"
                    f"{price} zł → {promo} zł\n{url}"
                )

            # Zmiana ceny promocyjnej
            if promo and old.get("promo") and old["promo"] != promo:
                changes.append(
                    f"🔄 Zmiana ceny promocyjnej: {name}\n"
                    f"{old['promo']} zł → {promo} zł\n{url}"
                )

        # Zapis aktualnych danych
        history[pid] = {"price": price, "promo": promo}

    return changes, history


def main():
    products = fetch_products()
    history = load_history()
    changes, new_history = detect_changes(products, history)

    if changes:
        body = "\n\n".join(changes)
        notify(body)

    save_history(new_history)


if __name__ == "__main__":
    fetch_test()



