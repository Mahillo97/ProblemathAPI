"""****************************************************************************************************
* REST API to use for the problemath web
* Version: 0
* Date: 15/4/2020
****************************************************************************************************"""

from flask import Flask, request, abort, jsonify, make_response, send_from_directory, url_for
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from flask.logging import create_logger
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from connections import dbConnectMySQL
from connections import mySQLException
import problemathFunctions
import json
import re
import os

UPLOAD_FOLDER = '/home/almahill/ProblemathAPIData/tmp'
ALLOWED_EXTENSIONS = {'tex'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
log = create_logger(app)
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
        con = None
        try:
            con = dbConnectMySQL()
            mycursor = con.cursor(prepared=True)
            sqlQuery = ' SELECT * FROM users WHERE username=%s and password=SHA2(%s,256) '
            mycursor.execute(sqlQuery, (username, password,))
            _password = mycursor.fetchone()
            mycursor.close()
            verified = (not (_password is None))

        except mySQLException as e:
            raise e
        finally:
            try:
                if con is not None:
                    con.close()
            except mySQLException as eCon:
                raise eCon
        return verified


"""****************************************************************************************************
* Description: method check the credentials
* INPUT: -
* OUTPUT: -
****************************************************************************************************"""


class ping(Resource):
    # Authentication
    @auth.login_required
    def get(self):
        pass


"""****************************************************************************************************
* Description: method to return a list of problems based on a QueryString
* INPUT: QueryString
* OUTPUT: json object with a list of problems and its basic info
****************************************************************************************************"""


class problemQueryList(Resource):

    def get(self):
        # Select in the database to get the info for the problems

        con = None
        try:
            con = dbConnectMySQL()

            # We get the parameters in the queryString
            validParams = ['tags', 'mag', 'prop']

            if(all(True if x in validParams else False for x in request.args.keys())):
                tags = request.args.get('tags')
                mag = request.args.get('mag')
                prop = request.args.get('prop')

                # Return the JSON created in the problemath library

                return jsonify(problemathFunctions.getProblemList(con, tags, mag, prop))
            else:
                abort(400)

        except mySQLException:
            log.exception('mySQL Exception')
            abort(500)
        finally:
            try:
                if(con is not None):
                    con.close()
            except mySQLException:
                log.exception('Unable to close connection')


"""****************************************************************************************************
* Description: method to return a churn prediction for one customer
* INPUT: customer id
* OUTPUT: a JSON with churn: [0,1] and score percentage of the prediction
****************************************************************************************************"""


class problemQuery(Resource):
    def get(self, problem_id):

        # Select in the database the info for the selected problem
        con = None
        try:
            # Check if problem_id is an int
            problem_id = int(problem_id)

            con = dbConnectMySQL()
            data = problemathFunctions.getProblem(con, problem_id)
            return jsonify(data) if data else abort(404)

        except ValueError:
            abort(400)
        except mySQLException:
            log.exception('mySQL Exception')
            abort(500)
        finally:
            try:
                if(con is not None):
                    con.close()
            except mySQLException:
                log.exception('Unable to close connection')


"""****************************************************************************************************
* Description: method to return the current values of a client in the database
* INPUT: customer id
* OUTPUT: a JSON with the data client
****************************************************************************************************"""


class problemPDFState(Resource):
    def get(self, problem_id):

        # Select in the database the info for the selected problem
        con = None
        try:
            # Check if problem_id is an int
            problem_id = int(problem_id)
            con = dbConnectMySQL()
            urlPDF = problemathFunctions.getProblemPDFState(con, problem_id)
            PDFName = urlPDF.split("/")[-1]
            PDFDirectory = urlPDF[:urlPDF.rindex("/")]
            return send_from_directory(PDFDirectory, PDFName)

        except ValueError:
            abort(400)
        except mySQLException:
            log.exception('mySQL Exception')
            abort(500)
        finally:
            try:
                if(con is not None):
                    con.close()
            except mySQLException:
                log.exception('Unable to close connection')


"""****************************************************************************************************
* Description: method to return the current servs of a client in the database
* INPUT: customer id
* OUTPUT: a JSON with the servs of the client
****************************************************************************************************"""


class problemPDFFull(Resource):
    def get(self, problem_id):

        # Select in the database the info for the selected problem
        con = None
        try:
            # Check if problem_id is an int
            problem_id = int(problem_id)
            con = dbConnectMySQL()
            urlPDF = problemathFunctions.getProblemPDFFull(con, problem_id)
            PDFName = urlPDF.split("/")[-1]
            PDFDirectory = urlPDF[:urlPDF.rindex("/")]
            return send_from_directory(PDFDirectory, PDFName)

        except ValueError:
            abort(400)
        except mySQLException:
            log.exception('mySQL Exception')
            abort(500)
        finally:
            try:
                if(con is not None):
                    con.close()
            except mySQLException:
                log.exception('Unable to close connection')


"""****************************************************************************************************
* Description: method to return the current bills of a client in the database
* INPUT: customer id
* OUTPUT: a JSON with the bills of the client
****************************************************************************************************"""


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class uploadProblem(Resource):
    # Authentication
    @auth.login_required
    def post(self):

        # Create the connection to upload the problem
        con = None
        try:
            con = dbConnectMySQL('admin')
            # We get the parameters in the queryString
            validParams = ['file', 'tags', 'mag', 'prop']

            if(all(True if x in validParams else False for x in request.args.keys())):

                # check if the post request has the file part
                if 'file'  in request.files and request.files['file'].filename == '':
                    file = request.files['file']

                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        absoluteURL = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(absoluteURL)

                        # Now we get the rest of params
                        tags = request.args.get('tags')
                        mag = request.args.get('mag')
                        prop = request.args.get('prop')

                        problemathFunctions.saveProblemDB(con, absoluteURL, tags, mag, prop)

                        os.remove(absoluteURL)

                        pass
            else:
                abort(400)

        except mySQLException:
            log.exception('mySQL Exception')
            abort(500)
        finally:
            try:
                if(con is not None):
                    con.close()
            except mySQLException:
                log.exception('Unable to close connection')

"""****************************************************************************************************
* Description: allow to create users for the API
* INUT: user, pwd, email and optionally role
* OUTPUT: -
****************************************************************************************************"""


class userManagement(Resource):
    # Authentication
    @auth.login_required
    def post(self):
        # Read post parameters
        user = request.form['user']
        pwd = request.form['pwd']
        email = request.form['email']
        role = request.form.get('role')  # Optional

        # Validate email
        if (not re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$', email.lower())):
            abort(400)

        # Validate role
        if (role) and (role not in ('admin', 'user')):
            abort(400)

        # Create the connection
        con = None
        try:
            conexion = dbConnectMySQL()
            mycursor = conexion.cursor()

            # Validate admin permisions for the user
            mycursor.execute(
                "SELECT Role FROM users WHERE username=" + "\'" + auth.username() + "\'")
            userRole = mycursor.fetchone()
            if userRole[0] == 'admin':

                # Check if the username exists in the database
                mycursor.execute(
                    "SELECT username from users WHERE username=" + "\'" + user + "\'")
                _userWithSameName = mycursor.fetchone()

                if (not _userWithSameName):

                    # Create the user in the database
                    if (role):
                        mycursor.execute("INSERT INTO users (username, password, email, role) VALUES ("+"\'" +
                                         user+"\',"+"\'"+generate_password_hash(pwd)+"\',"+"\'"+email+"\',"+"\'"+role+"\')")
                    else:
                        mycursor.execute("INSERT INTO users (username, password, email) VALUES (" +
                                         "\'"+user+"\',"+"\'"+generate_password_hash(pwd)+"\',"+"\'"+email+"\')")
                    conexion.commit()

                    # Return response
                    app.logger.info(f'User {user} added to the database')
                    return {'message': 'User added to the database'}

                else:
                    abort(
                        400, "There is already an username with this name in the database")
            else:
                abort(401)
            mycursor.close()

        except mySQLException as e:
            try:
                if not (con is None):
                    con.rollback()
                app.logger.exception('mySQL Exception', e)
                abort(500)
            except mySQLException as eRoll:
                app.logger.exception('mySQL Exception', e)
                abort(500)
        finally:
            try:
                if not (con is None):
                    con.close()
            except mySQLException as eCon:
                app.logger.exception(
                    'Unable to close connection to the database', e2)


"""****************************************************************************************************
* Description: test
* INUT: 
* OUTPUT: -
****************************************************************************************************"""


class test(Resource):

    def get(self):

        # Create the connection
        con = None
        try:
            conexion = dbConnectMySQL()
            mycursor = conexion.cursor(prepared=True)
            sqlQuery = 'SELECT username FROM users WHERE username=%s'
            mycursor.execute(sqlQuery, ("almahill",))
            row_headers = [x[0] for x in mycursor.description]
            users_data = mycursor.fetchall()
            json_data = []
            for user in users_data:
                json_data.append(
                    dict(zip(row_headers, [data.decode("utf-8") for data in user])))
            mycursor.close()

            return jsonify(dict(users=json_data))

        except mySQLException as e:
            try:
                if not (con is None):
                    con.rollback()
                app.logger.exception('mySQL Exception', e)
                abort(500)
            except mySQLException as eRoll:
                app.logger.exception('mySQL Exception', e)
                abort(500)
        finally:
            try:
                if not (con is None):
                    con.close()
            except mySQLException as eCon:
                app.logger.exception(
                    'Unable to close connection to the database', e2)


"""****************************************************************************************************
* Methods definition
****************************************************************************************************"""
api.add_resource(problemQueryList, '/users/problems')
api.add_resource(problemQuery, '/users/problem/<problem_id>')
api.add_resource(problemPDFState, '/users/problem/<problem_id>/pdfState')
api.add_resource(problemPDFFull, '/users/problem/<problem_id>/pdfFull')
api.add_resource(getCustomerBills, '/customers/bills/<customer_id>')
api.add_resource(userManagement, '/users')
api.add_resource(ping, '/ping')
api.add_resource(test, '/test')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
