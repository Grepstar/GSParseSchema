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
        self.generateSubclassRegistration()
        self.generateModelsHeader()

    def generateSubclass(self, schema, parseClassName='', subclassName='', isUserClass=False, subclassImports=[]):
        self.generateHeaderFile(schema, parseClassName, subclassName, isUserClass, subclassImports)
        self.generateImplementationFile(schema, parseClassName, subclassName, isUserClass, subclassImports)

############
# Helpers
############

    def generateHeaderFile(self, schema, parseClassName, subclassName, isUserClass, subclassImports):
        fileName = subclassName + '.h'

        # Header
        source = self.generateComments(fileName)

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
                source += '@property (nonatomic, assign) {} {};\n'.format(languageType, field)

        source += '\n@end\n\n'

        # Save
        self.saveFile(fileName, source)

    def generateImplementationFile(self, schema, parseClassName, subclassName, isUserClass, subclassImports):
        fileName = subclassName + '.m'

        # Header
        source = self.generateComments(fileName)

        # Imports
        source += '#import "{}.h"\n'.format(subclassName)
        source += '#import <Parse/PFObject+Subclass.h>\n'

        for subclassImport in subclassImports:
            source += '#import "{}.h"\n'.format(subclassImport)

        # Implementation
        source += '\n@implementation ' + subclassName + '\n\n'

        # Register subclass
        source += '+ (void)load {\n'
        source += '\t[self registerSubclass];\n'
        source += '}\n\n'

        # Parse Subclassing
        source += '+ (NSString *)parseClassName {\n'
        source += '\treturn @"{}";\n'.format(parseClassName)
        source += '}\n\n'

        # Properties
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

    def generateSubclassRegistration(self):
        print 'Skip Subclass Registration file... is it needed?'
        # TODO
        return

        fileName = 'Parse+Subclasses.h'
        filePath =  self.languageName + '/' + fileName
        source = self.generateComments(fileName)

        # Save
        self.saveFile(fileName, source)

    def generateModelsHeader(self):
        print 'Generate Models Header'

        fileName = '{}Models.h'.format(self.prefix)
        filePath =  self.languageName + '/' + fileName
        source = self.generateComments(fileName)

        for subclass in self.subclasses:
            source += '#import "{}.h"\n'.format(subclass)

        # Save
        self.saveFile(fileName, source)