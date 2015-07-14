# GSParseSchema
Parse Schema Swift subclass generation.

A simple python script to generate Swift subclasses from your Parse App Schema.

## Example
GSAddress.swift auto-generated from Parse Data Schema
```swift
import Parse

class GSAddress : PFObject, PFSubclassing {

	override class func initialize() {
		struct Static {
			static var onceToken : dispatch_once_t = 0;
		}
		dispatch_once(&Static.onceToken) {
			self.registerSubclass()
		}
	}

	class func parseClassName() -> String {
		return "Address"
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

GSUser.swift auto-generated from Parse Data Schema
```swift
import Parse

class GSUser : PFUser {

	override class func initialize() {
		struct Static {
			static var onceToken : dispatch_once_t = 0;
		}
		dispatch_once(&Static.onceToken) {
			self.registerSubclass()
		}
	}

	// MARK: Properties

	@NSManaged var firstName: String?

	@NSManaged var lastName: String?

	@NSManaged var profileImage: PFFile?

	@NSManaged var phone: NSNumber?

	@NSManaged var address: GSAddress?

}
```

## Usage
Edit main.py and customize the variables below.  Then run it!
```
$ python main.py -a <PARSE_APP_ID> -m <PARSE_MASTER_KEY> -p <CUSTOM_CLASS_PREFIX> -o -u
```
Voila!  Your custom classes will be generated in a local `Swift/` folder.  Drag and drop these into your project.

### `-a` `PARSE_APP_ID`
Your Parse Application ID

### `-m` `PARSE_MASTER_KEY`
Your Parse Master Key - **NEVER GIVE THIS TO ANYONE AND DO NOT SAVE IT TO YOUR REPO**

### `-p` `CUSTOM_CLASS_PREFIX`
The prefix to use for your Subclasses

### `-u` `SHOULD_SUBCLASS_USER`
PFUser will be subclassed as <`CUSTOM_CLASS_PREFIX`>User

### `-o` `USE_OPTIONALS`
Declare properties as optionals `?`


## Features
- Custom subclass prefix
- Internal Parse classes are skipped: _User, _Session, _Role, _Installation)
- Internal Parse fields are skipped: 'objectId', 'ACL', 'createdAt', 'updatedAt'
- Internal Parse PFUser fields are skipped: 'authData', 'email', 'emailVerified', 'username', 'password', 'role'
