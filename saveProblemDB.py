"""****************************************************************************************************
* Functions that saves statements and solutions in the database
* Version: 0
* Date: 23/04/2020
****************************************************************************************************"""

from connections import dbConnectMySQL
from connections import mySQLException
from werkzeug.utils import secure_filename
import os
import subprocess
import time
import re

DATA_DIRECTORY = 'Data'
DP_DIRECTORY = 'Data/dp'
UPLOAD_FOLDER = 'Data/tmp'

"""****************************************************************************************************
* Description: method to save a statement of a problem into the database 
* INPUT: -
* OUTPUT: true if it has been saved correctly, no in other case
****************************************************************************************************"""


def saveStatementDB(con, absoluteURL, tags, mag, prop):

    try:

        extension = absoluteURL.rsplit('.', 1)[1].lower()
        dirName = absoluteURL.rsplit('.', 1)[0]
        texStatement = ''

        if extension == 'zip':
            os.system('unzip -d '+dirName + ' ' + absoluteURL)
            ps = subprocess.Popen(('ls', dirName), stdout=subprocess.PIPE)
            nameTexFile = subprocess.check_output(
                ('grep', '.tex$'), stdin=ps.stdout).decode("utf-8").rstrip()
            ps.wait()

            # Delete the zip zile
            os.remove(absoluteURL)

            # We move the tex to the tmp folder with a new name
            timeStampMark = str('{:2f}'.format(
                time.time()*100000000)).split('.')[0]
            filename = timeStampMark + secure_filename(nameTexFile)
            absoluteURL = os.path.join(UPLOAD_FOLDER, filename)
            os.rename(os.path.join(dirName, nameTexFile), absoluteURL)

            # We mark that the statement has dependencies
            dep = 1

            # We get the rest of the files
            oldPaths = []
            oldRelativePaths = []
            # r=root, _=directories, f = files
            for r, _, f in os.walk(dirName):
                for file in f:
                    oldPaths.append(os.path.join(r, file))
                    oldRelativePaths.append(file)

            newPaths = saveDependenciesDB(con, oldPaths)

            # We remove the directory that right now it's empty
            os.removedirs(dirName)

            # We must edit the tex file
            # Read in the file to get the tex inside the document and the packages
            file = open(absoluteURL, "r")
            texStatement = file.read()
            file.close()

            # Replace the paths
            for oldRelativePath, newPath in zip(oldRelativePaths, newPaths):
                oldRelativePathExt = oldRelativePath.split(".", 1)[1]
                oldRelativePathName = oldRelativePath.split(".", 1)[0]

                print(oldRelativePathName)
                print(oldRelativePathExt)

                regexReplace1 = r'\{.*?' + re.escape(
                    oldRelativePathName) + r'\.' + re.escape(oldRelativePathExt) + r'.*?\}'
                regexReplace2 = r'\{.*?' + \
                    re.escape(oldRelativePathName) + r'.*?\}'

                print(regexReplace1)
                print(regexReplace2)

                print(newPath)

                texStatement = re.sub(
                    regexReplace1, '{' + newPath + '}', texStatement)
                texStatement = re.sub(
                    regexReplace2, '{' + newPath + '}', texStatement)

        else:
            dep = 0

        # Check tha variables to create the Query String
        sqlQueryBeginningStatement = 'INSERT INTO problem (Tex, URL_PDF_State, URL_PDF_Full, Dep_State'
        sqlQueryValues = 'VALUES (%s, %s, %s, %s'
        tupleValuesStatement = ()

        # We read the file
        if(not texStatement):
            file = open(absoluteURL, "r")
            texStatement = file.read()
            file.close()

        # From the tex we must get que packages

        headerLines = texStatement[:texStatement.find(
            '\\begin{document}')].splitlines()
        packagesWithoutOptions = []
        packagesWithOptions = []

        for line in headerLines:
            # We remove evrything that has been commented in the tex and find the packages

            packAux = re.findall(
                r'\\usepackage\{(.*?)\}', line[:line.find('%') if line.find('%') != -1 else len(line)])
            if(packAux):
                packagesWithoutOptions = list(
                    set(packagesWithoutOptions + packAux))

            packAux = re.findall(
                r'\\usepackage\[(.*?)\]\{(.*?)\}', line[:line.find('%') if line.find('%') != -1 else len(line)])
            if(packAux):
                packagesWithOptions = list(set(packagesWithOptions + packAux))

        # We get just the tex between the begin and end document tags
        texStatementLines = texStatement[texStatement.find(
            '\\begin{document}') + len('\\begin{document}'):texStatement.find('\\end{document}')].splitlines()
        texStatement = ''

        #We remove the comments
        for line in texStatementLines:
            if line.find('%') == -1 :
                texStatement = texStatement + line + '\n'
            elif line.find('/%') != -1:
                texStatement =  texStatement + line[:line.find('%')] + '\n'
            elif line.find('%') != 0:
                indexComment = 0
                allMatches = [m.start() for m in re.finditer('%', line)]
                for match in allMatches:
                    if line[match-1] != '/':
                        indexComment = match
                        break
                if indexComment == 0:
                    texStatement = texStatement + line + '\n'
                else:
                    texStatement =  texStatement + line[:indexComment] + '\n'

        tupleValuesStatement = tupleValuesStatement + \
            (texStatement, 'placeholder', 'placeholder', dep)

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
            list_tags = [x.strip() for x in tags.split(',')]
            sqlQueryFindTag = 'SELECT Id FROM tag WHERE Name = %s '
            sqlQueryNewTags = 'INSERT INTO tag (Name) VALUES (%s)'
            sqlQueryTags = 'INSERT INTO problem_tag (Id_Problem,Id_Tag) VALUES (%s,%s)'
            for tag in list_tags:
                if(tag):
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

        # We add the packages to the database
        mycursorFindPackage = con.cursor(prepared=True)
        mycursorNewPackage = con.cursor(prepared=True)
        mycursorPackages = con.cursor(prepared=True)

        if (packagesWithoutOptions or packagesWithOptions):
            sqlQueryFindPackage = 'SELECT Id FROM package WHERE Name = %s '
            sqlQueryNewPackage = 'INSERT INTO package (Name) VALUES (%s)'
            sqlQueryPackages = 'INSERT INTO problem_package (Id_Problem,Id_Package,Parameter) VALUES (%s,%s,%s)'

            for package in packagesWithoutOptions:
                idPackage = None
                mycursorFindPackage.execute(sqlQueryFindPackage, (package,))
                row = mycursorFindPackage.fetchone()
                if row is None:
                    mycursorNewPackage.execute(sqlQueryNewPackage, (package,))
                    idPackage = mycursorNewPackage.lastrowid
                else:
                    idPackage = row[0]
                mycursorPackages.execute(
                    sqlQueryPackages, (idProblem, idPackage, None))

            for packageTuple in packagesWithOptions:
                idPackage = None
                mycursorFindPackage.execute(
                    sqlQueryFindPackage, (packageTuple[1],))
                row = mycursorFindPackage.fetchone()
                if row is None:
                    mycursorNewPackage.execute(
                        sqlQueryNewPackage, (packageTuple[1],))
                    idPackage = mycursorNewPackage.lastrowid
                else:
                    idPackage = row[0]
                mycursorPackages.execute(
                    sqlQueryPackages, (idProblem, idPackage, packageTuple[0]))

        mycursorFindPackage.close()
        mycursorNewPackage.close()
        mycursorPackages.close()

        # We must update the dependency table to update the foreign keys
        if(dep == 1):
            mycursorUpdateDependencies = con.cursor(prepared=True)
            sqlQueryUpdateDependencies = 'UPDATE dependency SET Id_Problem=%s WHERE id=%s'
            for path in newPaths:
                _, filename = os.path.split(path)
                idDep = filename.split('.', 1)[0]
                mycursorUpdateDependencies.execute(
                    sqlQueryUpdateDependencies, (idProblem, idDep))

        return dict(idProblem=idProblem, absoluteURL=absoluteURL, URL_PDF_State=URL_PDF_State,
                    URL_PDF_Full=URL_PDF_Full, texProblem=texStatement, packagesWithoutOptions=packagesWithoutOptions,
                    packagesWithOptions=packagesWithOptions)

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

        extension = absoluteURLSolution.rsplit('.', 1)[1].lower()
        dirName = absoluteURLSolution.rsplit('.', 1)[0]
        texSolu = ''

        if extension == 'zip':
            os.system('unzip -d '+dirName + ' ' + absoluteURLSolution)
            ps = subprocess.Popen(('ls', dirName), stdout=subprocess.PIPE)
            nameTexFile = subprocess.check_output(
                ('grep', '.tex$'), stdin=ps.stdout).decode("utf-8").rstrip()
            ps.wait()

            # Delete the zip zile
            os.remove(absoluteURLSolution)

            # We move the tex to the tmp folder with a new name
            timeStampMark = str('{:2f}'.format(
                time.time()*100000000)).split('.')[0]
            filename = timeStampMark + secure_filename(nameTexFile)
            absoluteURLSolution = os.path.join(UPLOAD_FOLDER, filename)
            os.rename(os.path.join(dirName, nameTexFile), absoluteURLSolution)

            # We mark that the statement has dependencies
            dep = 1

            # We get the rest of the files
            oldPaths = []
            oldRelativePaths = []
            # r=root, _=directories, f = files
            for r, _, f in os.walk(dirName):
                for file in f:
                    oldPaths.append(os.path.join(r, file))
                    oldRelativePaths.append(file)

            newPaths = saveDependenciesDB(con, oldPaths)

            # We remove the directory that right now it's empty
            os.removedirs(dirName)

            # We must edit the tex file
            # Read in the file to get the tex inside the document and the packages
            file = open(absoluteURLSolution, "r")
            texSolu = file.read()
            file.close()

            # Replace the paths
            for oldRelativePath, newPath in zip(oldRelativePaths, newPaths):
                oldRelativePathExt = oldRelativePath.split(".", 1)[1]
                oldRelativePathName = oldRelativePath.split(".", 1)[0]

                regexReplace1 = r'\{.*?' + re.escape(
                    oldRelativePathName) + r'\.' + re.escape(oldRelativePathExt) + r'.*?\}'
                regexReplace2 = r'\{.*?' + \
                    re.escape(oldRelativePathName) + r'.*?\}'

                texSolu = re.sub(regexReplace1, '{' + newPath + '}', texSolu)
                texSolu = re.sub(regexReplace2, '{' + newPath + '}', texSolu)

        else:
            dep = 0

        # Check tha variables to create the Query String
        sqlQueryBeginningSolu = 'INSERT INTO solution (Id_Problem, Tex, Dep_Solu'
        sqlQueryValuesSolu = 'VALUES (%s, %s, %s'
        tupleValuesSolu = ()

        # We read the file
        if(not texSolu):
            file = open(absoluteURLSolution, "r")
            texSolu = file.read()
            file.close()

        # We get just the tex between the begin and end document tags
        texSoluLines = texSolu[texSolu.find(
            '\\begin{document}') + len('\\begin{document}'):texSolu.find('\\end{document}')].splitlines()     
        texSolu = ''
        #We remove the comments
        for line in texSoluLines:
            print(line + '\n')
            if line.find('%') == -1 :
                texSolu = texSolu + line + '\n'
            elif line.find('/%') != -1:
                texSolu =  texSolu + line[:line.find('%')] + '\n'
            elif line.find('%') != 0:
                indexComment = 0
                allMatches = [m.start() for m in re.finditer('%', line)]
                for match in allMatches:
                    if line[match-1] != '/':
                        indexComment = match
                        break
                if indexComment == 0:
                    texSolu = texSolu + line + '\n'
                else:
                    texSolu =  texSolu + line[:indexComment] + '\n'

        print('************************************************************************')
        print(texSolu + '\r\n')
        print('************************************************************************')

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

        # We must update the dependency table to update the foreign keys
        if(dep == 1):
            mycursorUpdateDependencies = con.cursor(prepared=True)
            sqlQueryUpdateDependencies = 'UPDATE dependency SET Id_Solu=%s WHERE id=%s'
            for path in newPaths:
                _, filename = os.path.split(path)
                idDep = filename.split('.', 1)[0]
                mycursorUpdateDependencies.execute(
                    sqlQueryUpdateDependencies, (idSolu, idDep))

        return dict(idSolu=idSolu, texSolu=texSolu, absoluteURLSolution=absoluteURLSolution)

    except mySQLException as e:
        con.rollback()
        raise e


