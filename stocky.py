# %%
import pandas_datareader as pdr
import datetime 
# Import Matplotlib's `pyplot` module as `plt`
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime

class Stocker():
	def __init__(self, symbols = []):
		self.symbols = symbols
		self.stocks = {} 
	
	def get_all(self,short=5,long=10,mean=9):
		for s in self.symbols:
			self.analyze_stock(s,short,long,mean)

	def get_stock(self, name = 'AAPL'):
		if name in self.stocks.keys():
			print(name, "in keys")
			return self.stocks[name]['stock'], None
		today = datetime.datetime.now()
		print(name)
		print(today.day, today.month, today.year)
		try:
			aapl = pdr.get_data_yahoo(name, 
						start=datetime.datetime(today.year-1, today.month+7, today.day), 
						end=datetime.datetime(today.year, today.month, today.day))
			conv = pdr.get_data_yahoo('EURUSD=X', 
						start=datetime.datetime(today.year-1, today.month+7, today.day), 
						end=datetime.datetime(today.year, today.month, today.day))
		except Exception as e:
			print(e)
			return None, None
		aapl = aapl
		print(aapl)
		# Plot the closing prices for `aapl`
		#aapl['Close'].plot(grid=True)
		adj_close_px = aapl['Adj Close']/conv['Adj Close']

		# Calculate the moving average
		#moving_avg = adj_close_px.rolling(window=12).mean()
		print(aapl.columns)
		#print(moving_avg)
		# Inspect the result
		#print(moving_avg[-10:])
		print("lol")
		# Short moving window rolling mean
		a13 = adj_close_px.rolling(window=13).mean()
		aapl['13'] = a13
		# Long moving window rolling mean
		a32 = adj_close_px.rolling(window=32).mean()
		aapl['32'] = a32
		# Plot the adjusted closing price, the short and long windows of rolling means
		#aapl[['Adj Close', '12', '32']].plot()

		self.stocks[name] = {'stock': aapl}

		# Show plot
		#plt.show()
		#plt.show()
		return aapl, conv

	def analyze_stock(self, name = 'AAPL',short=5,long=12,mean=9):

		aapl, conv = self.get_stock(name)
		if aapl is None:
			print("could not get Stock %s", name)
			return

		# Initialize the short and long windows
		short_window = short
		long_window = long 

		# Initialize the `signals` DataFrame with the `signal` column
		signals = pd.DataFrame(index=aapl.index)
		signals['signal'] = 0.0

		# Create short simple moving average over the short window
		signals['short_mavg'] = aapl['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
		signals['short_mavg'] = aapl['Close'].ewm(span=short_window, adjust=False).mean()

		# Create long simple moving average over the long window
		signals['long_mavg'] = aapl['Close'].rolling(window=long_window, min_periods=1, center=False).mean()
		signals['long_mavg'] = aapl['Close'].ewm(span=long_window, adjust=False).mean()
		signals['longest_mavg'] = aapl['Close'].ewm(span=20, adjust=False).mean()
		signals['mark'] = aapl['Close'].rolling(window=1, min_periods=1, center=False).mean()

		# Create signals
		signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] 
							> signals['long_mavg'][short_window:], 1.0, 0.0)   

		# Generate trading orders
		signals['positions'] = signals['signal'].diff()


		# Initialize the plot figure
		fig = plt.figure(figsize=(8, 6), dpi=80)
		plt.title(name+' s'+str(short)+' l'+str(long))

		# Add a subplot and label for y-axis
		ax1 = fig.add_subplot(111,  ylabel='Price in $')

		# Plot the closing price
		aapl['Close'].plot(ax=ax1, color='r', lw=2.)

		# Plot the short and long moving averages
		signals[['short_mavg', 'long_mavg', 'longest_mavg']].plot(ax=ax1, lw=2.)

		# Plot the buy signals
		ax1.plot(signals.loc[signals['positions'] == 1.0].index, 
			signals.mark[signals['positions'] == 1.0],
			'^', markersize=5, color='b')
			
		# Plot the sell signals
		ax1.plot(signals.loc[signals.positions == -1.0].index, 
			signals.mark[signals.positions == -1.0],
			'x', markersize=5, color='g')
			
		# Show the plot
		print(name)
		plt.show()

		signals['12'] = aapl['Close'].ewm(span=short, adjust=False).mean()
		signals['26'] = aapl['Close'].ewm(span=long, adjust=False).mean()
		signals['20'] = aapl['Close'].ewm(span=20, adjust=False).mean()
		macd = signals['12']-signals['26']
		macd9 = macd.ewm(span=mean, adjust=False).mean()
		signals['macd'] = .0
		signals['macd9'] = 0.0
		signals['signal2'] = 0.0
		signals['signal2'][short_window:] = np.where(macd[short_window:] 
							> macd9[short_window:], 1.0, 0.0)   

		# Generate trading orders
		signals['positions2'] = signals['signal2'].diff()
		fig = plt.figure(figsize=(8, 6), dpi=80)
		plt.title(name+'macd')

		# Add a subplot and label for y-axis
		ax1 = fig.add_subplot(111,  ylabel='Price in $')
		# Plot the buy signals
		signals[['12', '26', '20']].plot(ax=ax1, lw=2.)
		aapl['Close'].plot(ax=ax1, color='r', lw=2.)
		ax1.plot(signals.loc[signals.positions2 == 1.0].index, 
			signals.mark[signals.positions2 == 1.0],
			'^', markersize=5, color='b')
			
		# Plot the sell signals
		ax1.plot(signals.loc[signals.positions2 == -1.0].index, 
			signals.mark[signals.positions2 == -1.0],
			'x', markersize=5, color='g')
		plt.show()

		print(signals.tail(10))
		self.stocks[name]['signal'] = signals
		return {'sig':signals, 'stock':aapl}

# %%
symbols = ['ADSK','AAPL','MSFT','ADBE','ICLN','TTWO','IFNNY','LSCC','AMD','VBK.DE','STM']
stocks = {}
stocky = Stocker(symbols)


# %%
stocky.symbols = ['AAPL','MSFT','ADBE', \
	'ICLN','TTWO','IFNNY','LSCC','AMD', \
	'VBK.DE','STM', 'NXPI', 'ADI', 'VWSYF', \
	'GOOGL','ACC.OL','FCEL','BNTX','BLDP','DEZ.DE', \
	'NEL.OL', 'TXN', 'TSLA', 'NVDA', 'MDB', '2PP.DE']
stocky.get_all(short=4,long=8,mean=8)
# %%
stocky.stocks['IFNNY']['stock']['Close']
# %%

stocky.get_stock('AAPL')
# %%
