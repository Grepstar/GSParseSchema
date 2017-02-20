# GSParseSchema
Parse Schema iOS subclass generation in Swift and ObjC.

A python script to generate Swift and ObjC subclasses from your Parse App Schema.

Tested with Swift 3.0 and Xcode 8.

## Usage

### Generate subclasses

Swift
```
$ python parse-schema.py -a <PARSE_APP_ID> -m <PARSE_MASTER_KEY> -p <SUBCLASS_PREFIX> -u -l swift
```
Your custom classes will be generated in a local `Swift/` folder.

Objective-C
```
$ python parse-schema.py -a <PARSE_APP_ID> -m <PARSE_MASTER_KEY> -p <SUBCLASS_PREFIX> -u -l objc
```
Your custom classes will be generated in a local `ObjC/` folder. 

### Add files to your Xcode project
Drag and drop the generated files into your project.

### `Parse.registerSubclasses()` is no longer necessary with latest Parse SDK

#### `-u` `PARSE_SERVER_URL`
The Parse Server API URL.  Defaults to http://localhost:1337/parse.

#### `-a` `PARSE_APP_ID`
Your Parse Application ID

#### `-m` `PARSE_MASTER_KEY`
Your Parse Master Key - **NEVER GIVE THIS TO ANYONE AND DO NOT SAVE IT TO YOUR REPO**

#### `-p` `SUBCLASS_PREFIX`
The prefix to use for your Subclasses

#### `-l` `LANGUAGE`
The programming language to build your subclasses.  Valid inputs are "swift" or "objc". 

## Swift Example
```
$ python parse-schema.py -a <PARSE_APP_ID> -m <PARSE_MASTER_KEY> -p <SUBCLASS_PREFIX> -l swift
```
Auto-generated classes from Parse Data Schema

GSAddress.swift
```swift
import Parse

class GSAddress : PFObject, PFSubclassing {

	class func parseClassName() -> String {
		return "Address"
	}

	// MARK: Parse Keys

	class Key: PFObject.Key {
		static var startDate: String = "startDate"
		static var city: String = "city"
		static var country: String = "country"
		static var stateAbbrevation: String = "stateAbbrevation"
		static var line2: String = "line2"
		static var line1: String = "line1"
		static var zipCode: String = "zipCode"
		static var valid: String = "valid"
		static var location: String = "location"
	}
		
	// MARK: Properties

	@NSManaged var city: String?
	@NSManaged var country: String?
	@NSManaged var stateAbbrevation: String?
	@NSManaged var line2: String?
	@NSManaged var line1: String?
	@NSManaged var zipCode: NSNumber?
	var valid: Bool? {
		get { return self["valid"] as? Bool }
		set { return self["valid"] = newValue }
	}
	@NSManaged var location: PFGeoPoint?

}
```

GSUser.swift
```swift
import Parse

class GSUser : PFUser {

	class Key: PFObject.Key {
		static var firstName: String = "firstName"
		static var lastName: String = "lastName"
		static var profileImage: String = "profileImage"
		static var phone: String = "phone"
		static var address: String = "address"
	}

	// MARK: Properties

	@NSManaged var firstName: String?
	@NSManaged var lastName: String?
	@NSManaged var profileImage: PFFile?
	@NSManaged var phone: NSNumber?
	@NSManaged var address: GSAddress?

}
```

## Features
- Auto-generation of Parse keys and properties
- Custom subclass prefix
- Internal Parse classes are skipped: _User, _Session, _Role, _Installation)
- Internal Parse fields are skipped: 'objectId', 'ACL', 'createdAt', 'updatedAt'
- Internal Parse PFUser fields are skipped: 'authData', 'email', 'emailVerified', 'username', 'password', 'role'

## TODO
- Use file templates instead of string concatenation for generating source code
- Create boilerplate Swift extensions for adding addtional methods
- Create brew package
- Document `Add Script` build phase for auto-generation in Xcode project
