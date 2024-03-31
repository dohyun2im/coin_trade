from trade import trade
from dotenv import load_dotenv
import os

load_dotenv()

acc_key = os.getenv("UPBIT_ACCESS_KEY")
sec_key = os.getenv("UPBIT_SECRET_KEY")
slack_token = os.getenv("SLACK_TOKEN")

tradingBot = trade(acc_key, sec_key, slack_token,"KRW-SHIB")
tradingBot.start()