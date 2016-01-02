__author__ = 'dhallman'

from sourcegen import LanguageSource

class SwiftSource(LanguageSource.LanguageSource):

############
# Overrides
############

    def __init__(self, prefix, dateString, useOptionals):
        super(SwiftSource, self).__init__('Swift', prefix, dateString)
        self.useOptionals = useOptionals

    def createImplementation(self, schemas=[]):
        super(SwiftSource, self).createImplementation(schemas)
        self.generateParseExtension()

    def generateSubclass(self, schema, parseClassName='', subclassName='', isPrivateClass=False, subclassImports=[]):
        source = ''

        # Filename
        fileName = subclassName + '.swift'

        # Header
        source += self.generateComments(fileName)

        # Imports
        source += 'import Parse\n\n'

        # Inheritance
        if isPrivateClass:
            source += 'class ' + subclassName + ' : PF' + parseClassName[1:] + ' {\n\n'
        else:
            source += 'class ' + subclassName + ' : PFObject, PFSubclassing {\n\n'

        # Automatic registration of Parse subclass --> https://parse.com/docs/ios/guide#objects-subclassing-pfobject
        # However, this only works if you send a message to this class prior to initializing Parse.
        # source += '\toverride class func initialize() {\n'
        # source += '\t\tstruct Static {\n'
        # source += '\t\t\tstatic var onceToken : dispatch_once_t = 0;\n'
        # source += '\t\t}\n'
        # source += '\t\tdispatch_once(&Static.onceToken) {\n'
        # source += '\t\t\tself.registerSubclass()\n'
        # source += '\t\t}\n'
        # source += '\t}\n\n'

        # Parse Subclassing
        if not isPrivateClass:
            source += '\tclass func parseClassName() -> String {\n'
            source += '\t\treturn \"'+ parseClassName + '\"\n'
            source += '\t}\n\n'

        # Keys Enum
        source += '\t// MARK: Parse Keys\n\n'
        source += '\tenum Keys: String {\n'

        for field, fieldDict in schema['fields'].iteritems():

            # Skip core fields
            if field in self.fieldsToSkip['PFObject']:
                continue
            # Skip private fields
            elif isPrivateClass and field in self.fieldsToSkip[parseClassName]:
                continue

            source += '\t\tcase {0} = "{0}"\n'.format(field)

        source += '\t}\n\n'

        # Properties
        source += '\t// MARK: Properties\n\n'

        for field, fieldDict in schema['fields'].iteritems():

            # Skip core fields
            if field in self.fieldsToSkip['PFObject']:
                continue
            # Skip private fields
            elif isPrivateClass and field in self.fieldsToSkip[parseClassName]:
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

        print 'Generate Parse extension {}'.format(filePath)

        source = self.generateComments(fileName)

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