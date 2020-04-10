"""****************************************************************************************************
* REST API to make predictions over customer data
* Version: 0
* Date: 30/10/2019
****************************************************************************************************"""

from flask import Flask, request, abort
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import connections as cn
import churnFunctions
import json
import re

app = Flask(__name__)
api = Api(app, prefix="/v1")
auth = HTTPBasicAuth()


"""****************************************************************************************************
* Description: basic authentication implementation
* INUT: username and password
* OUTPUT: true if the users has api access
****************************************************************************************************"""

@auth.verify_password
def verify(username, password):
	verified = False
	if not (username and password):
		return verified
	else:
		conexion = None
		try:
			conexion = cn.dbConnectMySQL()
			mycursor = conexion.cursor()
			mycursor.execute("SELECT password FROM users WHERE username =" + "\'" + username + "\'")
			_password = mycursor.fetchone()

			mycursor.close()

			verified = (not (_password is None) and check_password_hash( _password[0],password))

		except cn.mySqlException as e:
			raise e
		finally:
			try:
				if conexion is not None:
					conexion.close()
			except cn.mySqlException as eCon:
				raise eCon
		return verified

"""****************************************************************************************************
* Description: method check the credentials
* INPUT: -
* OUTPUT: -
****************************************************************************************************"""
class ping(Resource):
	#Authentication
	@auth.login_required

	def get(self):
		pass


"""****************************************************************************************************
* Description: method to return a list of customers sensitive to leave the company in the next year
* INPUT: -
* OUTPUT: json object with a list of customers sensitive who might leave.
****************************************************************************************************"""
class customersChurnList(Resource):
	#Authentication
	@auth.login_required

	def get(self):
		#Select in the database to get the info for the customers database

		con = None
		try:
			con = cn.dbConnectSQLServer()

			#Return the JSON created in the churn function
			return churnFunctions.customersChurnList(con)

		except cn.sqlServerException as e:
			app.logger.exception('SQLServer Exception',e)
			abort(500)
		except cn.mySqlException as err:
			app.logger.exception('mySQL Exception',err)
			abort(500)
		finally:
			try:
				if(con is not None):
					con.close()
			except cn.sqlServerException as e2:
				app.logger.exception('Unable to close connection',e2)


"""****************************************************************************************************
* Description: method to return a churn prediction for one customer
* INPUT: customer id
* OUTPUT: a JSON with churn: [0,1] and score percentage of the prediction
****************************************************************************************************"""
class getCustomerChurn(Resource):
	#Authentication
	@auth.login_required

	def get(self,customer_id):
		#Select in the database the info for the selected customer

		con = None
		try:

			#Check if customer_id is an int
			customer_id = int(customer_id)
			con = cn.dbConnectSQLServer()

			#Check if the customer is in the database
			if churnFunctions.isCustomerActive(con,customer_id):
				#Return the JSON with the required data
				return churnFunctions.getCustomerChurn(con,customer_id)
			else:
				abort(400)

		except ValueError as ve:
			abort(400)
		except cn.sqlServerException as e:
			app.logger.exception('SQLServer Exception',e)
			abort(500)
		except cn.mySqlException as err:
			app.logger.exception('mySQL Exception',err)
			abort(500)
		finally:
			try:
				if(con is not None):
					con.close()
			except cn.sqlServerException as e2:
				app.logger.exception('Unable to close the connection', e2)

"""****************************************************************************************************
* Description: method to return the current values of a client in the database
* INPUT: customer id
* OUTPUT: a JSON with the data client
****************************************************************************************************"""
class getCustomerData(Resource):
	#Authentication
	@auth.login_required

	def get(self,customer_id):

		con = None
		try:

			#Check if customer_id is an int
			customer_id = int(customer_id)
			con = cn.dbConnectSQLServer()

			#Check if the customer is in the database
			if churnFunctions.isCustomerActive(con,customer_id):
				#Return the JSON with the required data
				return churnFunctions.getCustomerData(con,customer_id)
			else:
				abort(400)

		except ValueError as ve:
			abort(400)
		except cn.sqlServerException as e:
			app.logger.exception('SQLServer Exception',e)
			abort(500)
		except cn.mySqlException as err:
			app.logger.exception('mySQL Exception',err)
			abort(500)
		finally:
			try:
				if(con is not None):
					con.close()
			except cn.sqlServerException as e2:
				app.logger.exception('Unable to close the connection', e2)

