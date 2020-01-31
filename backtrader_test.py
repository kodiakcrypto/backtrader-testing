from datetime import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers
import pandas as pd
from random import choice

#define strat
class Strategy(bt.Strategy):
    def __init__(self):
        self.ema100 = bt.ind.EMA(self.data.close, period=100)
        # self.ema50 = bt.ind.EMA(self.data.close, period=50)
        self.ema34 = bt.ind.EMA(self.data.close, period=34)
        self.ema14 = bt.ind.EMA(self.data.close, period=14)

        self.EMAcrossUp = bt.ind.CrossUp(self.ema14, self.ema34)
        self.EMAcrossDown = bt.ind.CrossDown(self.ema14, self.ema34)

        # ICHIMOKU Example
        #self.ichi = bt.ind.Ichimoku(self.data)
        #self.tenkan = self.ichi.tenkan_sen
        #self.kijun = self.ichi.kijun_sen
        #Kijun cross above Tenkan => KTcrossUp == True
        #self.KTcrossUp = bt.ind.CrossUp(self.tenkan, self.kijun)
        #self.KTcrossDown = bt.ind.CrossDown(self.tenkan, self.kijun)
        #senkou_a under _b is green cloud, vice versa is red


        # PIVOTS Example
        # self.pivots = bt.ind.PivotPoint(self.data)
        # self.pivots.pivot 
        # self.pivots.r1 
        # self.pivots.r2 
        # self.pivots.s1 
        # self.pivots.s2

        # MACD Example
        # self.macd = bt.ind.MACD(self.data.close) 
        # self.macd_fast = self.macd.macd_signal
        # self.macd_slow = self.macd.macd

        # ATR Example
        # self.atr = bt.ind.AverageTrueRange(self.data.close)

        # Fib Pivots Example
        # self.Fpivots = bt.ind.FibonacciPivotPoint(self.data)
        # self.Fpivots.pivot .s1 .s2 .s3 .r1 .r2 .r3

        # CCI Example
        # self.cci = bt.ind.CommodityChannelIndex(self.data.close)

    #Backtrader runs this code on every candle
    def next(self):
        if self.position.size == 0:
            if self.EMAcrossUp:
                #check if the close price > the 100 EMA 
                #AND that the 100 EMA has been ascending for 2 candles (an uptrend)
                if self.data.close > self.ema100 and self.ema100[0] > self.ema100[-1] and self.ema100[-1] > self.ema100[-2]:
                    self.buy() #size=n makes it fail
                    pass
                elif self.EMAcrossDown:
                    if self.data.close < self.ema100 and self.ema100[0] < self.ema100[-1] and self.ema100[-1] < self.ema100[-2]:
                        self.sell() 
                        pass
        else:
            if self.position.size != 0: #if we have a position
                if self.position.size > 0 and self.EMAcrossDown or self.position.size < 0 and self.EMAcrossUp:
                    self.close()
                    pass

#idea: try skipping next signal if previous worked


#init strategy & cerebro instance
cerebro = bt.Cerebro()
cerebro.addstrategy(Strategy)

cerebro.broker.set_cash(10000000)
cerebro.broker.setcommission(commission=0.1)

#load 1 hour interval bitmex data
d = pd.read_csv('XBTUSD-ALL-TIME-1h.csv') 

#load 1 day interval bitmex data
#d = pd.read_csv('XBTUSD-ALL-TIME-1d.csv') 

#fill NaN values with 0's
d.fillna(0) 
#convert unix time to datetime objects
d['datetime'] = pd.to_datetime(d['datetime'].astype(int), unit='s') 

#drop all the indicator columns we dont need
data = d.drop(columns=['ema-50','tema-50','dema-50','zlema-50','hma-50','macd','rsi-14',
                       'stochrsi-14','cci-20','mfi-14','mass-10','mom-10','sma-50','vwma-50',
                       'wma-50','kama-50','trima-50','bbands-sma-20-2','atr-14','ultosc-7-14-28','obv','ao'])

#if data = 1 hour data, then you can consolidate it to a 3h interval with this command
#data = data.resample('3H').ohlc()

#initialize backtrader 'datafeed' via pandas dataframe
data_feed = btfeeds.PandasData(
    dataname=data,
    datetime=-1,
    open=-1,
    high=-1,
    low=-1,
    close=-1,
    volume=-1,
    openinterest=None
)
cerebro.adddata(data_feed)

# quandl is useful for getting stock data
# import quandl
# quandl_data = quandl_data.reset_index()
# quandl_data.drop(columns=["Bid", "Ask", "VWAP"], inplace=True)
# quandl_data.rename(columns={"Date":"datetime", "High":"high","Low":"low","Last":"close", "Volume":"volume"})
# quandl_data["open"] = quandl_data['close'].shift(-1)
# print(quandl_data)

# Analyzers
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe_ratio')
cerebro.addanalyzer(btanalyzers.DrawDown, _name='draw_down')
cerebro.addanalyzer(btanalyzers.PeriodStats, _name='general_stats') #compression=60, timeframe=Timeframe.Minutes
#cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='ta')
#cerebro.addanalyzer(btanalyzers.Calmar, _name='calmar_ratio')
#cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
#cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
#cerebro.addanalyzer(btanalyzers.VWR, _name='vwr')


print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

strats = cerebro.run()
strat = strats[0]

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

print('Sharpe Ratio:', strat.analyzers.sharpe_ratio.get_analysis())
print('Drawdown:')
strat.analyzers.draw_down.pprint()
print('Stats:')
thestrat.analyzers.general_stats.pprint()

# print('Calmar Ratio:', strat.analyzers.calmar_ratio.get_analysis())
# print('Trade anal:')
# thestrat.analyzers.ta.pprint()
# print('Returns:')
# thestrat.analyzers.returns.pprint()
# print('SQN:')
# thestrat.analyzers.sqn.pprint()
# print('VWR:')
# thestrat.analyzers.vwr.pprint()

cerebro.plot(style='bar') 
#lcolors=['green','red','black','orange'], style='candle')