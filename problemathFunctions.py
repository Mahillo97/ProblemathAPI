"""****************************************************************************************************
* Churn functions for the rest API
* Version: 0
* Date: 18/11/2019
****************************************************************************************************"""

from connections import dbConnectMySQL
from connections import mySQLException

"""****************************************************************************************************
* Description: method to return a list of customers sensitive to leave the company in the next year
* INPUT: -
* OUTPUT: dict object with a list of customers sensitive who might leave.
****************************************************************************************************"""


def getProblemList(con, tags, mag, prop):

	try:
		# Check tha variables to create the Query String
		sqlQueryBeginning = 'SELECT P.Id, P.Magazine, P.Proposer,group_concat(distinct T2.Name) as tags\
					FROM problem as P join problem_tag as PT on P.Id=PT.Id_Problem JOIN tag as T on PT.Id_Tag=T.Id join problem_tag as PT2 on PT2.Id_Problem = P.Id JOIN tag as T2 on PT2.Id_Tag=T2.Id '
		sqlQueryWhere = ''
		sqlQueryEnd = 'GROUP BY P.Id ORDER BY COUNT(Distinct T.Id) DESC'
		tuple_values=()
		if(tags or mag or prop):
			sqlQueryWhere = 'WHERE '
			if(tags):
				list_tags = tags.split(",")
				tuple_values = tuple_values + tuple(list_tags)
				for i in range(len(list_tags)):
					if len(list_tags)==1:
						sqlQueryWhere = sqlQueryWhere + '(T.Name=%s) '
					elif i == 0:
						sqlQueryWhere = sqlQueryWhere + '(T.Name=%s '
					elif i==len(list_tags)-1:
						sqlQueryWhere = sqlQueryWhere + 'or T.Name=%s) '
					else:
						sqlQueryWhere = sqlQueryWhere + 'or T.Name=%s '
			if(mag):
				if(tags):
					sqlQueryWhere = sqlQueryWhere + 'and '
				tuple_values = tuple_values + (mag,)
				sqlQueryWhere = sqlQueryWhere + 'P.Magazine=%s '
			if(prop):
				if(mag or tags):
					sqlQueryWhere = sqlQueryWhere + 'and '
				tuple_values = tuple_values + (prop,)
				sqlQueryWhere = sqlQueryWhere + 'P.Proposer=%s '

		sqlQuery = sqlQueryBeginning + sqlQueryWhere + sqlQueryEnd
		
		#Execute the query
		mycursor = con.cursor(prepared=True)
		mycursor.execute(sqlQuery, tuple_values)
		row_headers = [x[0].lower() for x in mycursor.description]
		problems_data = mycursor.fetchall()
		json_data = []
		for problem in problems_data:
			json_data.append(
				dict(zip(row_headers, [data if not isinstance(data,bytearray) else data.decode("utf-8") if counter != len(problem)-1 else data.decode("utf-8").split(",") for counter, data in enumerate(problem)])))
			mycursor.close()
			
		return dict(problems=json_data)
	except mySQLException as e:
		raise e

"""****************************************************************************************************
* Description: method to return the data of a problem
* INPUT: problem_id is an integer
* OUTPUT: a dict with the data of a 
****************************************************************************************************"""
def getProblem(con, problem_id):

	try:
		# Check tha variables to create the Query String
		sqlQuery = 'SELECT P.Id, P.Magazine, P.Tex, P.Proposer, P.Dep_State, P.URL_PDF_State, P.URL_PDF_Full, group_concat(distinct T.Name) as tags\
					FROM problem as P join problem_tag as PT on P.Id=PT.Id_Problem JOIN tag as T on PT.Id_Tag=T.Id\
					WHERE P.Id = %s\
					GROUP BY P.Id, P.Magazine, P.Tex, P.Proposer, P.Dep_State, P.URL_PDF_State, P.URL_PDF_Full'
		#Execute the query
		mycursor = con.cursor(prepared=True)
		mycursor.execute(sqlQuery, (problem_id,))
		row_headers = [x[0].lower() for x in mycursor.description]
		problem = mycursor.fetchone()
		if(problem):
			json_data = dict(zip(row_headers, [data if not isinstance(data,bytearray) else data.decode("utf-8") if counter != len(problem)-1 else data.decode("utf-8").split(",") for counter, data in enumerate(problem)]))
		else:
			json_data = None

		mycursor.close()			
		return json_data
	except mySQLException as e:
		raise e

