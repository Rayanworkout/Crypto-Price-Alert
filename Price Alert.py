import time
import requests
import schedule

TELEGRAM_BOT_TOKEN = 'MY BOT TOKEN'
TELEGRAM_CHAT_ID = 'MY CHAT ID'
CMC_API_KEY = 'MY API KEY'


# Put the same cryptos in "cryptos" in "alerts" and in "count"  (to be improved)

cryptos = {  # THE CRYPTOS YOU WANT TO TRACK
    'DOT': (0, 0),
    'SOL': (0, 0),
    'DYDX': (0, 0),
    'EGLD': (0, 0)
}


down_alerts = {  # WHEN PRICE DROPS TO THIS LEVEL (Stop Loss for example)
    'DOT': 50,
    'SOL': 134,
    'DYDX': 22,
    'EGLD': 200

}


up_alerts = {  # OR PUMP TO THIS PRICE (Take Profit)
    'DOT': 70,
    'SOL': 200,
    'DYDX': 27,
    'EGLD': 300

}

count = {
    'DOT': 0,
    'SOL': 0,
    'DYDX': 0,
    'EGLD': 0


}


def launch():
    print("Bot Running...")

    d = ('\n'.join("{}: {}".format(k, v) for k, v in down_alerts.items()))
    e = ('\n'.join("{}: {}".format(k, v) for k, v in up_alerts.items()))
    requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}"
                 .format(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, "Price Alert bot ✅"))
    time.sleep(2.5)
    requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}"
                 .format(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, f"Current alerts 📲 ️\n ️\n{d}"))
    time.sleep(2.5)
    requests.get(
        "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}"
        .format(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, f"As well as ⤵️ ️\n ️\n{e}"))


def get_alerts():
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': CMC_API_KEY}
    for crypto in cryptos:
        parameters = {'symbol': crypto, 'convert': 'USD'}
        response = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest', headers=headers,
                                params=parameters).json()
        price = round(response['data'][crypto]['quote']['USD']['price'], 2)
        percent_change_24h = round(response['data'][crypto]['quote']['USD']['percent_change_24h'], 2)
        cryptos.update({crypto: (price, percent_change_24h)})
    for i in cryptos:
        if cryptos[i][0] <= down_alerts[i] and count[i] != 1:
            requests.get(
                "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}"
                    .format(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, f"⚠️ {i}/USD: {cryptos[i][0]} USD ( {cryptos[i][1]}% 24h )  📉️"))
            count.update({i: 1})
            time.sleep(2)
            continue
        if cryptos[i][0] >= up_alerts[i] and count[i] != 1:
            requests.get(
                "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}"
                    .format(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, f"✅️ {i}/USD: {cryptos[i][0]} USD ( {cryptos[i][1]}% 24h )  📈"))
            count.update({i: 1})
            time.sleep(2)
            continue
        requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}"
                     .format(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, f"Could not send alert"))


def reset_count():
    for x in count:
        count.update({x: 0})


launch()
schedule.every(18).minutes.do(get_alerts)  # 18 minutes = 320 requests / day for 4 cryptos


schedule.every(12).hours.do(reset_count)  # Count is reset every 12 hours in order not to get spammed
while True:
    schedule.run_pending()
    time.sleep(1)
