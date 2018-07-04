import pandas as pd
import glob
import sqlite3

to_drop = ['Details', 'Type', 'Check or Slip #']
word_drop = {' IL':'', ' AURORA':'', ' LISLE':'', ' WOODRIDGE':'',
			 ' WHEATON':'', ' WESTMONT':'', ' LOMBARD':'', ' BLOOMINGDALE':'',
			 ' DOWNERS GROVE':'', ' NAPERVILLE':'', ' CHICAGO':''}

class Data():
	def __init__(self):
		self.filePath = 'C:\\Users\\micha\\Budget\\Bank Data\\'
		Data.get_data(self)
	
	# Retrieve data from saved bank csv files
	def get_data(self):
		self.data = pd.DataFrame()
		files = []
		csvs = []
		try:
			for item in glob.glob(self.filePath+'/*.csv'):
				csvs.append(item)
				with open(item, 'r') as file:
					sheet = pd.read_csv(file, index_col=False)
					files.append(sheet)
			self.data = pd.concat(files)
			print(csvs)
			return self.clean_Data()
		except:
			return None

	def clean_Data(self):
		self.data = self.data.rename(columns={'Posting Date':'postDate'})
		self.data['postDate'] = pd.to_datetime(self.data.postDate)
		self.data = self.data.sort_values(by='postDate')
		self.data['Index'] = range(self.data.shape[0])
		self.data = self.data.set_index('Index')
		self.data.drop(columns=to_drop, inplace=True)
		self.data['Description'] = self.data['Description'].str.upper()
		self.data['Description'] = self.data['Description'].str.translate(str.maketrans(dict.fromkeys('0123456789/#-')))
		self.data['Description'] = self.data['Description'].str.split(r'\s{2,}')
		self.data['Description'] = self.data.apply(lambda x: pd.Series(x['Description'][0]),axis=1)
		for i,j in word_drop.items():
			self.data['Description'] = self.data['Description'].str.replace(i,j)
		return self.data

class DataBase():

	def __init__(self):
		self.conn = sqlite3.connect('BankInfo.db')
		self.cur = self.conn.cursor()
		self.cur.execute('''CREATE TABLE IF NOT EXISTS bankStatement 
						(ind INTEGER PRIMARY KEY,postDate DATE,description TEXT,amount FLOAT,balance FLOAT)''')
		self.cur.execute('''CREATE TABLE IF NOT EXISTS existStatement
						(statement TEXT)''')
		self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS index_key on bankStatement(ind)''')
		self.conn.commit()
		self.data = Data().data
		#print(self.data)
		if len(self.data) > 0:
			self.insert_Data()
		#self.pull_Data()

	def insert_Data(self):
		self.data.to_sql('bankStatement',con=self.conn, if_exists='append', index=False)
		self.conn.commit()
		print('Data inserted into the database')

	def pull_Data(self):
		self.data = pd.read_sql('SELECT * FROM bankStatement',con=self.conn)
		#self.data = pd.read_sql('SELECT * FROM existStatement',con=self.conn)
		print(self.data)

	def __del__(self):
		self.conn.close()


if __name__ == '__main__':
	db = DataBase()
