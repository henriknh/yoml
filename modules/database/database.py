import sqlite3, logging, threading, os
from shutil import copyfile



class Database():

	def __init__(self, dataDir):

		self.dataDir = dataDir

		if not os.path.exists(dataDir):
			os.makedirs(dataDir)
		if not os.path.exists(dataDir + '/media.db'):
			copyfile('db', dataDir + '/media.db')

		self.con = sqlite3.connect(self.dataDir + '/media.db', check_same_thread=False)
		#self.c = self.con.cursor()

		self.lock = threading.Lock()
		logging.info("Database created if it didnt exist")

	def execute(self, sql, data):

		#lock.acquire()
		'''
		con = None

		try:

			con = sqlite3.connect(self.dataDir + '/media.db')
			c = con.cursor()

			logging.debug("Database executed %s with data %s" % (sql, str(data)))


			retval = ''
			if data == None:
				retval = c.execute(sql)
			else:
				newdata = []
				for d in data:
					newdata.append(unicode(d))
				retval = c.execute(sql, newdata)

			con.commit()



		finally:
			if con:
				con.close()
			#lock.release()
		'''
		self.lock.acquire()
		try:
			#con = sqlite3.connect(self.dataDir + '/media.db', check_same_thread=False)

			with self.con:
				cur = self.con.cursor()

				retval = ''
				if data == None:
					retval = cur.execute(sql)
				else:
					newdata = []
					for d in data:
						newdata.append(unicode(d))
					retval = cur.execute(unicode(sql), newdata)
		finally:
			self.lock.release()
		return retval

	def close(self):
		#self.con.close()
		return