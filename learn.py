
import pandas as pd

def performance_metric(y_true, y_pred):
	from sklearn.metrics import precision_score, recall_score
	w=0.5
	w = w**2
	p = precision_score(y_true, y_pred, average='micro') 
	r = recall_score(y_true, y_pred, average='micro') 
	f = (1+w)*p*r/(w*p+r)
	return f

def main():
	
	fname = 'data_train.csv'

	data = pd.read_csv(fname, header=0)

	def should_buy(x, threshold):
		if x>threshold:
			return 1
		return 0

	threshold_to_buy = 3
	data['should_buy'] = data['reward'].apply(should_buy, args=(threshold_to_buy, ))

	print "Total number of data points: {}".format(len(data))
	print "Number of data that should trigger buy: {}".format(data[data.should_buy==1].shape[0]) 
	print "Number of data that should not trigger buy: {}".format(data[data.should_buy==0].shape[0])


	# Data is unbalanced
	# how to do CV


	print data.head(5)

	# drop volume, as more than half are missing
	print data['vol_0'].describe()
	data = data.drop(['vol_0', 'vol_1', 'vol_2', 'vol_3'], axis=1)

	# drop date
	data = data.drop(['date'], axis=1)

	# drop reward
	data = data.drop(['reward'], axis=1)

	# drop adj_close
	data = data.drop(['adj_close_0', 'adj_close_1', 'adj_close_2', 'adj_close_3'], axis=1)

	feature_cols = list(data.columns[:-1])
	target_col = data.columns[-1]

	x_all = data[feature_cols]
	y_all = data[target_col]

	print x_all.head()
	print y_all.head()


	from sklearn.cross_validation import StratifiedShuffleSplit
	import numpy as np
	y = np.array([0, 0, 0, 0, 0, 0, 1, 1,1, 1])
	
	sss = StratifiedShuffleSplit(y, n_iter=1, test_size=0.3, random_state=0)
	for train_index, test_index in sss:
		print train_index
		print test_index


	print 'Done!'

if __name__ == "__main__":
	main()
