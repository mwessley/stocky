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
	
	def get_all(self,short=5,long=10):
		for s in self.symbols:
			self.analyze_stock(s,short,long)

	def get_stock(self, name = 'AAPL'):
		if name in self.stocks.keys():
			print(name, "in keys")
			return self.stocks[name]['stock'], None
		today = datetime.datetime.now()
		print(today.day, today.month, today.year)
		aapl = pdr.get_data_yahoo(name, 
					start=datetime.datetime(today.year, today.month-4, today.day), 
					end=datetime.datetime(today.year, today.month, today.day))
		conv = pdr.get_data_yahoo('EURUSD=X', 
					start=datetime.datetime(today.year, today.month-4, today.day), 
					end=datetime.datetime(today.year, today.month, today.day))
		aapl = aapl
		print(aapl)
		# Plot the closing prices for `aapl`
		#aapl['Close'].plot(grid=True)
		adj_close_px = aapl['Adj Close']/conv['Adj Close']

		# Calculate the moving average
		moving_avg = adj_close_px.rolling(window=12).mean()
		# Inspect the result
		#print(moving_avg[-10:])
		# Short moving window rolling mean
		aapl['12'] = adj_close_px.rolling(window=12).mean()
		# Long moving window rolling mean
		aapl['32'] = adj_close_px.rolling(window=32).mean()
		# Plot the adjusted closing price, the short and long windows of rolling means
		#aapl[['Adj Close', '12', '32']].plot()

		self.stocks[name] = {'stock': aapl}

		# Show plot
		#plt.show()
		#plt.show()
		return aapl, conv

	def analyze_stock(self, name = 'AAPL',short=5,long=12):

		aapl, conv = self.get_stock(name)

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
		signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=2.)

		# Plot the buy signals
		ax1.plot(signals.loc[signals.positions == 1.0].index, 
			signals.mark[signals.positions == 1.0],
			'^', markersize=5, color='b')
			
		# Plot the sell signals
		ax1.plot(signals.loc[signals.positions == -1.0].index, 
			signals.mark[signals.positions == -1.0],
			'x', markersize=5, color='g')
			
		# Show the plot
		print(name)
		plt.show()

		signals['12'] = aapl['Close'].ewm(span=12, adjust=False).mean()
		signals['26'] = aapl['Close'].ewm(span=26, adjust=False).mean()
		macd = signals['12']-signals['26']
		macd9 = macd.ewm(span=9, adjust=False).mean()
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
		signals[['12', '26']].plot(ax=ax1, lw=2.)
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
		return {'sig':signals, 'stock':aapl}

# %%
symbols = ['ADSK','AAPL','MSFT','ADBE','ICLN','TTWO','IFNNY','LSCC','AMD','VBK.DE','STM']
stocks = {}
#for s in symbols:
#	stocks[s] = analyze_stock(s, 4, 8)
#for s in symbols:
#	stocks[s] = analyze_stock(s, 4, 8)

stocky = Stocker(symbols)


# %%
stocky.symbols = ['ADSK','AAPL','MSFT','ADBE', \
	'ICLN','TTWO','IFNNY','LSCC','AMD', \
	'VBK.DE','STM','NXPI', 'ADI', 'VWSYF', 'MDB']
stocky.get_all(4,15)
# %%
stocky.stocks['IFNNY']
# %%
# VBK Verbio
# VWSYF Vestas
# ADI Analog Devices
# 
stocky.names = {
	'ADSK': 'Autodesk',
	'AAPL': 'Apple',
	'MDB': 'MongoDB'
	} 
