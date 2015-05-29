__author__ = 'Daniel Hallman'
__email__ = 'daniel.hallman@grepstar.net'

import json, httplib, os

# Custom variables (you should change these)
PARSE_APP_ID = ""
PARSE_MASTER_KEY = "" # DO NOT GIVE THIS TO ANYONE!
CUSTOM_CLASS_PREFIX = "GS"
SHOULD_SUBCLASS_USER = True

# Parse constants
PARSE_CLASS_PREFIX = "PF"

def main():
    assert PARSE_APP_ID, 'PARSE_APP_ID is blank!  Visit https://www.parse.com to obtain your keys.'
    assert PARSE_MASTER_KEY, 'PARSE_MASTER_KEY is blank! Visit https://www.parse.com to obtain your keys.'
    assert CUSTOM_CLASS_PREFIX, 'CUSTOM_CLASS_PREFIX is blank!  You should probably use a custom prefix.'

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

        print 'Generate {} --> {}'.format(filePath, className)

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
        source += '\t\t}\n\n'

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
                typeClass = parse_to_custom_class_name(fieldDict['targetClass'])
                if typeClass:
                    swiftType = typeClass + '?'
            elif type == 'Relation':
                typeClass = parse_to_custom_class_name(fieldDict['targetClass'])
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

        # Open file
        file = open(filePath, 'w')
        file.write(source)
        file.close()

def parse_to_custom_class_name(className=''):
    if SHOULD_SUBCLASS_USER and className == '_User':
        return CUSTOM_CLASS_PREFIX + className[1:]
    elif className.startswith('_'):
        return ''
    else:
        return CUSTOM_CLASS_PREFIX + className

if __name__ == '__main__':
    main()