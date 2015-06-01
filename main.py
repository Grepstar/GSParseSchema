__author__ = 'Daniel Hallman'
__email__ = 'daniel.hallman@grepstar.net'

import json, httplib, os

from optparse import OptionParser

# Custom variables (you should change these)
PARSE_APP_ID = ""
PARSE_MASTER_KEY = "" # DO NOT GIVE THIS TO ANYONE!
CUSTOM_CLASS_PREFIX = ""
SHOULD_SUBCLASS_USER = True

# Parse constants
PARSE_CLASS_PREFIX = "PF"

def main():
    parser = OptionParser()
    parser.add_option("-a", "--parseappid", dest="parse_app_id",
                      help="Parse App ID",)
    parser.add_option("-m", "--parsemaster", dest="parse_master_key",
                      help="Parse Master Key",)
    parser.add_option("-p", "--prefix", dest="custom_class_prefex",
                      help="Custom Class Prefix",)

    (options, args) = parser.parse_args()

    if options.parse_app_id:
        PARSE_APP_ID = options.parse_app_id
    else:
        assert False, 'PARSE_APP_ID is blank!  Visit https://www.parse.com to obtain your keys.'

    if options.parse_master_key:
        PARSE_MASTER_KEY = options.parse_master_key
    else:
        assert False, 'PARSE_MASTER_KEY is blank!  Visit https://www.parse.com to obtain your keys.'

    if options.custom_class_prefex:
        CUSTOM_CLASS_PREFIX = options.custom_class_prefex
    else:
        assert False, 'CUSTOM_CLASS_PREFIX is blank!  You should probably use a custom prefix.'

    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('GET', '/1/schemas', "", {
           "X-Parse-Application-Id": PARSE_APP_ID,
           "X-Parse-Master-Key": PARSE_MASTER_KEY,
           "Content-Type": "application/json"
         })
    result = json.loads(connection.getresponse().read())

    schemas = result['results']

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

        customClass = CUSTOM_CLASS_PREFIX + className
        fileName = customClass + '.swift'
        filePath = 'Swift/' + fileName

        print 'Generate subclass for {} --> {}'.format(className, filePath)

        source = 'import Parse\n\n'

        # Inheritance
        if isUserClass:
            source += 'class ' + customClass + ' : PFUser, PFSubclassing {\n'
        else:
            source += 'class ' + customClass + ' : PFObject, PFSubclassing {\n'

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

            if type == 'String':
                swiftType =  'String?'
            elif type == 'Number':
                swiftType = 'NSNumber?'
            elif type == 'Boolean':
                swiftType = 'Bool?'
            elif type == 'Date':
                swiftType = 'NSDate?'
            elif type == 'GeoPoint':
                swiftType = 'PFGeoPoint?'
            elif type == 'File':
                swiftType = 'PFFile?'
            elif type == 'Pointer':
                typeClass = parse_to_custom_class_name(fieldDict['targetClass'], CUSTOM_CLASS_PREFIX, SHOULD_SUBCLASS_USER)
                if typeClass:
                    swiftType = typeClass + '?'
            elif type == 'Relation':
                typeClass = parse_to_custom_class_name(fieldDict['targetClass'], CUSTOM_CLASS_PREFIX, SHOULD_SUBCLASS_USER)
                if typeClass:
                    swiftType = '[' + typeClass + ']'
            elif type == 'Array':
                swiftType = '[AnyObject]?'
            else:
                print '\tunhandled field: {} {}'.format(field, str(fieldDict))
                continue

            source += '\t@NSManaged var {}: {}\n'.format(field, swiftType)

        source += '}'

        # Create directory
        dir = os.getcwd() + '/Swift'
        if not os.path.exists(dir):
            os.makedirs(dir)

        # Remove old file if it exists
        os.remove(filePath)

        # Open file
        file = open(filePath, 'w')
        file.write(source)
        file.close()

def parse_to_custom_class_name(className='', prefix='', shouldSubclassUser=False):
    if shouldSubclassUser and className == '_User':
        return prefix + className[1:]
    elif className.startswith('_'):
        return ''
    else:
        return prefix + className

if __name__ == '__main__':
    main()