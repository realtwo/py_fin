
import pandas as pd

def main():
	
	fname = 'data_train.csv'

	data = pd.read_csv(fname, header=0)

	def should_buy(x, threshold):
		if x>threshold:
			return 1
		return 0

	data['should_buy'] = data['reward'].apply(should_buy, args=(3, ))

	print "Total number of data points: {}".format(len(data))
	print "Number of data that should trigger buy: {}".format(data[data.should_buy==1].shape[0]) 
	print "Number of data that should not trigger buy: {}".format(data[data.should_buy==0].shape[0])

	print 'Done!'

if __name__ == "__main__":
	main()
