"""****************************************************************************************************
* Churn functions for the rest API
* Version: 0
* Date: 18/11/2019
****************************************************************************************************"""

import connections as cn

"""****************************************************************************************************
* Description: method to return a list of customers sensitive to leave the company in the next year
* INPUT: -
* OUTPUT: json object with a list of customers sensitive who might leave.
****************************************************************************************************"""
def customersChurnList(con):

	#Select in the database to get the list of clients that will churn
	try:
		sqlQuery = 'SELECT * FROM tblModelChurn WHERE activosFech1=1'
		dataClientIDs = pd.read_sql(sqlQuery, con)
		dataClient = dataClientIDs.drop(['sampleID', 'activosFech1', 'activosFech2'], axis=1)

		#Call churn model to execute prediction
		with open('ModeloChurnPrediction/modelChurn.pkl', 'rb') as pickle_file:
			model = pickle.load(pickle_file)
		pred_aux = model.predict_proba(dataClient)
		pred_list = []
		for pred, ID, fact in zip(pred_aux, dataClientIDs.sampleID, dataClientIDs.factAnual):
			score = pred[0]*100
			if score>50:
				dictClient = dict({'ID':int(ID),'score':float(score), 'turnover':float(fact)})
				#'fact':float(client.factAnual)
				pred_list = np.append(pred_list,dictClient)
		ord_pred_list = sorted(list(pred_list), key=lambda k: k['turnover'], reverse=True)

		#Build a JSON with customer whose prediction is 0
		return {'list':ord_pred_list}

	except cn.sqlServerException as e:
		raise e
	except cn.mySqlException as err:
		raise err


"""****************************************************************************************************
* Description: method to return a churn prediction for one customer
* INPUT: customer id that must be active
* OUTPUT: a JSON with churn: [0,1] and score percentage of the prediction
****************************************************************************************************"""
def getCustomerChurn(con, customer_id):

	#Select in the database the info for the selected customer
	try:
		sqlQuery = 'SELECT * FROM tblModelChurn WHERE sampleID='+str(customer_id)
		dataClient = pd.read_sql(sqlQuery, con)
		dataClient = dataClient.drop(['sampleID', 'activosFech1', 'activosFech2'], axis=1)

		#Call churn model to execute prediction
		with open('ModeloChurnPrediction/modelChurn.pkl', 'rb') as pickle_file:
			model = pickle.load(pickle_file)
		pred = model.predict_proba(dataClient)
		score = pred[0][0]
		if score>0.5:
			churn = 0
		else:
			churn = 1
			score = pred[0][1]

		return {'churn':churn,'score':float(score*100)}

	except cn.sqlServerException as e:
		raise e
	except cn.mySqlException as err:
		raise err

"""****************************************************************************************************
* Description: method to say if a customer is active in the database
* INPUT: customer id
* OUTPUT: a boolean value: true if the customer is active in the database false in other cases
****************************************************************************************************"""
def isCustomerActive(con, customer_id):

	isCustomer = False

	#Select in the database the customer
	try:
		sqlQuery = 'SELECT * FROM tblDataClientChurn WHERE sampleID='+str(customer_id)
		dataClient = pd.read_sql(sqlQuery, con)
		if dataClient.shape[0]!=0 and dataClient.activosFech1[0] == 1:
			isCustomer = True

	except cn.sqlServerException as e:
		raise e
	except cn.mySqlException as err:
		raise err

	return isCustomer

"""****************************************************************************************************
* Description: method to return the current values of a client in the database
* INPUT: customer id
* OUTPUT: a JSON with the data client
****************************************************************************************************"""
def getCustomerData(con, customer_id):

	#Select in the database the info for the selected customer

	try:
		sqlQuery = 'SELECT * FROM tblDataClientChurn WHERE sampleID='+str(customer_id)
		dataClient = pd.read_sql(sqlQuery, con)

		#Return the client data
		dictClient = dict()
		for value, column in zip(dataClient.values[0],dataClient.columns):
			if column == "sampleID":
				dictClient["ID"] = value
			else:
				dictClient[column] = value

		return dictClient

	except cn.sqlServerException as e:
		raise e
	except cn.mySqlException as err:
		raise err

"""****************************************************************************************************
* Description: method to return the bills of a client
* INPUT: customer id
* OUTPUT: a JSON with the data client
****************************************************************************************************"""
def getCustomerBills(con, customer_id):

	#Select in the database the info for the selected customer

	try:
		sqlQuery = 'SELECT * FROM tblFacturas where IDCliente =' + str(customer_id)
		billsClient = pd.read_sql(sqlQuery, con)

		#Return the client bills
		bill_list = []
		for index, bill in billsClient.iterrows():
			dictBill = dict()
			for value, column in zip(bill.values,billsClient.columns):
				if column == "IDClient":
					dictBill["ID"] = value
				elif type(value).__name__ == "Timestamp":
					dictBill[column] = str(value)
				else:
					dictBill[column] = value
			bill_list = np.append(bill_list,dictBill)
			ord_bill_list = sorted(list(bill_list), key=lambda k: k['IDFactura'], reverse=True)
		return {'list': ord_bill_list}

	except cn.sqlServerException as e:
		raise e
	except cn.mySqlException as err:
		raise err

"""****************************************************************************************************
* Description: method to return the active services of a client
* INPUT: customer id
* OUTPUT: a JSON with the active services of a client
****************************************************************************************************"""
def getCustomerServs(con, customer_id):

	#Select in the database the info for the selected customer

	try:
		sqlQuery = 'SELECT * FROM tblServicios where IDCliente =' + str(customer_id) + '  and Estado = \'ACTIVO\''
		servsClient = pd.read_sql(sqlQuery, con)

		#Return the client bills
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

	except cn.sqlServerException as e:
		raise e
	except cn.mySqlException as err:
		raise err
