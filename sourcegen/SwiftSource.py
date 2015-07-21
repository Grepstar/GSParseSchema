__author__ = 'dhallman'

from sourcegen import LanguageSource

class SwiftSource(LanguageSource.LanguageSource):

############
# Overrides
############

    def __init__(self, prefix, dateString, shouldSubclassUser, useOptionals):
        super(SwiftSource, self).__init__('Swift', prefix, dateString, shouldSubclassUser)
        self.useOptionals = useOptionals

    def createImplementation(self, schemas=[]):
        super(SwiftSource, self).createImplementation(schemas)
        self.generateParseExtension()

    def generateSubclass(self, schema, parseClassName='', subclassName='', isUserClass=False, subclassImports=[]):

        # Filename
        fileName = subclassName + '.swift'

        # Source
        source = ''

        # Header
        source += self.generateComments(fileName)

        # Imports
        source += 'import Parse\n\n'

        # Inheritance
        if isUserClass:
            source += 'class ' + subclassName + ' : PFUser {\n\n'
        else:
            source += 'class ' + subclassName + ' : PFObject, PFSubclassing {\n\n'

        source += '\toverride class func initialize() {\n'
        source += '\t\tstruct Static {\n'
        source += '\t\t\tstatic var onceToken : dispatch_once_t = 0;\n'
        source += '\t\t}\n'
        source += '\t\tdispatch_once(&Static.onceToken) {\n'
        source += '\t\t\tself.registerSubclass()\n'
        source += '\t\t}\n'
        source += '\t}\n\n'

        # Only necessary for PFObject subclasses
        if not isUserClass:
            source += '\tclass func parseClassName() -> String {\n'
            source += '\t\treturn \"'+ parseClassName + '\"\n'
            source += '\t}\n\n'

        source += '\t// MARK: Properties\n\n'

        for field, fieldDict in schema['fields'].iteritems():

            # Skip core fields
            if field in ['objectId', 'ACL', 'createdAt', 'updatedAt']:
                continue
            # Skip PFUser fields
            elif isUserClass and field in ['authData', 'email', 'emailVerified', 'username', 'password', 'role']:
                continue

            type = fieldDict['type']
            declareAsManaged = True

            if type == 'String':
                languageType =  'String'
            elif type == 'Number':
                languageType = 'NSNumber'
            elif type == 'Boolean':
                languageType = 'Bool'
                declareAsManaged = False
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
                languageType = '[{}]'.format(typeClass)
            elif type == 'Array':
                languageType = '[AnyObject]'
            else:
                print '\tunhandled field: {} {}'.format(field, str(fieldDict))
                continue

            # Property declaration
            if declareAsManaged:
                if self.useOptionals:
                    source += '\t@NSManaged var {}: {}?'.format(field, languageType)
                else:
                    source += '\t@NSManaged var {}: {}'.format(field, languageType)
            else:
                if self.useOptionals:
                    source += '\tvar {0}: {1}? {{\n\t\tget {{ return self["{0}"] as? {1} }}\n\t\tset {{ return self["{0}"] = newValue }}\n\t}}'.format(field, languageType)
                else:
                    source += '\tvar {0}: {1} {{\n\t\tget {{ return self["{0}"] as! {1} }}\n\t\tset {{ return self["{0}"] = newValue }}\n\t}}'.format(field, languageType)

            source += '\n'

        source += '}'

        # Save
        self.saveFile(fileName, source)

############
# Helpers
############

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