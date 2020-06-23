"""****************************************************************************************************
* Churn functions for the rest API
* Version: 0
* Date: 18/11/2019
****************************************************************************************************"""

from connections import dbConnectMySQL
from connections import mySQLException
import saveProblemDB
import os
import time
import shutil

UPLOAD_FOLDER = 'Data/tmp'
DATA_DIRECTORY = 'Data'

"""****************************************************************************************************
* Description: method to return a list of customers sensitive to leave the company in the next year
* INPUT: -
* OUTPUT: dict object with a list of customers sensitive who might leave.
****************************************************************************************************"""


def getProblemList(con, tags, mag, prop, tamPag, pag):

    try:
        # Check tha variables to create the Query String
        sqlQueryBeginning = 'SELECT P.Id, P.Tex, P.Magazine, P.Proposer,group_concat(distinct T2.Name) as tags\
                    FROM problem as P join problem_tag as PT on P.Id=PT.Id_Problem JOIN tag as T on PT.Id_Tag=T.Id join problem_tag as PT2 on PT2.Id_Problem = P.Id JOIN tag as T2 on PT2.Id_Tag=T2.Id '
        sqlQueryWhere = ''
        sqlQueryEnd = 'GROUP BY P.Id ORDER BY COUNT(Distinct T.Id) DESC '
        sqlQueryLimit = ''
        tuple_values = ()
        if(tags or mag or prop):
            sqlQueryWhere = 'WHERE '
            if(tags):
                list_tags = tags.split(",")
                # We remove the empty tags
                list_tags = [tag for tag in list_tags if tag]
                # We set the any string before and after the tag
                list_tags = ["%" + tag + "%" for tag in list_tags]
                tuple_values = tuple_values + tuple(list_tags)
                for i in range(len(list_tags)):
                    if len(list_tags) == 1:
                        sqlQueryWhere = sqlQueryWhere + '(T.Name LIKE %s) '
                    elif i == 0:
                        sqlQueryWhere = sqlQueryWhere + '(T.Name LIKE %s '
                    elif i == len(list_tags)-1:
                        sqlQueryWhere = sqlQueryWhere + 'or T.Name LIKE %s) '
                    else:
                        sqlQueryWhere = sqlQueryWhere + 'or T.Name LIKE %s '
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

        if((tamPag or tamPag == 0) and (pag or pag == 0)):
            sqlQueryLimit = 'LIMIT %s, %s'
            tuple_values = tuple_values + (tamPag*(pag-1), tamPag)

        sqlQuery = sqlQueryBeginning + sqlQueryWhere + sqlQueryEnd + sqlQueryLimit

        # Execute the query
        mycursor = con.cursor(prepared=True)
        mycursor.execute(sqlQuery, tuple_values)
        row_headers = [x[0].lower() for x in mycursor.description]
        problems_data = mycursor.fetchall()
        json_data = []
        for problem in problems_data:
            json_data.append(
                dict(zip(row_headers, [data if not isinstance(data, bytearray) else data.decode("utf-8") if counter != len(problem)-1 else data.decode("utf-8").split(",") for counter, data in enumerate(problem)])))
            mycursor.close()

        return dict(problems=json_data)
    except mySQLException as e:
        raise e


"""****************************************************************************************************
* Description: method to return a list of customers sensitive to leave the company in the next year
* INPUT: -
* OUTPUT: dict object with a list of customers sensitive who might leave.
****************************************************************************************************"""


