
import pandas as pd

def should_buy(x, threshold):
	if x>threshold:
		return 1
	return 0



def format_x_y(fname="data2.csv", threshold_to_buy=1.5):

	data = pd.read_csv(fname, header=0)
	data['should_buy'] = data['reward'].apply(should_buy, args=(threshold_to_buy, ))

	# drop reward
	data = data.drop(['reward'], axis=1)

	feature_cols = list(data.columns[:-1])
	target_col = data.columns[-1]

	x_all = data[feature_cols]
	y_all = data[target_col]

	return x_all, y_all

def print_stats(x_all, y_all):
	print "Total number of data points: {}".format(x_all.shape[0])
	print "Total number of featuers: {}".format(x_all.shape[1])
	print "Features: {}".format(x_all.columns.values)
	print "Number of data that should trigger buy: {}".format(y_all[y_all==1].shape[0]) 
	print "Number of data that should trigger buy: {}".format(y_all[y_all==0].shape[0]) 	

def main():
	

	x_all, y_all = format_x_y()


	print x_all
	print y_all

	print_stats(x_all, y_all)

	print 'Done!'

if __name__ == "__main__":
	main()
