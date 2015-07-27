__author__ = 'dhallman'

import os

class LanguageSource(object):

    def __init__(self, languageName, prefix, dateString, shouldSubclassUser):
        self.languageName = languageName
        self.prefix = prefix
        self.dateString = dateString
        self.shouldSubclassUser = shouldSubclassUser
        self.subclasses = []
        self.parseFieldsToSkip = ['objectId', 'ACL', 'createdAt', 'updatedAt']
        self.userFieldsToSkip = ['authData', 'email', 'emailVerified', 'username', 'password', 'role']

#############################################
# Methods to override in language subclasses
#############################################

    # Subclasses will likely call this super method first, then execute another method after completion
    def createImplementation(self, schemas=[]):
        # Create directory
        dir = os.getcwd() + '/' + self.languageName
        if not os.path.exists(dir):
            os.makedirs(dir)

        # Build list of subclasses
        subclassImportsByClass = {}

        # First iteration builds a list of all the subclasses and their cross-references to each other
        for schema in schemas:
            className = schema['className']
            isUserClass = (className == '_User')

            # Create empty array of imports
            subclassImportsByClass[className] = []

            if self.shouldSubclassUser and isUserClass:
                # Special case to subclass User
                baseName = className[1:]
                subclassName = self.prefix + baseName
            elif className.startswith('_'):
                # Skip internal Parse classes (User if not subclassing, Session, Role, Installation)
                continue
            else:
                # Custom Parse classes
                subclassName = self.prefix + className

            # Build subclass list
            self.subclasses.append(subclassName)

            # Iterate to find subclasses which need to reference/import another subclass
            for field, fieldDict in schema['fields'].iteritems():
                type = fieldDict['type']

                if type == 'Pointer':
                    typeClass = self.determineSubclassName(fieldDict['targetClass'])
                    if typeClass == None:
                        # No subclass
                        continue

                    # If not in the list, then add it
                    imports = subclassImportsByClass[className]
                    if typeClass not in imports:
                        imports.append(typeClass)

        # Second iteration creates the source code
        for schema in schemas:
            className = schema['className']
            isUserClass = (className == '_User')
            subclassImports = subclassImportsByClass[className]

            if self.shouldSubclassUser and isUserClass:
                # Special case to subclass User
                baseName = className[1:]
                subclassName = self.prefix + baseName
            elif className.startswith('_'):
                # Skip internal Parse classes (User if not subclassing, Session, Role, Installation)
                continue
            else:
                # Custom Parse classes
                subclassName = self.prefix + className

            # Create the source
            print 'Generate {} subclass {} for Parse class {}'.format(self.languageName, subclassName, className)
            self.generateSubclass(schema, parseClassName=className, subclassName=subclassName, isUserClass=isUserClass, subclassImports=subclassImports)

    # Override this method to create the source code
    def generateSubclass(self, schema, parseClassName='', subclassName='', isUserClass=False, subclassImports=[]):

        # Filename
        fileName = subclassName + '.txt'

        # Header
        source = self.generateComments(fileName)

        # Body
        source = 'Source goes here\n\n'

        # Save
        self.saveFile(fileName, source)

    # Override this method change the commented header
    def generateComments(self, fileName):
        source = '//\n'
        source += '// {}\n'.format(fileName)
        source += '//\n'
        source += '// Auto-generated by GSParseSchema on {}.\n'.format(self.dateString)
        source += '// https://github.com/Grepstar/GSParseSchema\n'
        source += '//\n\n'
        return source

##########
# Helpers
##########

    # Helper method to determine subclass name from the Parse model
    def determineSubclassName(self, className=''):
        if self.shouldSubclassUser and className == '_User':
            return self.prefix + className[1:]
        elif className.startswith('_'):
            return None
        else:
            return self.prefix + className

    def saveFile(self, fileName, source):
        # Remove old file if it exists
        filePath = self.languageName + '/' + fileName
        if os.path.exists(filePath):
            os.remove(filePath)

        # Save file
        file = open(filePath, 'w')
        file.write(source)
        file.close()

        print '\tCreated {}'.format(filePath)
