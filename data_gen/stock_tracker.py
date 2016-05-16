import datetime as dt
import urllib2

class YahooStock (object):
	def __init__(self, filename, symbol):
		self.log_file = filename
		self.symbol = symbol

	def get_price_history(self, sym, from_date, to_date):
		start = from_date.split('-')
		stop = to_date.split('-')
		url = 'http://ichart.yahoo.com/table.csv?s=%s&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv' \
		% (sym, int(start[1])-1, int(start[2]), int(start[0]), int(stop[1])-1, int(stop[2]), int(stop[0])) 

		req = urllib2.Request(url)
		resp = urllib2.urlopen(req)
		content = str(resp.read().decode('utf-8').strip())
		daily_data = content.splitlines()[::-1]
		return daily_data

	def update_data(self):
		
		try:
			fp = open(self.log_file)
			for i, line in enumerate(fp):
				pass
			total = i+1
			last_day = line.split(",")[0].split('-')

			fp.close()
		except IOError as e:
			print "StockTracker: creating new stock data log file"
			total = 0
			# write header to csv
			fp = open(self.log_file,'a')
			fp.write("date,open,high,low,close,vol,adj_close\n")
			fp.close()
			last_day = ['2006','1','1']

		today = dt.date.today()

		last_day = dt.date(int(last_day[0]), int(last_day[1]), int(last_day[2]))
		from_date = last_day + dt.timedelta(days=1) 

		data = self.get_price_history(self.symbol, str(from_date), str(today))

		fp = open(self.log_file,'a')
		for i in range(0, len(data)-1):
			fp.write(data[i]+'\n')
		fp.close()

		print "Stock data updated until %s" %str(today)

	def update(self):
		print "Updating data for " + self.symbol
		try: 
			self.update_data()
		except urllib2.HTTPError:
			print "Already have latest data as of %s." %str(dt.date.today())


def main():
	stockData = YahooStock('data-STI.csv', '^STI')
	stockData.update()

if __name__ == "__main__":
	main()
