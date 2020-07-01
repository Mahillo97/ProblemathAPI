"""****************************************************************************************************
* REST API to use for the problemath web
* Version: 0
* Date: 15/4/2020
****************************************************************************************************"""
import problemathFunctions
import json
import re
import os
import time
from flask import Flask, request, abort, jsonify, make_response, send_from_directory, url_for
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from flask.logging import create_logger
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from connections import dbConnectMySQL
from connections import mySQLException
from apscheduler.schedulers.background import BackgroundScheduler

UPLOAD_FOLDER = 'Data/tmp'
ALLOWED_EXTENSIONS = {'tex', 'zip'}

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
            validParams = ['tags', 'mag', 'prop', 'tamPag', 'pag']

            if(all(True if x in validParams else False for x in request.args.keys())):
                tags = request.args.get('tags')
                mag = request.args.get('mag')
                prop = request.args.get('prop')
                tamPag = request.args.get('tamPag')
                pag = request.args.get('pag')

                # Check if tamPag and pag are ints
                if(tamPag):
                    tamPag = int(tamPag)

                if(pag):
                    pag = int(pag)

                # Return the JSON created in the problemath library
                return jsonify(problemathFunctions.getProblemList(con, tags, mag, prop, tamPag, pag))
            else:
                abort(400)
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
* Description: method to return a list of problems based on a QueryString
* INPUT: QueryString
* OUTPUT: json object with a list of problems and its basic info
****************************************************************************************************"""


class problemQueryListSize(Resource):

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
                return jsonify(problemathFunctions.getProblemListSize(con, tags, mag, prop))
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
* Description: method to return the current servs of a client in the database
* INPUT: customer id
* OUTPUT: a JSON with the servs of the client
****************************************************************************************************"""

class resourceDependency(Resource):
    def get(self, dependency_id):

        con = None
        try:
            # Check if dependency_id is an int
            dependency_id = int(dependency_id)
            con = dbConnectMySQL()
            urlImage = problemathFunctions.getDependency(con, dependency_id)
            if(urlImage):
                imageName = urlImage.split("/")[-1]
                imageDirectory = urlImage[:urlImage.rindex("/")]
                return send_from_directory(imageDirectory, imageName)
            else:
                abort(404)
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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class uploadProblem(Resource):
    # Authentication
    @auth.login_required
    def post(self):

        # Create the connection to upload the problem
        con = None
        try:
            con = dbConnectMySQL('admin')
            # We get the parameters in the queryString
            validParams = ['problem', 'tags', 'mag', 'prop']
            if(all(True if x in validParams else True if (re.match('solution[1-9]?', x) or re.match('solver[1-9]?', x)) else False for x in list(request.args.keys())+list(request.form.keys()))):
                # check if the post request has the problem part and at least one solution
                if 'problem' in request.files and request.files['problem'].filename != '' and 'solution1' in request.files and request.files['solution1'].filename != '':
                    problem = request.files['problem']
                    if problem and allowed_file(problem.filename):
                        timeStampMark = str('{:2f}'.format(
                            time.time()*100000000)).split('.')[0]
                        filename = timeStampMark + \
                            secure_filename(problem.filename)
                        absoluteURL = os.path.join(
                            app.config['UPLOAD_FOLDER'], filename)
                        problem.save(absoluteURL)

                        solutionsData = []

                        for param, solution in request.files.items():
                            numberSolu = param[param.find(
                                'solution') + len('solution'):]
                            if re.match('solution[1-9]?', param):
                                if solution and allowed_file(solution.filename):
                                    solver = request.form.get(
                                        'solver' + str(numberSolu))
                                    timeStampMark = str('{:2f}'.format(
                                        time.time()*100000000)).split('.')[0]
                                    filename = timeStampMark + \
                                        secure_filename(solution.filename)
                                    absoluteURLAux = os.path.join(
                                        app.config['UPLOAD_FOLDER'], filename)
                                    solutionsData.append(
                                        dict(solutionURL=absoluteURLAux, solver=solver))
                                    solution.save(absoluteURLAux)
                                else:
                                    abort(400)

                        # Now we get the rest of params
                        tags = request.form.get('tags')
                        mag = request.form.get('mag')
                        prop = request.form.get('prop')

                        if(problemathFunctions.saveProblem(
                            con, absoluteURL, solutionsData, tags, mag, prop)):
                            return {'message':'Problem uploaded correctly.'}
                        else:
                            abort(400,'Errors compiling the Latex')                      
            abort(400,'Error with the parameters')
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

