
import pandas as pd
from data_gen import stock_tracker 

import matplotlib.pyplot as plt

class DataWeekly(object):
	def __init__(self, filename):
		self.filename = filename
		self.df = pd.read_csv(filename, header=0)
	
		self.days_back = 4
		self.days_hold_max = 5
		
		self.data_count = 0
		

	def print_rules(self):
		rule = "Sell when max hold day is reached, \n"
		rule += "Price is based on closing \n"
		print "------------- RULES -----------------"
		print rule
		print "-------------------------------------"

	def cal_return(self, day_shift, col_name):
		tmp = self.df['adj_close'] - self.df['adj_close'].shift(day_shift)
		self.df[col_name] = 100.0*tmp/self.df['adj_close'].shift(day_shift)

	def cal_reward(self):
		col_name = 'reward'
		day_shift = 4
		self.cal_return(day_shift = day_shift, col_name=col_name)
		self.df[col_name] = self.df[col_name].shift(-day_shift)

	def cal_rsi(self, period=10):
		## RSI calculation
		self.df['change'] = self.df['adj_close'] - self.df['adj_close'].shift()
		print self.df

		def get_positive(x):
			if x>0:
				return x
			return 0

		def get_negative(x):
			if x<0:
				return -x
			return 0

		self.df['gain'] = self.df.change.apply(get_positive)	
		self.df['loss'] = self.df.change.apply(get_negative)

		def cal_weighted_avg(df, colname, p=period):
			colout = 'avg_'+colname
			for i in xrange(0, df.shape[0]):
				if i<p:
					series = df.ix[0:i, colname]
					df.ix[i, colout] = series.mean()
				else:
					df.ix[i, colout] = ((p-1)*df.ix[i-1, colout] + df.ix[i, colname])/p
				#print series
				
			return df

		self.df = cal_weighted_avg(df = self.df, colname = 'gain', p=period)
		self.df = cal_weighted_avg(df = self.df, colname = 'loss', p=period)
		for i in xrange(0, self.df.shape[0]):
			g = self.df.ix[i, 'avg_gain']
			l = self.df.ix[i, 'avg_loss']
			if l == 0:
				if g == 0:
					rsi = 50
				else:
					rsi = 100
			else:
				rsi = 100 - 100/(1+g/l)
			self.df.ix[i, 'rsi'] = rsi
		self.df = self.df.drop(['change', 'gain', 'loss', 'avg_gain', 'avg_loss'], axis=1)

		plt.plot(self.df.adj_close)
		plt.plot(10*self.df.rsi+2000)
		plt.show()

	def build_features_price(self):
		for col_base in ['open', 'high', 'low', 'close']:
			for i in xrange(1,4):
				col_name = col_base+ '_' + str(i)	
				self.df[col_name] = self.df[col_base].shift(i)

	def build_features_and_labels(self):
		self.cal_reward()

		self.build_features_price()

		self.cal_rsi(period=10)

		self.df.dropna(inplace=True)

		print self.df

		self.labels = self.df['reward']

		self.features = self.df.drop(['date', 'adj_close', 'vol', 'reward'], axis=1)

	def export(self, fname = "data.csv"):
		tmp = pd.concat([self.labels, self.features], axis=1)
		tmp.to_csv(fname, index=False)

def main():
	
	counter = 'STI'
	fname = 'data-' + counter + '.csv'
	symbol = '^'+counter

	# Build training data and save into csv file
	#stockData = stock_tracker.YahooStock(fname, symbol)
	#stockData.update()

	data = DataWeekly(fname)
	
	data.build_features_and_labels()

	#print data.features
	#print data.labels

	data.export("data2.csv")
	print "Done!"
	

if __name__ == "__main__":
	main()
