"""****************************************************************************************************
* Functions that define the connection of the database
* Version: 0
* Date: 18/11/2019
****************************************************************************************************"""
import configparser
from mysql.connector import connect as mySQLConnect
from mysql.connector import Error as mySqlException
from pyodbc import connect as SQLServerConnect
from pyodbc import DatabaseError as sqlServerException

"""****************************************************************************************************
* Description: method to create a conexion to a MySQL database 
* INPUT: -
* OUTPUT: a conexion object to the database
****************************************************************************************************"""
def dbConnectMySQL(user=None,pwd=None):
	try:
		config = configparser.SafeConfigParser()
		config.read('config.ini')
		server = str(config.get('MySQLDatabase','Server'))
		db = str(config.get('MySQLDatabase','Database'))
		if(user is None or pwd is None):
			user = str(config.get('MySQLDatabase','User'))
			pwd = str(config.get('MySQLDatabase','Password'))

		return mySQLConnect(host = server, database = db, user = user, password = pwd)
	except mySQLException as e:
		raise e

"""****************************************************************************************************
* Description: method to create a conexion to the SQL SERVER database 
* INPUT: -
* OUTPUT: a conexion object to the database
****************************************************************************************************"""
def dbConnectSQLServer():
	try:
		config = configparser.SafeConfigParser()
		config.read('config.ini')
		driver = str(config.get('SQLServerDatabase','Driver'))
		server = str(config.get('SQLServerDatabase','Server'))
		db = str(config.get('SQLServerDatabase','Database'))
		user = str(config.get('SQLServerDatabase','User'))
		pwd = str(config.get('SQLServerDatabase','Password'))

		connection = f'driver={driver};server={server};database={db};uid={user};pwd={pwd}'
		conexion = SQLServerConnect(connection)
		return conexion
	except sqlServerException as e:
		raise e