def getProblemListSize(con, tags, mag, prop):

    # We should try to return a JSON with the total number of results and just the pages that we really want so the pagination can be done easily.
    # This would be implemented in future versions

    try:
        # Check tha variables to create the Query String
        sqlQueryBeginning = 'SELECT count(distinct P.Id) as size\
                    FROM problem as P join problem_tag as PT on P.Id=PT.Id_Problem JOIN tag as T on PT.Id_Tag=T.Id join problem_tag as PT2 on PT2.Id_Problem = P.Id JOIN tag as T2 on PT2.Id_Tag=T2.Id '
        sqlQueryWhere = ''
        tuple_values = ()
        if(tags or mag or prop):
            sqlQueryWhere = 'WHERE '
            if(tags):
                list_tags = tags.split(",")
                # We remove the empty tags
                list_tags = [tag for tag in list_tags if tag]
                # We set the any string before and after the tag
                list_tags = ["%" + tag + "%" for tag in list_tags]
                tuple_values = tuple_values + tuple(list_tags)
                for i in range(len(list_tags)):
                    if len(list_tags) == 1:
                        sqlQueryWhere = sqlQueryWhere + '(T.Name LIKE %s) '
                    elif i == 0:
                        sqlQueryWhere = sqlQueryWhere + '(T.Name LIKE %s '
                    elif i == len(list_tags)-1:
                        sqlQueryWhere = sqlQueryWhere + 'or T.Name LIKE %s) '
                    else:
                        sqlQueryWhere = sqlQueryWhere + 'or T.Name LIKE %s '
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

        sqlQuery = sqlQueryBeginning + sqlQueryWhere

        # Execute the query
        mycursor = con.cursor(prepared=True)
        mycursor.execute(sqlQuery, tuple_values)
        result = mycursor.fetchone()
        resultDict = dict()
        if(result):
            resultDict = dict(size=result[0])
        mycursor.close()

        return resultDict
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
        sqlQuery = 'SELECT P.Id, P.Magazine, P.Tex, P.Proposer, P.Dep_State, group_concat(distinct T.Name) as tags\
                    FROM problem as P join problem_tag as PT on P.Id=PT.Id_Problem JOIN tag as T on PT.Id_Tag=T.Id\
                    WHERE P.Id = %s\
                    GROUP BY P.Id, P.Magazine, P.Tex, P.Proposer, P.Dep_State'
        # Execute the query
        mycursor = con.cursor(prepared=True)
        mycursor.execute(sqlQuery, (problem_id,))
        row_headers = [x[0].lower() for x in mycursor.description]
        problem = mycursor.fetchone()
        if(problem):
            json_data = dict(zip(row_headers, [data if not isinstance(data, bytearray) else data.decode(
                "utf-8") if counter != len(problem)-1 else data.decode("utf-8").split(",") for counter, data in enumerate(problem)]))

            # We get the solutions information for this problem
            sqlQuery2 = 'SELECT S.Id, S.Tex, S.Solver FROM solution as S WHERE S.Id_Problem = %s'

            # Execute the query
            mycursor2 = con.cursor(prepared=True)
            mycursor2.execute(sqlQuery2, (problem_id,))
            row_headers2 = [x[0].lower() for x in mycursor2.description]
            solutions_data = mycursor2.fetchall()
            json_data_solutions = []
            for solution in solutions_data:
                json_data_solutions.append(
                    dict(zip(row_headers2, [data if not isinstance(data, bytearray) else data.decode("utf-8") for data in solution])))
            mycursor2.close()

            json_data['solutions'] = json_data_solutions
        else:
            json_data = None

        mycursor.close()

        return json_data
    except mySQLException as e:
        raise e


"""****************************************************************************************************
* Description: method to return the data of a problem
* INPUT: problem_id is an integer
* OUTPUT: a dict with the data of a 
****************************************************************************************************"""


def getProblemTex(con, problem_id):

    try:
        # Tex variable
        problemTex = None
        # Check tha variables to create the Query String
        sqlQuery = 'SELECT P.Tex FROM problem as P WHERE P.Id = %s'
        # Execute the query
        mycursor = con.cursor(prepared=True)
        mycursor.execute(sqlQuery, (problem_id,))
        problem = mycursor.fetchone()
        if (problem):
            problemTex = problem[0].decode("utf-8")
        return problemTex
    except mySQLException as e:
        raise e


"""****************************************************************************************************
* Description: method to return the data of a problem
* INPUT: problem_id is an integer
* OUTPUT: a dict with the data of a 
****************************************************************************************************"""


def getSolutionTex(con, problem_id, solution_id):

    try:
        # Tex variable
        solutionTex = None
        # Check tha variables to create the Query String
        sqlQuery = 'SELECT S.Tex FROM solution as S WHERE S.Id = %s and S.Id_Problem=%s'
        # Execute the query
        mycursor = con.cursor(prepared=True)
        mycursor.execute(sqlQuery, (solution_id, problem_id))
        solution = mycursor.fetchone()
        if (solution):
            solutionTex = solution[0].decode("utf-8")
        return solutionTex
    except mySQLException as e:
        raise e


