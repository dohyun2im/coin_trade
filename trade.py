import pyupbit
import time
import datetime
import traceback
import atexit
from slack import slack

class trade :
    def __init__(self, acc_key, sec_key, slack_token, ticker) :
        self.upbit = pyupbit.Upbit(acc_key, sec_key)
        self.bot = slack(slack_token, "#coin")
        self.fee = 0.0005 # 거래 수수료 0.05% (매수+매도 수수료 0.1%)
        self.sell_percent = 1.0025 # 판매 예상 금액 0.25 (%)
        self.ticker = ticker # 티커
        self.purchase_avg = self.upbit.get_avg_buy_price(ticker) # 평균구매가
        self.cash = self.upbit.get_balance("KRW") # 현금
        self.coin = self.upbit.get_balance(ticker) # 코인
        self.coef3 = 0 # 3일 고저평균 돌파계수
        self.coef5 = 0 # 5일 고저평균 돌파계수
        self.coef10 = 0 # 10일 고저평균 돌파계수
        self.ma3 = 0 # 3일 이동평균
        self.ma5 = 0 # 5일 이동평균
        self.ma10 = 0 # 10일 이동평균
        self.minute = 0 # 현재 분

    def start(self) :
        now = datetime.datetime.now()
        formatted_time = "{}년 {}월 {}일 {}시 {}분 {}초".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
        self.get_today_data()
        self.bot.message("\n🏁 자동 매매를 시작합니다\n시작 시간 : " + formatted_time + "\n매매 대상 : " + self.ticker + "\n시작 현금 : " + str(self.cash))
        atexit.register(self.handle_exit)
        
        while True :
            try :
                now = datetime.datetime.now()
                current_price = pyupbit.get_current_price(self.ticker)
                self.get_today_data()

                if(now.minute != self.minute) :
                    self.minute = now.minute
                    self.cash = self.upbit.get_balance("KRW")
                    self.coin = self.upbit.get_balance(self.ticker)

                    print("=================================================================")
                    print("현재        :", now.strftime("%Y-%m-%d %H:%M:%S"))
                    print("현금 (원)   :", self.cash)
                    print("코인 (원)   :", self.coin * current_price)
                    print("현재가      :", current_price)
                    print("평균구매가  :", self.purchase_avg)
                    print("판매금액    :", self.purchase_avg * self.sell_percent)
                    print("3 돌파계수  :", self.coef3)
                    print("5 돌파계수  :", self.coef5)
                    print("10 돌파계수 :", self.coef10)
                    print("3 이평      :", self.ma3)
                    print("5 이평      :", self.ma5)
                    print("10 이평     :", self.ma10)

                if((self.purchase_avg > 0) and (self.purchase_avg * self.sell_percent <= current_price)) :
                    self.cash = self.upbit.get_balance("KRW")
                    self.coin = self.upbit.get_balance(self.ticker)
                    self.sell_coin()

                if((current_price < self.ma3) and self.cash > 5250) :
                    self.cash = self.upbit.get_balance("KRW")
                    self.coin = self.upbit.get_balance(self.ticker)
                    self.buy_coin()

            except Exception as err:
                self.bot.message("==================== [ ‼️ 오류 발생 ] ====================")
                self.bot.message(err)
                traceback.print_exc()

            time.sleep(1)

    def handle_exit(self):
            now = datetime.datetime.now()
            formatted_time = "{}년 {}월 {}일 {}시 {}분 {}초".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
            self.bot.message("\n🔚 자동 매매를 종료합니다.\n종료 시간 : " + formatted_time)

    def get_today_data(self) :
        daily_data = pyupbit.get_ohlcv(self.ticker, count=10)

        # 3일 평균 돌파계수
        daily_data['mid_avg3'] = (daily_data['high'].rolling(window=3, min_periods=1).mean() + daily_data['low'].rolling(window=3, min_periods=1).mean()) / 2
        daily_data['coef3'] = daily_data['close'] / daily_data['mid_avg3']
        # 5일 평균 돌파계수
        daily_data['mid_avg5'] = (daily_data['high'].rolling(window=5, min_periods=1).mean() + daily_data['low'].rolling(window=5, min_periods=1).mean()) / 2
        daily_data['coef5'] = daily_data['close'] / daily_data['mid_avg5']
        # 10일 평균 돌파계수
        daily_data['mid_avg10'] = (daily_data['high'].rolling(window=10, min_periods=1).mean() + daily_data['low'].rolling(window=10, min_periods=1).mean()) / 2
        daily_data['coef10'] = daily_data['close'] / daily_data['mid_avg10']

        # 3일 이동평균선
        daily_data['ma3'] = daily_data['close'].rolling(window=3, min_periods=1).mean()
        # 5일 이동평균선
        daily_data['ma5'] = daily_data['close'].rolling(window=5, min_periods=1).mean()
        # 10일 이동평균선
        daily_data['ma10'] = daily_data['close'].rolling(window=10, min_periods=1).mean()

        today = daily_data.iloc[-1]
        self.coef3 = today.coef3
        self.coef5 = today.coef5
        self.coef10 = today.coef10
        self.ma3 = today.ma3
        self.ma5 = today.ma5
        self.ma10 = today.ma10

    def buy_coin(self) :
        balance = self.upbit.get_balance("KRW") # 현금 잔고 조회
        
        if balance > 5025 :
            self.upbit.buy_market_order(self.ticker, balance * (1 - self.fee))

            buy_price = pyupbit.get_orderbook(self.ticker)['orderbook_units'][0]['ask_price'] # 최우선 매도 호가
            self.purchase_avg = buy_price
            self.cash = self.upbit.get_balance("KRW")
            self.coin = self.upbit.get_balance(self.ticker)
            print('==================== [ 🪣 매수 시도 ] ====================')
            self.bot.message("#매수 주문\n매수 주문 가격 : " + str(buy_price) + "원")
        else:
            self.bot.message("#매수 실패\n현재 현금 잔고 : " + str(balance) + "원")

    def sell_coin(self) :
        balance = self.upbit.get_balance(self.ticker) # 코인 잔고 조회

        if (balance > 0):
            self.upbit.sell_market_order(self.ticker, balance)
            sell_price = pyupbit.get_orderbook(self.ticker)['orderbook_units'][0]['bid_price'] # 최우선 매수 호가
            self.purchase_avg = 0
            self.cash = self.upbit.get_balance("KRW")
            self.coin = self.upbit.get_balance(self.ticker)
            print('==================== [ 🏏 매도 시도 ] ====================')
            self.bot.message("#매도 주문\n매도 주문 가격 : " + str(sell_price) + "원")
        else :
            self.bot.message("#매도 실패\n현재 코인 잔고 : " + str(balance) + "원")