import os


class Config(object):

	SECRET_KEY = 'my_secret_key'


class DevelopmentConfig(Config):

	DEBUG = True
	SERVER_NAME = 'localhost:8000'
	SQLALCHEMY_DATABASE_URI = 'mysql://root:Rocky1995#@localhost/crafts_test'
	SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):

	DEBUG = False
	SERVER_NAME = 'localhost:5000'
	SQLALCHEMY_DATABASE_URI = 'mysql://root:Rocky1995#@localhost/crafts'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