"""****************************************************************************************************
* Description: method to return the data of a problem
* INPUT: problem_id is an integer
* OUTPUT: a dict with the data of a 
****************************************************************************************************"""


def getPackagesProblem(con, problem_id):

    try:
        # Tex variable
        packages = []
        # Check tha variables to create the Query String
        sqlQuery = 'SELECT P.Name, PP.Parameter FROM problem_package as PP join package as P on PP.Id_Package=P.Id WHERE PP.Id_Problem= %s'
        # Execute the query
        mycursor = con.cursor(prepared=True)
        mycursor.execute(sqlQuery, (problem_id,))
        packages_data = mycursor.fetchall()
        for package in packages_data:
            # packages will ve a list with tuples and elements
            if(package[1]):
                packages.append(
                    (package[0].decode("utf-8"), package[1].decode("utf-8")))
            else:
                packages.append(package[0].decode("utf-8"))
        mycursor.close()

        return packages
    except mySQLException as e:
        raise e


"""****************************************************************************************************
* Description: method to return the data of a problem
* INPUT: problem_id is an integer
* OUTPUT: a dict with the data of a 
****************************************************************************************************"""


def getPackagesProblemList(con, problem_list):

    try:
        packages = []
        for problem_id in problem_list:
            packagesAux = getPackagesProblem(con, problem_id)
            packages = list(set(packages + packagesAux))
        return packages
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

        # Execute the query
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

        # Execute the query
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


def getDependency(con, dependency_id):

    try:
        # Check tha variables to create the Query String
        sqlQuery = 'SELECT D.URL FROM dependency as D WHERE D.Id = %s'

        # Execute the query
        mycursor = con.cursor(prepared=True)
        mycursor.execute(sqlQuery, (dependency_id,))
        image_data = mycursor.fetchone()
        mycursor.close()

        url = None
        if(image_data):
            url = image_data[0].decode("utf-8")
            # We return images in this method
            if(url.rsplit('.', 1)[1].lower() == 'pdf'):
                url = url.rsplit('.', 1)[0] + '.svg'

        return url
    except mySQLException as e:
        raise e

"""****************************************************************************************************
* Description: method to return the bills of a client
* INPUT: customer id
* OUTPUT: a JSON with the data client
****************************************************************************************************"""


