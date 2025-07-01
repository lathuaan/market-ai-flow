
import yaml, pandas as pd
from kucoin.client import User, Market
from utils.slack_notifier import send_slack_alert
from datetime import datetime

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def log_whale(symbol, amount, usd):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([[now, "[WHALE]", symbol, amount, usd]],
                      columns=["time", "source", "symbol", "amount", "usd"])
    df.to_csv("alerts.csv", mode="a", index=False, header=not pd.io.common.file_exists("alerts.csv"))
    msg = f"[WHALE] {symbol} | Amount: {amount} | ≈ ${usd:.2f}"
    print(msg)
    send_slack_alert(msg)

def track():
    cfg = load_config()
    market = Market()
    user = User(cfg['kucoin']['api_key'], cfg['kucoin']['api_secret'], cfg['kucoin']['api_passphrase'])

    balances = user.get_account_list()
    prices = {i['symbol']: float(i['price']) for i in market.get_all_tickers()['ticker']}

    for asset in balances:
        coin = asset['currency']
        if coin not in cfg['watcher']['token_watchlist']:
            continue
        amount = float(asset['available']) + float(asset['holds'])
        price = prices.get(f"{coin}-USDT", 0)
        usd_value = amount * price
        if usd_value >= cfg['watcher']['min_transfer_usd']:
            log_whale(coin, amount, usd_value)

if __name__ == "__main__":
    track()
