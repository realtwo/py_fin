
import pandas as pd

IDX_DATE = 0
IDX_OPEN = 1
IDX_HIGH = 2
IDX_LOW = 3
IDX_CLOSE = 4


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

	def build_features_price(self):
		for col_base in ['open', 'high', 'low', 'close']:
			for i in xrange(1,4):
				col_name = col_base+ '_' + str(i)	
				self.df[col_name] = self.df[col_base].shift(i)

	def build_features_and_labels(self):
		self.cal_reward()

		self.build_features_price()

		self.df.dropna(inplace=True)

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
	import stock_tracker
	stockData = stock_tracker.YahooStock(fname, symbol)
	stockData.update()

	data = DataWeekly(fname)
	
	data.build_features_and_labels()

	print data.features
	print data.labels

	data.export("data2.csv")
	print "Done!"
	

if __name__ == "__main__":
	main()