"""****************************************************************************************************
* Description: method to return the current servs of a client in the database
* INPUT: customer id
* OUTPUT: a JSON with the servs of the client
****************************************************************************************************"""
class getCustomerServs(Resource):
	#Authentication
	@auth.login_required

	def get(self,customer_id):

		con = None
		try:

			#Check if customer_id is an int
			customer_id = int(customer_id)
			con = cn.dbConnectSQLServer()

			#Check if the customer is in the database
			if churnFunctions.isCustomerActive(con,customer_id):
				#Return the JSON with the required data
				return churnFunctions.getCustomerServs(con,customer_id)
			else:
				abort(400)

		except ValueError as ve:
			abort(400)
		except cn.sqlServerException as e:
			app.logger.exception('SQLServer Exception',e)
			abort(500)
		except cn.mySqlException as err:
			app.logger.exception('mySQL Exception',err)
			abort(500)
		finally:
			try:
				if(con is not None):
					con.close()
			except cn.sqlServerException as e2:
				app.logger.exception('Unable to close the connection', e2)


"""****************************************************************************************************
* Description: method to return the current bills of a client in the database
* INPUT: customer id
* OUTPUT: a JSON with the bills of the client
****************************************************************************************************"""
class getCustomerBills(Resource):
	#Authentication
	@auth.login_required

	def get(self,customer_id):

		con = None
		try:

			#Check if customer_id is an int
			customer_id = int(customer_id)
			con = cn.dbConnectSQLServer()

			#Check if the customer is in the database
			if churnFunctions.isCustomerActive(con,customer_id):
				#Return the JSON with the required data
				return churnFunctions.getCustomerBills(con,customer_id)
			else:
				abort(400)

		except ValueError as ve:
			abort(400)
		except cn.sqlServerException as e:
			app.logger.exception('SQLServer Exception',e)
			abort(500)
		except cn.mySqlException as err:
			app.logger.exception('mySQL Exception',err)
			abort(500)
		finally:
			try:
				if(con is not None):
					con.close()
			except cn.sqlServerException as e2:
				app.logger.exception('Unable to close the connection', e2)

"""****************************************************************************************************
* Description: allow to create users for the API
* INUT: user, pwd, email and optionally role
* OUTPUT: -
****************************************************************************************************"""
class userManagement(Resource):
	#Authentication
	@auth.login_required

	def post(self):
		#Read post parameters
		user  = request.form['user']
		pwd = request.form['pwd']
		email = request.form['email']
		role = request.form.get('role') #Optional

		#Validate email
		if (not re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$',email.lower())):
			abort(400)

		#Validate role
		if (role) and (role not in ('admin', 'user')):
			abort(400)

		#Create the connection
		con = None
		try:
			conexion = cn.dbConnectMySQL()
			mycursor = conexion.cursor()

			#Validate admin permisions for the user
			mycursor.execute("SELECT Role FROM users WHERE username=" + "\'" + auth.username() + "\'")
			userRole = mycursor.fetchone()
			if userRole[0]== 'admin':

				#Check if the username exists in the database
				mycursor.execute("SELECT username from users WHERE username=" + "\'" + user + "\'")
				_userWithSameName = mycursor.fetchone()

				if (not _userWithSameName):

					#Create the user in the database
					if (role):
						mycursor.execute("INSERT INTO users (username, password, email, role) VALUES ("+"\'"+user+"\',"+"\'"+generate_password_hash(pwd)+"\',"+"\'"+email+"\',"+"\'"+role+"\')")
					else:
						mycursor.execute("INSERT INTO users (username, password, email) VALUES ("+"\'"+user+"\',"+"\'"+generate_password_hash(pwd)+"\',"+"\'"+email+"\')")
					conexion.commit()

					#Return response
					app.logger.info(f'User {user} added to the database')
					return {'message': 'User added to the database'}

				else:
					abort(400,"There is already an username with this name in the database")
			else:
				abort(401)
			mycursor.close()

		except cn.mySqlException as e:
			try:
				if not (con is None):
					con.rollback()
				app.logger.exception('mySQL Exception', e)
				abort(500)
			except cn.mySqlException as eRoll:
				app.logger.exception('mySQL Exception', e)
				abort(500)
		finally:
			try:
				if not (con is None):
					con.close()
			except mySqlException as eCon:
				app.logger.exception('Unable to close connection to the database', e2)

"""****************************************************************************************************
* Methods definition
****************************************************************************************************"""
api.add_resource(customersChurnList,'/customers/churn')
api.add_resource(getCustomerChurn,'/customers/churn/<customer_id>')
api.add_resource(getCustomerData,'/customers/<customer_id>')
api.add_resource(getCustomerServs,'/customers/servs/<customer_id>')
api.add_resource(getCustomerBills,'/customers/bills/<customer_id>')
api.add_resource(userManagement,'/users')
api.add_resource(ping,'/ping')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
