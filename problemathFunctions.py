"""****************************************************************************************************
* Churn functions for the rest API
* Version: 0
* Date: 18/11/2019
****************************************************************************************************"""

from connections import dbConnectMySQL
from connections import mySQLException
import os

UPLOAD_FOLDER = 'Data/tmp'
DATA_DIRECTORY = 'Data'

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
		con.start_transaction()

		# Check tha variables to create the Query String
		sqlQueryBeginningProblem = 'INSERT INTO problem (Tex, URL_PDF_State, URL_PDF_Full, Dep_State'
		sqlQueryValuesProblem= 'VALUES (%s, %s, %s, %s'
		tupleValuesProblem=()

		#We read the file
		file = open(absoluteURL,"r")
		tex = file.read()
		file.close()

		tupleValuesProblem = tupleValuesProblem + (tex,'placeholder','placeholder',0)

		if(mag):
			sqlQueryBeginningProblem = sqlQueryBeginningProblem + ', Magazine'
			sqlQueryValuesProblem = sqlQueryValuesProblem + ', %s'
			tupleValuesProblem = tupleValuesProblem + (mag,)
		if(prop):
			sqlQueryBeginningProblem = sqlQueryBeginningProblem + ', Proposer'
			sqlQueryValuesProblem = sqlQueryValuesProblem + ', %s'
			tupleValuesProblem = tupleValuesProblem + (prop,)

		sqlQueryBeginningProblem = sqlQueryBeginningProblem + ') '
		sqlQueryValuesProblem = sqlQueryValuesProblem + ')'

		sqlQueryProblem = sqlQueryBeginningProblem + sqlQueryValuesProblem

		#Execute the query
		mycursorProblem = con.cursor(prepared=True)
		mycursorProblem.execute(sqlQueryProblem, tupleValuesProblem)
		idProblem = mycursorProblem.lastrowid
		mycursorProblem.close()

		#We update the placeholders
		mycursorUpdate= con.cursor(prepared=True)
		sqlQueryUpdate = 'UPDATE problem SET URL_PDF_State=%s, URL_PDF_Full=%s WHERE id=%s'
		URL_PDF_State = DATA_DIRECTORY+'/'+str(idProblem)+'/pdfState.pdf'
		URL_PDF_Full = DATA_DIRECTORY+'/'+str(idProblem)+'/pdfFull.pdf'
		tupleValuesUpdate = (URL_PDF_State,URL_PDF_Full,idProblem)
		mycursorUpdate.execute(sqlQueryUpdate, tupleValuesUpdate)
		mycursorUpdate.close()

		#We add the tags to the database
		mycursorFindTag= con.cursor(prepared=True)
		mycursorNewTag= con.cursor(prepared=True)
		mycursorTags= con.cursor(prepared=True)

		if(tags):
			list_tags = tags.split(",")
			sqlQueryFindTag = 'SELECT Id FROM tag WHERE Name = %s '
			sqlQueryNewTags = 'INSERT INTO tag (Name) VALUES (%s)'
			sqlQueryTags = 'INSERT INTO problem_tag (Id_Problem,Id_Tag) VALUES (%s,%s)'
			for tag in list_tags:
				idTag = None
				mycursorFindTag.execute(sqlQueryFindTag,(tag,))
				row = mycursorFindTag.fetchone()
				if row is None:
					mycursorNewTag.execute(sqlQueryNewTags,(tag,))
					idTag= mycursorNewTag.lastrowid
				else:
					idTag=row[0]		
				mycursorTags.execute(sqlQueryTags,(idProblem,idTag))
		
		mycursorFindTag.close()
		mycursorNewTag.close()
		mycursorTags.close()

		#We commit the changes
		con.commit()

		#Now we compile de problem
		cliMakeDir = 'mkdir '+ DATA_DIRECTORY+'/'+str(idProblem)
		cliCompile = 'laton  -o '+ URL_PDF_State + ' ' + absoluteURL 
		print(cliCompile)
		os.system(cliMakeDir)
		os.system(cliCompile)


		return True
	except mySQLException as e:
		con.rollback()
		raise e
