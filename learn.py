
import pandas as pd
import preprocess as pp

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
	
	x_all, y_all = pp.format_x_y()


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