"""****************************************************************************************************
* Description: method to say if a customer is active in the database
* INPUT: customer id
* OUTPUT: a boolean value: true if the customer is active in the database false in other cases
****************************************************************************************************"""
def getProblemPDFState(con, problem_id):

	try:
		# Check tha variables to create the Query String
		sqlQuery = 'SELECT P.URL_PDF_State FROM problem as P WHERE P.Id = %s'

		#Execute the query
		mycursor = con.cursor(prepared=True)
		mycursor.execute(sqlQuery, (problem_id,))
		url = mycursor.fetchone()[0].decode("utf-8")
		mycursor.close()

		return url
	except mySQLException as e:
		raise e

	

"""****************************************************************************************************
* Description: method to return the current values of a client in the database
* INPUT: customer id
* OUTPUT: a JSON with the data client
****************************************************************************************************"""
def getProblemPDFFull(con, problem_id):

	try:
		# Check tha variables to create the Query String
		sqlQuery = 'SELECT P.URL_PDF_Full FROM problem as P WHERE P.Id = %s'

		#Execute the query
		mycursor = con.cursor(prepared=True)
		mycursor.execute(sqlQuery, (problem_id,))
		url = mycursor.fetchone()[0].decode("utf-8")
		mycursor.close()

		return url
	except mySQLException as e:
		raise e

"""****************************************************************************************************
* Description: method to return the bills of a client
* INPUT: customer id
* OUTPUT: a JSON with the data client
****************************************************************************************************"""
def saveProblemDB(con, absoluteURL, tags, mag, prop):

	try:
		# Check tha variables to create the Query String
		sqlQueryBeginning = 'INSERT INTO problem (Tex,URL_PDF_State,URL_PDF_State'
		sqlQuerycolumns = ''
		sqlQueryValues= 'VALUES'
		tuple_values=()
		if(tags or mag or prop):
			sqlQueryWhere = 'WHERE '
			if(tags):
				list_tags = tags.split(",")
				tuple_values = tuple_values + tuple(list_tags)
				for i in range(len(list_tags)):
					if len(list_tags)==1:
						sqlQueryWhere = sqlQueryWhere + '(T.Name=%s) '
					elif i == 0:
						sqlQueryWhere = sqlQueryWhere + '(T.Name=%s '
					elif i==len(list_tags)-1:
						sqlQueryWhere = sqlQueryWhere + 'or T.Name=%s) '
					else:
						sqlQueryWhere = sqlQueryWhere + 'or T.Name=%s '
			if(mag):
				if(tags):
					sqlQueryWhere = sqlQueryWhere + 'and '
				tuple_values = tuple_values + (mag,)
				sqlQueryWhere = sqlQueryWhere + 'P.Magazine=%s '
			if(prop):
				if(mag or tags):
					sqlQueryWhere = sqlQueryWhere + 'and '
				tuple_values = tuple_values + (prop,)
				sqlQueryWhere = sqlQueryWhere + 'P.Proposer=%s '

		sqlQuery = sqlQueryBeginning + sqlQueryWhere + sqlQueryEnd
		
		#Execute the query
		mycursor = con.cursor(prepared=True)
		mycursor.execute(sqlQuery, tuple_values)
		row_headers = [x[0].lower() for x in mycursor.description]
		problems_data = mycursor.fetchall()
		json_data = []
		for problem in problems_data:
			json_data.append(
				dict(zip(row_headers, [data if not isinstance(data,bytearray) else data.decode("utf-8") if counter != len(problem)-1 else data.decode("utf-8").split(",") for counter, data in enumerate(problem)])))
			mycursor.close()
			
		return dict(problems=json_data)
	except mySQLException as e:
		raise e

"""****************************************************************************************************
* Description: method to return the active services of a client
* INPUT: customer id
* OUTPUT: a JSON with the active services of a client
****************************************************************************************************"""
def getCustomerServs(con, customer_id):

	# Select in the database the info for the selected customer

	try:
		sqlQuery = 'SELECT * FROM tblServicios where IDCliente =' + str(customer_id) + '  and Estado = \'ACTIVO\''
		servsClient = pd.read_sql(sqlQuery, con)

		# Return the client bills
		serv_list = []
		for index, serv in servsClient.iterrows():
			dictServ = dict()
			for value, column in zip(serv.values,servsClient.columns):
				if column == "IDClient":
					dictServ["ID"] = value
				elif type(value).__name__ == "Timestamp":
					dictServ[column] = str(value)
				else:
					dictServ[column] = value
			serv_list = np.append(serv_list,dictServ)
			ord_serv_list = sorted(list(serv_list), key=lambda k: k['FAlta'], reverse=True)
		return {'list': ord_serv_list}

	except sqlServerException as e:
		raise e
	except mySQLException as err:
		raise err
