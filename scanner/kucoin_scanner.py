
import yaml, pandas as pd
from kucoin.client import Market
from utils.slack_notifier import send_slack_alert
from datetime import datetime

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def log_alert(symbol, change, volume):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([[now, "[SCANNER]", symbol, change, volume]],
                      columns=["time", "source", "symbol", "price_change(%)", "volume"])
    df.to_csv("alerts.csv", mode="a", index=False, header=not pd.io.common.file_exists("alerts.csv"))
    msg = f"[SCANNER] {symbol} | Δ{change:.2f}% | Vol: {volume:.2f}"
    print(msg)
    send_slack_alert(msg)

def scan():
    cfg = load_config()
    client = Market()
    tickers = client.get_all_tickers()['ticker']

    for t in tickers:
        if not any(t['symbol'].endswith(q) for q in cfg['scanner']['quote_currency']):
            continue
        try:
            change = float(t['changeRate']) * 100
            vol = float(t['volValue'])

            if abs(change) >= cfg['scanner']['price_change_percent'] or vol >= cfg['scanner']['volume_threshold']:
                log_alert(t['symbol'], change, vol)
        except:
            continue

if __name__ == "__main__":
    scan()