class removeProblem(Resource):
    # Authentication
    @auth.login_required
    def post(self,problem_id):

        # Create the connection to delete the problem
        con = None
        try:
            # Check if problem_id is an int
            problem_id = int(problem_id)
            con = dbConnectMySQL('admin')

            #Check if the problem is in the database
            if(problemathFunctions.getProblem(con, problem_id)):
                response = problemathFunctions.deleteProblem(con, problem_id)
                return {'message': response}
            else:
                abort(404)
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
* Description: method to return a pdf of a series of problems
* INPUT: 
* OUTPUT: a PDF
****************************************************************************************************"""


class getProblemSheet(Resource):

    def get(self):

        # Create the connection to upload the problem
        con = None
        try:
            con = dbConnectMySQL()
            keys = list(request.args.keys())
            num = int(len(keys)/2)
            keysP = list(filter(lambda x: x.startswith('problem'), keys))
            keysP.sort()
            keysS = list(filter(lambda x: x.startswith('solution'), keys))
            keysS.sort()

            if keysP and keysS and len(keysP) == num and len(keysS) == num:
                if (all((keysP[n-1][-1] == str(n) and keysS[n-1][-1] == str(n)) for n in range(1, num+1))):
                    urlPDF = problemathFunctions.getProblemSheet(
                        con, request.args)
                    if(urlPDF):
                        PDFName = urlPDF.split("/")[-1]
                        PDFDirectory = urlPDF[:urlPDF.rindex("/")]
                        return send_from_directory(PDFDirectory, PDFName)
                    else:
                        abort(400,'Compilation errors')            
            abort(400,'Unvalid params')
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
* INUT: user and pwd
* OUTPUT: -
****************************************************************************************************"""
class addUser(Resource):
    # Authentication
    @auth.login_required
    def post(self):
        # Read post parameters
        username = request.form.get('user')
        password = request.form.get('pwd')

        # Create the connection
        con = None
        try:
            #Open connection
            con = dbConnectMySQL('admin')

            # Check if the username exists in the database
            sqlQueryUser = 'SELECT * FROM users as U WHERE U.username = %s'
            
            # Execute the query
            mycursorUser = con.cursor(prepared=True)
            mycursorUser.execute(sqlQueryUser, (username,))
            user = mycursorUser.fetchone()
            mycursorUser.close()
            
            if(not user):
                sqlQueryInsert = 'INSERT INTO users (username,password) VALUES (%s,SHA2(%s,256))'

                mycursorInsert = con.cursor(prepared=True)
                mycursorInsert.execute(sqlQueryInsert, (username,password))
                mycursorInsert.close()
                con.commit()

                # Return response
                log.info(f'User {username} added to the database')
                return {'message': 'User added to the database'}

            else:
                #The user already exists in the data base
                abort(400, "There is already an username with this name in the database")
        except mySQLException:         
            try:
                if(con is not None):
                    con.rollback()
                log.exception('mySQL Exception')
            except mySQLException:
                log.exception('Unable to rollback user')
            finally:
                abort(500)
        finally:
            try:
                if(con is not None):
                    con.close()
            except mySQLException:
                log.exception('Unable to close connection')


"""****************************************************************************************************
* Description: allow to create users for the API
* INUT: user and pwd
* OUTPUT: -
****************************************************************************************************"""
class changePassword(Resource):
    # Authentication
    @auth.login_required
    def post(self):
        # Read post parameters
        username = request.form.get('user')
        password = request.form.get('pwd')

        # Create the connection
        con = None
        try:
            #Open connection
            con = dbConnectMySQL('admin')

            # Check if the username is the same that has logged in
            if(auth.username() ==  username):
                #We update the password
                
                sqlQueryUpdate = 'UPDATE users SET password=SHA2(%s,256) WHERE username = %s'

                mycursorUpdate = con.cursor(prepared=True)
                mycursorUpdate.execute(sqlQueryUpdate, (password,username))
                mycursorUpdate.close()
                con.commit()

                # Return response
                log.info(f'User {username} has changed the password')
                return {'message': f'User password changed correctly'}

            else:
                #Unable to change password, login and param doesnt match
                abort(403)

        except mySQLException:         
            try:
                if(con is not None):
                    con.rollback()
                log.exception('mySQL Exception')
            except mySQLException:
                log.exception('Unable to rollback user')
            finally:
                abort(500)
        finally:
            try:
                if(con is not None):
                    con.close()
            except mySQLException:
                log.exception('Unable to close connection')

"""****************************************************************************************************
* Daemon to delete all tmp files each 30 minutes
****************************************************************************************************"""

def deletetmp():
    os.system('find ' + app.config['UPLOAD_FOLDER'] + '/* -mmin +30 -exec rm -r {} \\;')
    

sched = BackgroundScheduler(daemon=True)
sched.add_job(deletetmp,'interval',minutes=30)
sched.start()

"""****************************************************************************************************
* Methods definition
****************************************************************************************************"""
api.add_resource(problemQueryList, '/users/problems')
api.add_resource(problemQueryListSize, '/users/problems/size')
api.add_resource(problemQuery, '/users/problem/<problem_id>')
api.add_resource(problemPDFState, '/users/problem/<problem_id>/pdfState')
api.add_resource(problemPDFFull, '/users/problem/<problem_id>/pdfFull')
api.add_resource(resourceDependency, '/users/dependency/<dependency_id>')
api.add_resource(getProblemSheet, '/users/getProblemSheet')
api.add_resource(uploadProblem, '/admin/uploadProblem')
api.add_resource(removeProblem, '/admin/removeProblem/<problem_id>')
api.add_resource(addUser, '/admin/addUser')
api.add_resource(changePassword, '/admin/changePassword')
api.add_resource(ping, '/ping')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
