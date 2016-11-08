import logging

class Config():

	database = None

	def __init__(self, database):
		self.database = database


	def get_config(self):

		configs = []

		for rs in self.database.execute('SELECT * FROM config WHERE 1', None):
			config = {}

			config['config_id'] = rs[0]
			config['config'] = rs[1]
			config['value_type'] = rs[2]
			config['value'] = rs[3]
			config['label'] = rs[4]
			config['description'] = rs[5]

			configs.append(config)

		return configs

	def get_config_by_id(self, id):

		for rs in self.database.execute('SELECT * FROM config WHERE config_id=?', [id]):
			config = {}

			config['config_id'] = rs[0]
			config['config'] = rs[1]
			config['value_type'] = rs[2]
			config['value'] = rs[3]
			config['label'] = rs[4]
			config['description'] = rs[5]

			return config

	def get_config_by_config(self, config):

		for rs in self.database.execute('SELECT * FROM config WHERE config=?', [config]):
			config = {}

			config['config_id'] = rs[0]
			config['config'] = rs[1]
			config['value_type'] = rs[2]
			config['value'] = rs[3]
			config['label'] = rs[4]
			config['description'] = rs[5]

			return config

	def set_config(self, config_id, value):
		self.database.execute('UPDATE config SET `value`=? WHERE `config_id`=?', [value, config_id])


