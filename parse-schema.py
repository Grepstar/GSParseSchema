__author__ = "Daniel Hallman"
__email__ = "daniel.hallman@grepstar.net"
__copyright__ = "Copyright 2015, Grepstar, LLC"
__license__ = "MIT"

import json, httplib, os
import datetime

from optparse import OptionParser

# Parse constants
PARSE_CLASS_PREFIX = "PF"

def main():
    parser = OptionParser()
    parser.add_option("-a", "--parseappid", dest="parse_app_id",
                      help="Parse App ID",)
    parser.add_option("-m", "--parsemaster", dest="parse_master_key",
                      help="Parse Master Key",)
    parser.add_option("-p", "--prefix", dest="subclass_prefix",
                      help="Subclass Prefix",)
    parser.add_option("-o", "--optionals", action="store_true", dest="optionals",
                      help="Declare properties as optionals",)
    parser.add_option("-u", "--user", action="store_true", dest="subclass_user",
                      help="Subclass PFUser",)

    (options, args) = parser.parse_args()

    if options.parse_app_id:
        PARSE_APP_ID = options.parse_app_id
    else:
        assert False, 'PARSE_APP_ID is blank!  Visit https://www.parse.com to obtain your keys.'

    if options.parse_master_key:
        PARSE_MASTER_KEY = options.parse_master_key
    else:
        assert False, 'PARSE_MASTER_KEY is blank!  Visit https://www.parse.com to obtain your keys.'

    if options.subclass_prefix:
        SUBCLASS_PREFIX = options.subclass_prefix
    else:
        assert False, 'SUBCLASS_PREFIX is blank!  You should probably use a custom prefix.'

    if options.optionals:
        USE_OPTIONALS = options.optionals
    else:
        USE_OPTIONALS = False

    if options.subclass_user:
        SHOULD_SUBCLASS_USER = options.subclass_user
    else:
        SHOULD_SUBCLASS_USER = False

    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('GET', '/1/schemas', "", {
           "X-Parse-Application-Id": PARSE_APP_ID,
           "X-Parse-Master-Key": PARSE_MASTER_KEY,
           "Content-Type": "application/json"
         })
    result = json.loads(connection.getresponse().read())

    schemas = result['results']

    # Array of subclasses
    subclasses = []

    for schema in schemas:
        className = schema['className']

        isUserClass = False

        # Special case to subclass User
        if SHOULD_SUBCLASS_USER and className == '_User':
            isUserClass = True
            className = className[1:]
        # Skip internal Parse classes (User, Session, Role, Installation)
        elif className.startswith('_'):
            continue

        subclass = SUBCLASS_PREFIX + className
        subclasses.append(subclass)
        fileName = subclass + '.swift'
        filePath = 'Swift/' + fileName


        print 'Generate subclass for {} --> {}'.format(className, filePath)

        source = ''

        today = datetime.date.today().strftime('%m/%d/%y')

        # Header
        source += generateHeaderSource(fileName, today)

        # Imports
        source += 'import Parse\n\n'

        # Inheritance
        if isUserClass:
            source += 'class ' + subclass + ' : PFUser {\n\n'
        else:
            source += 'class ' + subclass + ' : PFObject, PFSubclassing {\n\n'

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
            source += '\t\treturn \"'+ className + '\"\n'
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
                swiftType =  'String'
            elif type == 'Number':
                swiftType = 'NSNumber'
            elif type == 'Boolean':
                swiftType = 'Bool'
                declareAsManaged = False
            elif type == 'Date':
                swiftType = 'NSDate'
            elif type == 'GeoPoint':
                swiftType = 'PFGeoPoint'
            elif type == 'File':
                swiftType = 'PFFile'
            elif type == 'Pointer':
                typeClass = parse_to_subclass_name(fieldDict['targetClass'], SUBCLASS_PREFIX, SHOULD_SUBCLASS_USER)
                swiftType = typeClass
            elif type == 'Relation':
                typeClass = parse_to_subclass_name(fieldDict['targetClass'], SUBCLASS_PREFIX, SHOULD_SUBCLASS_USER)
                swiftType = '[{}]'.format(typeClass)
            elif type == 'Array':
                swiftType = '[AnyObject]'
            else:
                print '\tunhandled field: {} {}'.format(field, str(fieldDict))
                continue

            # Property declaration
            if declareAsManaged:
                if USE_OPTIONALS:
                    source += '\t@NSManaged var {}: {}?'.format(field, swiftType)
                else:
                    source += '\t@NSManaged var {}: {}'.format(field, swiftType)
            else:
                if USE_OPTIONALS:
                    source += '\tvar {0}: {1}? {{\n\t\tget {{ return self["{0}"] as? {1} }}\n\t\tset {{ return self["{0}"] = newValue }}\n\t}}'.format(field, swiftType)
                else:
                    source += '\tvar {0}: {1} {{\n\t\tget {{ return self["{0}"] as! {1} }}\n\t\tset {{ return self["{0}"] = newValue }}\n\t}}'.format(field, swiftType)

            source += '\n\n'

        source += '}'

        # Create directory
        dir = os.getcwd() + '/Swift'
        if not os.path.exists(dir):
            os.makedirs(dir)

        # Remove old file if it exists
        if os.path.exists(filePath):
            os.remove(filePath)

        # Open file
        file = open(filePath, 'w')
        file.write(source)
        file.close()

    # Generate the subclass registration extension
    generateParseExtension(subclasses, today)

# Generate the subclass registration extension
def generateParseExtension(subclasses=[], today=''):
    fileName = 'Parse+Subclasses.swift'
    filePath = 'Swift/' + fileName
    source = ''

    print 'Generate Parse extension {}'.format(filePath)

    source += generateHeaderSource(fileName, today)

    # Imports
    source += 'import Parse\n\n'

    # Extension
    source += 'extension Parse {\n\n'
    source += '\t// Call this function before \'Parse.setApplicationId(applicationId: String, clientKey: String)\' in your AppDelegate\n'
    source += '\tclass func registerSubclasses() {\n'

    for subclass in subclasses:
        source += '\t\t{}.registerSubclass()\n'.format(subclass)

    source += '\t}\n'
    source += '}'

    # Remove old file if it exists
    if os.path.exists(filePath):
        os.remove(filePath)

    # Open file
    file = open(filePath, 'w')
    file.write(source)
    file.close()

# Generate header source
def generateHeaderSource(fileName='', today=''):
    source = '//\n'
    source += '// {}\n'.format(fileName)
    source += '//\n'
    source += '// Auto-generated by GSParseSchema on {}.\n'.format(today)
    source += '// https://github.com/Grepstar/GSParseSchema\n'
    source += '//\n\n'
    return source

# Helper method to determine subclass name from the Parse model
def parse_to_subclass_name(className='', prefix='', shouldSubclassUser=False):
    if shouldSubclassUser and className == '_User':
        return prefix + className[1:]
    elif className.startswith('_'):
        return ''
    else:
        return prefix + className

if __name__ == '__main__':
    main()