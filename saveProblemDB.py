"""****************************************************************************************************
* Functions that saves statements and solutions in the database
* Version: 0
* Date: 23/04/2020
****************************************************************************************************"""

from connections import dbConnectMySQL
from connections import mySQLException

DATA_DIRECTORY = 'Data'

"""****************************************************************************************************
* Description: method to save a statement of a problem into the database 
* INPUT: -
* OUTPUT: true if it has been saved correctly, no in other case
****************************************************************************************************"""


def saveStatementDB(con, absoluteURL, tags, mag, prop):

    try:

        # Check tha variables to create the Query String
        sqlQueryBeginningStatement = 'INSERT INTO problem (Tex, URL_PDF_State, URL_PDF_Full, Dep_State'
        sqlQueryValues = 'VALUES (%s, %s, %s, %s'
        tupleValuesStatement = ()

        # We read the file
        file = open(absoluteURL, "r")
        texStatement = file.read()
        file.close()

        tupleValuesStatement = tupleValuesStatement + \
            (texStatement, 'placeholder', 'placeholder', 0)

        if(mag):
            sqlQueryBeginningStatement = sqlQueryBeginningStatement + ', Magazine'
            sqlQueryValues = sqlQueryValues + ', %s'
            tupleValuesStatement = tupleValuesStatement + (mag,)
        if(prop):
            sqlQueryBeginningStatement = sqlQueryBeginningStatement + ', Proposer'
            sqlQueryValues = sqlQueryValues + ', %s'
            tupleValuesStatement = tupleValuesStatement + (prop,)

        sqlQueryBeginningStatement = sqlQueryBeginningStatement + ') '
        sqlQueryValues = sqlQueryValues + ')'

        sqlQueryStatement = sqlQueryBeginningStatement + sqlQueryValues

        # Execute the query
        mycursorStatement = con.cursor(prepared=True)
        mycursorStatement.execute(sqlQueryStatement, tupleValuesStatement)
        idProblem = mycursorStatement.lastrowid
        mycursorStatement.close()

        # We update the placeholders
        mycursorUpdate = con.cursor(prepared=True)
        sqlQueryUpdate = 'UPDATE problem SET URL_PDF_State=%s, URL_PDF_Full=%s WHERE id=%s'
        URL_PDF_State = DATA_DIRECTORY+'/'+str(idProblem)+'/pdfState.pdf'
        URL_PDF_Full = DATA_DIRECTORY+'/'+str(idProblem)+'/pdfFull.pdf'
        tupleValuesUpdate = (URL_PDF_State, URL_PDF_Full, idProblem)
        mycursorUpdate.execute(sqlQueryUpdate, tupleValuesUpdate)
        mycursorUpdate.close()

        # We add the tags to the database
        mycursorFindTag = con.cursor(prepared=True)
        mycursorNewTag = con.cursor(prepared=True)
        mycursorTags = con.cursor(prepared=True)

        if(tags):
            list_tags = tags.split(",")
            sqlQueryFindTag = 'SELECT Id FROM tag WHERE Name = %s '
            sqlQueryNewTags = 'INSERT INTO tag (Name) VALUES (%s)'
            sqlQueryTags = 'INSERT INTO problem_tag (Id_Problem,Id_Tag) VALUES (%s,%s)'
            for tag in list_tags:
                idTag = None
                mycursorFindTag.execute(sqlQueryFindTag, (tag,))
                row = mycursorFindTag.fetchone()
                if row is None:
                    mycursorNewTag.execute(sqlQueryNewTags, (tag,))
                    idTag = mycursorNewTag.lastrowid
                else:
                    idTag = row[0]
                mycursorTags.execute(sqlQueryTags, (idProblem, idTag))

        mycursorFindTag.close()
        mycursorNewTag.close()
        mycursorTags.close()

        return dict(idProblem=idProblem, URL_PDF_State=URL_PDF_State, URL_PDF_Full=URL_PDF_Full, texProblem=texStatement)

    except mySQLException as e:
        con.rollback()
        raise e


"""****************************************************************************************************
* Description: method to save a solution to a problem into the database 
* INPUT: -
* OUTPUT: true if it has been saved correctly, no in other case
****************************************************************************************************"""


def saveSolutionDB(con, absoluteURLSolution, idProblem, solver):

    try:

        # Check tha variables to create the Query String
        sqlQueryBeginningSolu = 'INSERT INTO solution (Id_Problem, Tex, Dep_Solu'
        sqlQueryValuesSolu = 'VALUES (%s, %s, %s'
        tupleValuesSolu = ()

        # We read the file
        file = open(absoluteURLSolution, "r")
        texSolu = file.read()
        file.close()

        # We get just the tex between the begin and end document tags
        texSolu = texSolu[texSolu.find(
            '\\begin{document}') + len('\\begin{document}'):texSolu.find('\\end{document}')]

        tupleValuesSolu = tupleValuesSolu + (idProblem, texSolu, 0)

        if(solver):
            sqlQueryBeginningSolu = sqlQueryBeginningSolu + ', Solver'
            sqlQueryValuesSolu = sqlQueryValuesSolu + ', %s'
            tupleValuesSolu = tupleValuesSolu + (solver,)

        sqlQueryBeginningSolu = sqlQueryBeginningSolu + ') '
        sqlQueryValuesSolu = sqlQueryValuesSolu + ')'

        sqlQueryProblem = sqlQueryBeginningSolu + sqlQueryValuesSolu

        # Execute the query
        mycursorSolu = con.cursor(prepared=True)
        mycursorSolu.execute(sqlQueryProblem, tupleValuesSolu)
        idSolu = mycursorSolu.lastrowid
        mycursorSolu.close()

        # We commit the changes

        return dict(idSolu=idSolu, texSolu=texSolu)

    except mySQLException as e:
        con.rollback()
        raise e