"""****************************************************************************************************
* Description: method to save a statement of a problem into the database 
* INPUT: -
* OUTPUT: true if it has been saved correctly, no in other case
****************************************************************************************************"""


def saveDependenciesDB(con, paths):

    try:
        newPaths = []

        mycursorInsert = con.cursor(prepared=True)
        mycursorUpdate = con.cursor(prepared=True)
        sqlQueryInsert = 'INSERT INTO dependency (URL) VALUES (%s)'
        sqlQueryUpdate = 'UPDATE dependency SET URL=%s WHERE id=%s'

        for filePath in paths:
            fileExtension = filePath.rsplit('.', 1)[1].lower()

            # if(fileExtension=='pdf'):
            #     fileExtension='png'
            #     oldFilePath = filePath
            #     filePath = filePath.rsplit('.', 1)[0]+'.png'

            #     #We use this variable because pdftoppm rename that way the png
            #     auxfilePath = filePath.rsplit('.', 1)[0]+'-1.png'

            #     os.system('pdftoppm ' + oldFilePath + ' ' + filePath.rsplit('.', 1)[0] +' -png')
            #     os.rename(auxfilePath, filePath)
            #     os.remove(oldFilePath)

            mycursorInsert.execute(sqlQueryInsert, (filePath,))
            idDep = mycursorInsert.lastrowid

            # Rename path
            newPath = os.path.join(
                DP_DIRECTORY, str(idDep) + '.' + fileExtension)
            mycursorUpdate.execute(sqlQueryUpdate, (newPath, idDep))
            newPaths.append(newPath)

            # Move the file to its new location
            os.rename(filePath, newPath)

            # And if it's a pdf we create also a svg for the html visualization
            os.system('pdf2svg ' + newPath + ' ' +
                      newPath.rsplit('.', 1)[0] + '.svg')

        mycursorInsert.close()
        mycursorUpdate.close()

        return newPaths

    except mySQLException as e:
        con.rollback()
        raise e
