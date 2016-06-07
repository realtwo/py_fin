
import pandas as pd
from sklearn.metrics import precision_score, recall_score

def performance_metric(y_true, y_pred):
	w=0.5
	w = w**2
	p = precision_score(y_true, y_pred, average='micro') 
	r = recall_score(y_true, y_pred, average='micro') 
	f = (1+w)*p*r/(w*p+r)
	return f

def fit_and_predict(clf, x_train, y_train, x_test):
	clf.fit(x_train, y_train)
	y_pred = clf.predict(x_test)
	return y_pred

def evaluate_model(clf, x_train, y_train, x_test, y_test):

	y_pred = fit_and_predict(clf, x_train, y_train, x_test)
		
	print '----------------------'
	print clf 
	print "precision: {}".format(precision_score(y_test, y_pred))
	print "recall: {}".format(recall_score(y_test, y_pred))
	print "F-score: {}".format(performance_metric(y_true=y_test, y_pred=y_pred))

def main():
	
	fname = 'data_train.csv'

	data = pd.read_csv(fname, header=0)

	def should_buy(x, threshold):
		if x>threshold:
			return 1
		return 0

	threshold_to_buy = 3
	data['should_buy'] = data['reward'].apply(should_buy, args=(threshold_to_buy, ))
	
	# Data is unbalanced
	print "Total number of data points: {}".format(len(data))
	print "Number of data that should trigger buy: {}".format(data[data.should_buy==1].shape[0]) 
	print "Number of data that should not trigger buy: {}".format(data[data.should_buy==0].shape[0])

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

	feat_p = [  'open_0', 'high_0', 'low_0', 'close_0',
				'open_1', 'high_1', 'low_1', 'close_1', 
				'open_2', 'high_2', 'low_2', 'close_2', 
				'open_3', 'high_3', 'low_3', 'close_3',
				'ma_5', 'ma_10', 'ma_20', 'ma_60']
	x_all[feat_p] = x_all[feat_p].sub(x_all['open_0'], axis=0)


	x_all = x_all.drop(['open_0'], axis=1)
	#x_all = x_all.drop(['rsi'], axis=1)

	print x_all


	from sklearn.cross_validation import StratifiedShuffleSplit
	sss = StratifiedShuffleSplit(y_all, n_iter=5, test_size=0.3, random_state=0)
	for train_index, test_index in sss:
		x_train = x_all.iloc[train_index]
		y_train = y_all.iloc[train_index]
		x_test = x_all.iloc[test_index]
		y_test = y_all.iloc[test_index]

		from sklearn.ensemble import AdaBoostClassifier
		clf = AdaBoostClassifier()
		evaluate_model(clf, x_train, y_train, x_test, y_test)

		#from sklearn.linear_model import LogisticRegression
		#clf = LogisticRegression()
		#evaluate_model(clf, x_train, y_train, x_test, y_test)

		#from sklearn.ensemble import RandomForestClassifier
		#clf = RandomForestClassifier()
		#evaluate_model(clf, x_train, y_train, x_test, y_test)

		#from sklearn.neural_network import MLPClassifier
		#clf = MLPClassifier()		
		#evaluate_model(clf, x_train, y_train, x_test, y_test)

		print '============================================='
	print 'Done!'

if __name__ == "__main__":
	main()