def saveProblem(con, absoluteURL, solutionsData, tags, mag, prop):

    try:

        con.start_transaction()

        # We save the statement
        dictSavedStatement = saveProblemDB.saveStatementDB(
            con, absoluteURL, tags, mag, prop)

        if dictSavedStatement:
            listDictSavedSolu = []
            for solutionDict in solutionsData:
                listDictSavedSolu.append(saveProblemDB.saveSolutionDB(con, solutionDict['solutionURL'], str(
                    dictSavedStatement['idProblem']), solutionDict['solver']))

            if listDictSavedSolu:

                # Now we compile the statement
                urlNewTexStatementPDF = dictSavedStatement['URL_PDF_State'].rsplit('.', 1)[
                    0] + '.tex'
                statementTex = dictSavedStatement['texProblem']

                newTexFileStatementPDF = open(urlNewTexStatementPDF, "w+")

                # We start the document
                newTexFileStatementPDF.write(
                    '\\documentclass[12pt]{article}\n')

                # We write the packages

                if(dictSavedStatement['packagesWithOptions']):
                    for tuplePackage in dictSavedStatement['packagesWithOptions']:
                        newTexFileStatementPDF.write(
                            '\\usepackage[' + tuplePackage[0] + ']{' + tuplePackage[1] + '}\n')

                if(dictSavedStatement['packagesWithoutOptions']):
                    for package in dictSavedStatement['packagesWithoutOptions']:
                        newTexFileStatementPDF.write(
                            '\\usepackage{' + package + '}\n')

                # We state the styles directives
                newTexFileStatementPDF.write('\\setlength{\\parindent}{0pt}\n')

                # We start the statement
                newTexFileStatementPDF.write('\\begin{document}\n')

                # First the data of the problem this just goes into the pdf
                newTexFileStatementPDF.write(
                    '\\textbf{PROBLEMA ' + str(dictSavedStatement['idProblem']) + '} ')
                if(prop):
                    newTexFileStatementPDF.write(
                        '\\textit{Propuesto por ' + prop + '}')
                if(mag):
                    newTexFileStatementPDF.write(
                        '\\textit{Publicado en ' + mag + '}')
                newTexFileStatementPDF.write('\\medskip \n')

                # We write the statement
                newTexFileStatementPDF.write(statementTex + '\n')

                # We end the document
                newTexFileStatementPDF.write('\\end{document}')
                newTexFileStatementPDF.flush()
                newTexFileStatementPDF.close()

                # We compile the new .tex for the pdf
                # We compile it twice just in case we need some references
                cliCompile = 'pdflatex -interaction batchmode -halt-on-error -jobname=' + \
                    dictSavedStatement['URL_PDF_State'].rsplit(
                        '.', 1)[0] + ' ' + urlNewTexStatementPDF
                os.system(cliCompile)
                resultStatement = os.system(cliCompile)
                errorCodeStatement = resultStatement >> 8

                # We delete the aux .tex files
                os.remove(urlNewTexStatementPDF)

                # Now we compile the statement with the solutions
                # For that we must create a new tex
                urlNewTex = dictSavedStatement['URL_PDF_Full'].rsplit('.', 1)[
                    0] + '.tex'
                statementTex = dictSavedStatement['texProblem']
                newTexFileFull = open(urlNewTex, "w+")

                # We start the document
                newTexFileFull.write('\\documentclass[12pt]{article}\n')

                # We write the packages

                if(dictSavedStatement['packagesWithOptions']):
                    for tuplePackage in dictSavedStatement['packagesWithOptions']:
                        newTexFileFull.write(
                            '\\usepackage[' + tuplePackage[0] + ']{' + tuplePackage[1] + '}\n')

                if(dictSavedStatement['packagesWithoutOptions']):
                    for package in dictSavedStatement['packagesWithoutOptions']:
                        newTexFileFull.write('\\usepackage{' + package + '}\n')

                # We state the styles directives
                newTexFileFull.write('\\setlength{\\parindent}{0pt}\n')

                # We write the statement
                newTexFileFull.write('\\begin{document}\n')

                # First the data of the problem
                newTexFileFull.write(
                    '\\textbf{PROBLEMA ' + str(dictSavedStatement['idProblem']) + '} ')
                if(prop):
                    newTexFileFull.write(
                        '\\textit{Propuesto por ' + prop + '}')
                if(mag):
                    newTexFileFull.write('\\textit{Publicado en ' + mag + '}')
                newTexFileFull.write('\\medskip \n')

                newTexFileFull.write(statementTex + '\n')

                # We write each solution          
                for counter, DictSavedSolu in enumerate(listDictSavedSolu):

                    # We write the solution 
                    solutionTex = DictSavedSolu['texSolu']
                    solver = DictSavedSolu['solver']
                    newTexFileFull.write(
                        '\\textbf{Solución ' + str(counter+1) + '.}')
                    if(solver):
                        newTexFileFull.write(
                            '\\textit{ Enviada por: ' + solver + '}')
                    newTexFileFull.write('\\newline\n')
                    newTexFileFull.write(solutionTex)
                    newTexFileFull.write('\\\\\n')

                # We end the main document
                newTexFileFull.write('\\end{document}')
                newTexFileFull.flush()
                newTexFileFull.close()

                # We compile the new .tex
                # We compile it twice just in case we need some references
                cliCompile = 'pdflatex -interaction batchmode -halt-on-error -jobname=' + \
                    dictSavedStatement['URL_PDF_Full'].rsplit(
                        '.', 1)[0] + ' ' + urlNewTex
                os.system(cliCompile)
                resultFull = os.system(cliCompile)
                errorCodeFull =  resultFull >> 8

                # We delete the aux .tex
                os.remove(urlNewTex)

                # We remove the files
                for DictSavedSolu in listDictSavedSolu:
                    os.remove(DictSavedSolu['absoluteURLSolution'])

                os.remove(dictSavedStatement['absoluteURL'])

                if(errorCodeStatement == 0 and errorCodeFull == 0):
                    con.commit()
                    return True
                else:
                    # We delete the folder
                    shutil.rmtree(os.path.join(DATA_DIRECTORY, str(
                        dictSavedStatement['idProblem'])))

                    # We delete the posible dependencies
                    # Note: this can be done because we state the transaction level as read uncommitted just in this place
                    sqlQuerySelectDependencies = 'SELECT D.url FROM dependency as D LEFT JOIN solution as S ON Id_solu=S.Id WHERE D.Id_Problem = %s OR S.Id_Problem = %s'

                    # Execute the query
                    cursorSelectDependencies = con.cursor(prepared=True)
                    cursorSelectDependencies.execute(
                        "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
                    cursorSelectDependencies.execute(sqlQuerySelectDependencies, (
                        dictSavedStatement['idProblem'], dictSavedStatement['idProblem']))
                    dependencies_data = cursorSelectDependencies.fetchall()
                    for dependency in dependencies_data:
                        dep_url = dependency[0].decode("utf-8")
                        # If the extension is .pdf then it must exist an svg
                        if(dep_url.rsplit('.', 1)[1].lower() == 'pdf'):
                            dep_url_svg = dep_url.rsplit('.', 1)[0] + '.svg'
                            os.remove(dep_url)
                            os.remove(dep_url_svg)
                        else:
                            os.remove(dep_url)
                    cursorSelectDependencies.close()
        con.rollback()
        return False
    except mySQLException as e:
        con.rollback()
        raise e


"""****************************************************************************************************
* Description: method to return the bills of a client
* INPUT: customer id
* OUTPUT: a JSON with the data client
****************************************************************************************************"""


def deleteProblem(con, problem_id):

    try:

        con.start_transaction()

        # First we delete the dependencies
        sqlQuerySelectDependencies = 'SELECT D.url FROM dependency as D LEFT JOIN solution as S ON Id_solu=S.Id WHERE D.Id_Problem = %s OR S.Id_Problem = %s'

        # Execute the query
        cursorSelectDependencies = con.cursor(prepared=True)
        cursorSelectDependencies.execute(
            sqlQuerySelectDependencies, (problem_id, problem_id))
        dependencies_data = cursorSelectDependencies.fetchall()
        for dependency in dependencies_data:
            dep_url = dependency[0].decode("utf-8")
            # If the extension is .pdf then it must exist an svg
            if(dep_url.rsplit('.', 1)[1].lower() == 'pdf'):
                dep_url_svg = dep_url.rsplit('.', 1)[0] + '.svg'
                os.remove(dep_url)
                os.remove(dep_url_svg)
            else:
                os.remove(dep_url)
        cursorSelectDependencies.close()

        # We delete the dependencies from the database
        sqlQueryDeleteDependencies = 'DELETE D FROM dependency as D LEFT JOIN solution as S ON Id_solu=S.Id WHERE D.Id_Problem = %s OR S.Id_Problem = %s'

        # Execute the query
        cursorDeleteDependencies = con.cursor(prepared=True)
        cursorDeleteDependencies.execute(
            sqlQueryDeleteDependencies, (problem_id, problem_id))
        cursorDeleteDependencies.close()

        # We delete the solutions
        sqlQueryDeleteSolutions = 'DELETE FROM solution WHERE Id_Problem = %s'

        # Execute the query
        cursorDeleteSolutions = con.cursor(prepared=True)
        cursorDeleteSolutions.execute(sqlQueryDeleteSolutions, (problem_id,))
        cursorDeleteSolutions.close()

        # We delete the tags
        sqlQueryDeleteTags = 'DELETE FROM problem_tag WHERE Id_Problem = %s'

        # Execute the query
        cursorDeleteTags = con.cursor(prepared=True)
        cursorDeleteTags.execute(sqlQueryDeleteTags, (problem_id,))
        cursorDeleteTags.close()

        # We delete the tags
        sqlQueryDeletePackage = 'DELETE FROM problem_package WHERE Id_Problem = %s'

        # Execute the query
        cursorDeletePackage = con.cursor(prepared=True)
        cursorDeletePackage.execute(sqlQueryDeletePackage, (problem_id,))
        cursorDeletePackage.close()

        # We remove the folder of the problem inside the Data folder
        shutil.rmtree(os.path.join(DATA_DIRECTORY, str(problem_id)))

        # We delete the problem from the database
        sqlQueryDeleteProblem = 'DELETE FROM problem WHERE Id= %s'

        # Execute the query
        cursorDeleteProblem = con.cursor(prepared=True)
        cursorDeleteProblem.execute(sqlQueryDeleteProblem, (problem_id,))
        cursorDeleteProblem.close()

        con.commit()

        return f'The problem {problem_id} was deleted correctly.'

    except mySQLException as e:
        con.rollback()
        raise e


"""****************************************************************************************************
* Description: method to return the bills of a client
* INPUT: customer id
* OUTPUT: a JSON with the data client
****************************************************************************************************"""


def getProblemSheet(con, dictionaryProblems):

    try:
        numProblems = int(len(dictionaryProblems)/2)
        problems_id = []
        keysP = list(filter(lambda x: x.startswith(
            'problem'), dictionaryProblems.keys()))
        for keyProblem in keysP:
            problems_id.append(dictionaryProblems.get(keyProblem))

        # We get the packages needed for the document
        packages = getPackagesProblemList(con, problems_id)

        # We must create a new tex
        timeStampMark = str('{:2f}'.format(
            time.time()*100000000)).split('.')[0]
        filename = timeStampMark + 'userPDF.tex'
        urlNewTex = os.path.join(UPLOAD_FOLDER, filename)
        newTexFile = open(urlNewTex, "w+")

        # We start the document
        newTexFile.write('\\documentclass[12pt]{article}\n')

        # We write the packages
        for package in packages:
            if type(package) == tuple:
                newTexFile.write(
                    '\\usepackage[' + package[1] + ']{' + package[0] + '}\n')
            else:
                newTexFile.write('\\usepackage{' + package + '}\n')

        # We state the title
        newTexFile.write('\\title{\\sf\\bfseries \\large Hoja de problemas. Generada con ProbleMath}\n')

        # We start the document
        newTexFile.write('\\begin{document}\n')

        # We set the styling for the page problem
        newTexFile.write('\\frenchspacing\n')
        newTexFile.write('\\maketitle\n')
        #newTexFile.write('\\medskip\n')
        #newTexFile.write('\\hrule\n')
        #newTexFile.write('\\bigskip\n')
        #newTexFile.write('\\vskip.5cm\n')
        newTexFile.write('\\newcounter{ejem}\n')
        newTexFile.write('\\begin{list}{\\sf\\bfseries\\arabic{ejem}.}\n')
        newTexFile.write('{\\usecounter{ejem}\\leftmargin 0pt}\n')

        for n in range(1, numProblems+1):
            # We get the problem id
            problem_id = dictionaryProblems.get('problem'+str(n))

            # we get the tex from the database
            auxTex = getProblemTex(con, problem_id)

            # We write the problem in if it exits
            if(auxTex):
                newTexFile.write('\\item ' + auxTex + '\n')

            # We get the solutions id
            solution_ids = dictionaryProblems.get('solution'+str(n))
            solutionIdList = solution_ids.split(',')

            # We get the solutions tex and write them
            solutionsCounter = 1
            for solution_id in solutionIdList:

                # We get the tex from the database
                auxTex = getSolutionTex(con, problem_id, solution_id)

                # We write the solution
                if(auxTex):
                    newTexFile.write(
                        '\\emph{Solución ' + str(solutionsCounter) + '.}\\\\\n')
                    newTexFile.write(auxTex + '\n')
                    newTexFile.write('\\medskip')
                    solutionsCounter = solutionsCounter + 1

        # We end the document
        newTexFile.write('\\end{list}\n')
        newTexFile.write('\\end{document}')
        newTexFile.flush()
        newTexFile.close()

        # We compile the new .tex

        cliCompile = 'pdflatex -interaction batchmode -halt-on-error -jobname=' + \
            urlNewTex.rsplit('.', 1)[0] + ' ' + urlNewTex
        os.system(cliCompile)
        result = os.system(cliCompile)
        errorCode = result >> 8

        # We delete the aux .tex
        rmAuxTex = 'rm ' + urlNewTex
        os.system(rmAuxTex)

        return urlNewTex.rsplit('.', 1)[0]+'.pdf' if errorCode == 0 else None

    except mySQLException as e:
        raise e
