# GSParseSchema
Parse Schema Swift subclass generation.

A simple python script to generate Swift subclasses from your Parse App Schema.

## Example
GSAddress.swift
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

	class func parseClassName() -> String {
		return "Address"
	}

	// MARK: Properties

	@NSManaged var line1: String?
	@NSManaged var line2: String?
	@NSManaged var city: String?
	@NSManaged var state: String?
	@NSManaged var zipCode: NSNumber?
	@NSManaged var country: String?
}
```

## Usage
Edit main.py and customize the variables below.  Then run it!
```
$ python main.py
```
Voila!  You're custom classes will be generated in a local `Swift/` folder.  Drag and drop these into your project.

### `PARSE_APP_ID`
Your Parse Application ID

### `PARSE_MASTER_KEY`
Your Parse Master Key - **NEVER GIVE THIS TO ANYONE AND DO NOT SAVE IT TO YOUR REPO**

### `CUSTOM_CLASS_PREFIX`
The prefix to use for your Subclasses

### `SHOULD_SUBCLASS_USER`
If True, PFUser will be subclassed as <`CUSTOM_CLASS_PREFIX`>User

## Features
- Custom subclass prefix
- Internal Parse classes are skipped: _User, _Session, _Role, _Installation)
- Internal Parse fields are skipped: 'objectId', 'ACL', 'createdAt', 'updatedAt'
- If `SHOULD_SUBCLASS_USER` = True - Internal Parse User fields are skipped: 'authData', 'email', 'emailVerified', 'username', 'password', 'role'