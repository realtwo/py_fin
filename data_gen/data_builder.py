
import pandas as pd

IDX_DATE = 0
IDX_OPEN = 1
IDX_HIGH = 2
IDX_LOW = 3
IDX_CLOSE = 4

class Data(object):
	def __init__(self, filename):
		self.filename = filename
		self.df = pd.read_csv(filename, header=0)

		self.str_train = "data_train.csv"
		self.str_val = "data_val.csv"
		self.str_test = "data_test.csv"
		self.data_log = open(filename, 'r')  # raw input file
		self.data_train = open(self.str_train,'w')
		self.data_val = open(self.str_val,'w')
		self.data_test = open(self.str_test,"w")
		
		self.days_back = 4
		self.days_hold_max = 20
		self.price_open = 0
		self.price_close = 0
		
		self.stop_loss = 0.1
		
		self.data_count = 0
		
		self.test_data_ratio = 0.0 # ratio of test data / total data

		# trend test: 1: up, -1: down, 0: sideline
		self.trend_days_back = 20 # number of days back to test trend
		self.trend_ratio = 0.6 # ratio to affirm a trend


	def print_rules(self):
		rule = "Sell when stop loss level is hit, \n"
		rule += " or max hold days is reached.\n"
		rule += "Price is based on worst case:\n"
		rule += " buy at highest, and sell at lowest.\n"
		print "------------- RULES -----------------"
		print rule
		print "-------------------------------------"

	def close_data_log(self):
		self.data_log.close()
		self.data_train.close()
		self.data_test.close()
		self.data_val.close()

	def cal_price_open(self, day_idx):
		line = self.data_raw[day_idx].strip().split(',') # day on which to buy
		price_open = int(float(line[IDX_HIGH])) # buy at price high for worst case
		return price_open

	# returns open and close prices
	def cal_price_open_close(self, day_idx):
		# calculate open price
		p_open = self.cal_price_open(day_idx)

		# get all close prices during max hold time window
		price_all = []
		for j in xrange(day_idx, day_idx+self.days_hold_max):
			line = self.data_raw[j].strip().split(',')
			p = int(float(line[IDX_LOW]))  # sell at price low for worst case
			price_all.append(p)

		# now calculate close price
		price_max = 0
		for p_close in price_all:
			if p_close > price_max:
				price_max = p_close
				continue
			if p_close < p_open*(1-self.stop_loss):
				break
			if p_close < price_max*(1-self.stop_loss):
				break
		return (p_open, p_close)


	def cal_reward(self, day_idx):
		# Calculate open and close price
		(p_open, p_close) = self.cal_price_open_close(day_idx)
		# Use % returns as reward
		reward = 100.0*(p_close-p_open)/p_open
		return reward

	def cal_all_ma(self, ma_list):
		df = self.df
		p_close = df.close
		for v in ma_list:
			p_ma = pd.rolling_mean(p_close, window=v, min_periods=1)
			col_name = 'ma_'+str(v)
			df[col_name] = p_ma

		#df.to_csv(self.filename, index=False)
		self.df = df

	def cal_rsi(self, period=14):
		## RSI calculation
		self.df['change'] = self.df['close'] - self.df['close'].shift()

		def get_positive(x):
			if x>0:
				return x
			return 0

		def get_negative(x):
			if x<0:
				return -x
			return 0

		self.df['gain'] = self.df['change'].apply(get_positive)	
		self.df['loss'] = self.df['change'].apply(get_negative)

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


	def _cal_raw_feature(self, day_idx):
		data_feature = []
		for j in range(day_idx-self.days_back, day_idx):
			line = self.data_raw[j].strip().split(',')
			data_feature+=line[1:1+6]  # O/H/L/C/Vol/AdjC
		return [int(float(v)) for v in data_feature]	


	def _get_val_from_df(self, idx, col):
		if isinstance(idx, list):
			v = self.df.ix[idx[0]:idx[1], col]
		else:
			v = self.df.ix[idx, col]
		return v

	# Returns the pattern of the curve with col_name:
	# Divide the data into two halfs and test trend on each half,
	# The trend could be up, down, or side.
	# Then combine the two trends into a single value
	def _cal_feature_curve_pattern(self, day_idx, col_name):

		def find_pattern(data):
			n = len(data)
			cnt_up = 0
			for i in xrange(1, n):
				if data[i]>data[i-1]:
					cnt_up+=1
			cnt_down = n-cnt_up
			
			if cnt_up > n-2:
				return 2
			elif cnt_down > n-2:
				return 1
			else:
				return 0

		idx_end = day_idx-2 #inclusive
		idx_start = idx_end-self.trend_days_back+1
		
		if idx_end < 5: # no point to look at too few data points
			return 0 
		if idx_start<0: #note df index starts with 0
			idx_start = 0

		data = self._get_val_from_df([idx_start,idx_end], col_name).values

		pattern1 = find_pattern(data[0:len(data)/2])
		pattern2 = find_pattern(data[len(data)/2:])

		return pattern1*10+pattern2


	def build_feature(self, day_idx, feat_list):
		
		# baseline features: OCHL, date, reward
		data_feature = self._cal_raw_feature(day_idx)

		for v in feat_list:
			if v == 'ma_5':
				#-1 for prev day, -1 to begin index in df with 0
				p_ma5 = self._get_val_from_df(day_idx-2, v)  
				data_feature.append(p_ma5)
			elif v == 'ma_10':
				p_ma10 = self._get_val_from_df(day_idx-2, v)
				data_feature.append(p_ma10)
			elif v == 'ma_20':
				p_ma20 = self._get_val_from_df(day_idx-2, v)
				data_feature.append(p_ma20)
			elif v == 'ma_60':
				p_ma60 = self._get_val_from_df(day_idx-2, v)
				data_feature.append(p_ma60)
			elif v == 'rsi':
				rsi = self._get_val_from_df(day_idx-2, v)
				data_feature.append(rsi)
			else:
				#print 'Feature: %s: baseline, or unhandled!' %v	
				pass
		return data_feature

	def format_training_single(self, data_reward, data_feature):
		return [data_reward] + data_feature

	def read_all_in_mem(self):
		self.data_raw = self.data_log.readlines()
		print "Done reading %d lines into memory" %len(self.data_raw)
		self.data_count = len(self.data_raw)

	## build data for train, validation and test
	def generate_header(self, hasReward):
		if hasReward:
			line = "date,reward"
		else:
			line = "date"
		for i in xrange(0, self.days_back):
			line2 =",open_"+str(i)+",high_"+str(i)+",low_"+str(i)+",close_"+str(i)
			line += line2
			line2 = ",vol_"+str(i)+",adj_close_"+str(i)
			line += line2
		line += ",ma_5,ma_10,ma_20,ma_60"
		line +=",rsi"

		print line
		return line

	def build_test(self):

		header = self.generate_header(hasReward=False)		

		self.data_test.write(header+'\n')

		## create data for test, without reward
		for i in xrange(self.data_count-self.days_hold_max, self.data_count):
			id_date = self.data_raw[i].strip().split(',')[0]

			#Build feature data
			data_feature = self.build_feature(i, header.split(','))
			
			line = ",".join(str(v) for v in data_feature)
			line = id_date+","+line
			self.data_test.write(line+'\n')
		print "Done writing %d data to test files." %(self.days_hold_max)

	def build_train_val(self):
		header = self.generate_header(hasReward=True)		
		self.data_val.write(header+'\n')
		self.data_train.write(header+'\n')

		# take self.days_back price data as feature
		# calculate return / loss as label
		# i points to current date
		# [i-days_back,... , i-2,i-1] forms pattern
		# max hold date is [i+days_hold_max]
		for i in xrange(self.days_back+1, self.data_count-self.days_hold_max):
		#for i in range(self.days_back, self.days_back+1):
			id_date = self.data_raw[i].strip().split(',')[0]

			# Calculate reward
			data_reward = self.cal_reward(i)
			#print "Return of %d" %reward

			#Build feature data
			data_feature = self.build_feature(i, header.split(','))

			# final training data: label, followed by features
			data_training = self.format_training_single(data_reward, data_feature)
			
			line = ",".join(str(v) for v in data_training)
			line = id_date+","+line

			if i>(1-self.test_data_ratio)*self.data_count:  #Use fixed training size
				self.data_val.write(line+'\n')
			else:
				self.data_train.write(line+'\n')

		print "Done writing %d data to train and validation files." %(i-self.days_back+1)

	def build_all(self):
		
		self.cal_all_ma([5,10,20,60])
		
		self.cal_rsi(period=14)

		## read all data into mem, process by index of the day

		self.read_all_in_mem()
		self.build_train_val()
		self.build_test()

		
	def verify_files(self):
		fp = open(self.str_train)
		for j, l in enumerate(fp):
			pass
		print "Training file contains %d data" %(j+1)
		fp.close()

		fp = open(self.str_val)
		for j, l in enumerate(fp):
			pass
		print "Validation file contains %d data" %(j+1)
		fp.close

		fp = open(self.str_test)
		for j, l in enumerate(fp):
			pass
		print "Test file contains %d data" %(j+1)
		fp.close


def main():
	
	counter = 'STI'
	fname = 'data-' + counter + '.csv'
	symbol = '^'+counter

	# Build training data and save into csv file
	import stock_tracker
	stockData = stock_tracker.YahooStock(fname, symbol)
	stockData.update()

	data = Data(fname)
	
	data.print_rules()

	data.build_all()

	data.close_data_log() # close both raw and training data

	data.verify_files()

	df = pd.read_csv("data_train.csv")
	print df 

if __name__ == "__main__":
	main()
