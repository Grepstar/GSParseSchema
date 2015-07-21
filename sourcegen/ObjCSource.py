__author__ = 'dhallman'

from sourcegen import LanguageSource

class ObjCSource(LanguageSource.LanguageSource):

############
# Overrides
############

    def __init__(self, prefix, dateString, shouldSubclassUser):
        super(ObjCSource, self).__init__('ObjC', prefix, dateString, shouldSubclassUser)

    def createImplementation(self, schemas=[]):
        super(ObjCSource, self).createImplementation(schemas)
        #self.generateParseExtension()

    def generateSubclass(self, schema, parseClassName='', subclassName='', isUserClass=False, subclassImports=[]):
        self.generateHeaderFile(schema, parseClassName, subclassName, isUserClass, subclassImports)
        self.generateImplementationFile(schema, parseClassName, subclassName, isUserClass, subclassImports)

############
# Helpers
############

    def generateHeaderFile(self, schema, parseClassName, subclassName, isUserClass, subclassImports):
        fileName = subclassName + '.h'

        # Source
        source = ''

        # Header
        source += self.generateComments(fileName)

        # Imports
        source += '#import <Parse/Parse.h>\n\n'

        for subclassImport in subclassImports:
            source += '@class {};\n'.format(subclassImport)

        # Inheritance
        if isUserClass:
            source += '\n@interface ' + subclassName + ' : PFUser\n\n'
        else:
            source += '\n@interface ' + subclassName + ' : PFObject<PFSubclassing>\n\n'

        source += '+ (NSString *)parseClassName;\n\n'

        for field, fieldDict in schema['fields'].iteritems():

            # Skip core fields
            if field in ['objectId', 'ACL', 'createdAt', 'updatedAt']:
                continue
            # Skip PFUser fields
            elif isUserClass and field in ['authData', 'email', 'emailVerified', 'username', 'password', 'role']:
                continue

            type = fieldDict['type']
            isPointer = True

            if type == 'String':
                languageType =  'NSString'
            elif type == 'Number':
                languageType = 'NSNumber'
            elif type == 'Boolean':
                languageType = 'BOOL'
                isPointer = False
            elif type == 'Date':
                languageType = 'NSDate'
            elif type == 'GeoPoint':
                languageType = 'PFGeoPoint'
            elif type == 'File':
                languageType = 'PFFile'
            elif type == 'Pointer':
                typeClass = self.determineSubclassName(fieldDict['targetClass'])
                languageType = typeClass
            elif type == 'Relation':
                typeClass = self.determineSubclassName(fieldDict['targetClass'])
                #languageType = '[{}]'.format(typeClass)
                languageType = 'PFRelation'
            elif type == 'Array':
                languageType = 'NSArray'
            else:
                print '\tunhandled field: {} {}'.format(field, str(fieldDict))
                continue

            # Property declaration
            if isPointer:
                source += '@property (nonatomic, strong) {} *{};\n'.format(languageType, field)
            else:
                source += '@property (nonatomic, strong) {} {};\n'.format(languageType, field)

        source += '\n@end\n\n'

        # Save
        self.saveFile(fileName, source)

    def generateImplementationFile(self, schema, parseClassName, subclassName, isUserClass, subclassImports):
        fileName = subclassName + '.m'

        # Source
        source = ''

        # Header
        source += self.generateComments(fileName)

        # Imports
        source += '#import "{}.h"\n'.format(subclassName)
        source += '#import <Parse/PFObject+Subclass.h>\n'

        for subclassImport in subclassImports:
            source += '#import "{}.h"\n'.format(subclassImport)

        # Implementation
        source += '\n@implementation ' + subclassName + '\n\n'

        for field, fieldDict in schema['fields'].iteritems():

            # Skip core fields
            if field in ['objectId', 'ACL', 'createdAt', 'updatedAt']:
                continue
            # Skip PFUser fields
            elif isUserClass and field in ['authData', 'email', 'emailVerified', 'username', 'password', 'role']:
                continue

            # Property declaration
            source += '@dynamic {};\n'.format(field)

        source += '\n@end\n\n'

        # Save
        self.saveFile(fileName, source)

    def generateParseExtension(self):
        fileName = 'Parse+Subclasses.swift'
        filePath =  self.languageName + '/' + fileName
        source = ''

        print 'Generate Parse extension {}'.format(filePath)

        source += self.generateComments(fileName)

        # Imports
        source += 'import Parse\n\n'

        # Extension
        source += 'extension Parse {\n\n'
        source += '\t// Call this function before \'Parse.setApplicationId(applicationId: String, clientKey: String)\' in your AppDelegate\n'
        source += '\tclass func registerSubclasses() {\n'

        for subclass in self.subclasses:
            source += '\t\t{}.registerSubclass()\n'.format(subclass)

        source += '\t}\n'
        source += '}'

        # Save
        self.saveFile(fileName, source)