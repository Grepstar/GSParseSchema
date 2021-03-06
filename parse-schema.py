__author__ = "Daniel Hallman"
__email__ = "daniel.hallman@grepstar.net"
__copyright__ = "Copyright 2015, Grepstar, LLC"
__license__ = "MIT"

import json, urllib2, os
import datetime

from optparse import OptionParser

from sourcegen import SwiftSource, ObjCSource

# Parse constants
PARSE_CLASS_PREFIX = "PF"

def main():
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="parse_server_url",
                      help="Parse Server URL",)
    parser.add_option("-a", "--parseappid", dest="parse_app_id",
                      help="Parse App ID",)
    parser.add_option("-m", "--parsemaster", dest="parse_master_key",
                      help="Parse Master Key",)
    parser.add_option("-p", "--prefix", dest="subclass_prefix",
                      help="Subclass Prefix",)
    parser.add_option("-l", "--language", dest="language",
                      help="Language to build templates",)
    (options, args) = parser.parse_args()

    if options.parse_server_url:
        PARSE_SERVER_URL = options.parse_server_url
    else:
        PARSE_SERVER_URL = 'http://localhost:1337/parse'
        # assert False, 'PARSE_SERVER_URL is blank!'

    if options.parse_app_id:
        PARSE_APP_ID = options.parse_app_id
    else:
        assert False, 'PARSE_APP_ID is blank!'

    if options.parse_master_key:
        PARSE_MASTER_KEY = options.parse_master_key
    else:
        assert False, 'PARSE_MASTER_KEY is blank!  Visit https://www.parse.com to obtain your keys.'

    if options.subclass_prefix:
        SUBCLASS_PREFIX = options.subclass_prefix
    else:
        assert False, 'SUBCLASS_PREFIX is blank!  You should probably use a custom prefix.'

    if options.language:
        LANGUAGE = options.language
        languages = ["swift", "objc"]
        assert LANGUAGE.lower() in languages, 'LANGUAGE must be one of the following: ' + ', '.join(languages)
    else:
        LANGUAGE = "swift"

    req = urllib2.Request(PARSE_SERVER_URL+'/schemas')
    req.add_header("X-Parse-Application-Id", PARSE_APP_ID)
    req.add_header("X-Parse-Master-Key", PARSE_MASTER_KEY)
    req.add_header("Content-Type", "application/json")
    opener = urllib2.build_opener()
    f = opener.open(req)
    result = json.loads(f.read())
    schemas = result['results']

    today = datetime.date.today().strftime('%m/%d/%y')

    if LANGUAGE == 'swift':
        generator = SwiftSource.SwiftSource(SUBCLASS_PREFIX, today, True)
    if LANGUAGE == 'objc':
        generator = ObjCSource.ObjCSource(SUBCLASS_PREFIX, today)

    generator.createImplementation(schemas)

if __name__ == '__main__':
    main()