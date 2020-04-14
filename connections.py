"""****************************************************************************************************
* Functions that define the connection of the database
* Version: 0
* Date: 18/11/2019
****************************************************************************************************"""
import configparser
from mysql.connector import connect as mySQLConnect
from mysql.connector import Error as mySQLException

"""****************************************************************************************************
* Description: method to create a conexion to a MySQL database 
* INPUT: -
* OUTPUT: a conexion object to the database
****************************************************************************************************"""
def dbConnectMySQL(user=None,pwd=None):
	try:
		config = configparser.SafeConfigParser()
		config.read('config.ini')
		server = str(config.get('MySQLDatabase-User','Server'))
		db = str(config.get('MySQLDatabase-User','Database'))
		if(user=='admin'):
			user = str(config.get('MySQLDatabase-Admin','User'))
			pwd = str(config.get('MySQLDatabase-Admin','Password'))
		else:
			user = str(config.get('MySQLDatabase-User','User'))
			pwd = str(config.get('MySQLDatabase-User','Password'))

		return mySQLConnect(host = server, database = db, user = user, password = pwd)
	except mySQLException as e:
		raise e