
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

	
def main():
	
	counter = 'STI'
	fname = 'data-' + counter + '.csv'
	symbol = '^'+counter

	# Build training data and save into csv file
	import stock_tracker
	stockData = stock_tracker.YahooStock(fname, symbol)
	stockData.update()

	data = DataWeekly(fname)
	
	data.print_rules()
	

if __name__ == "__main__":
	main()
