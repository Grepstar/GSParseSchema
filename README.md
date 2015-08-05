# GSParseSchema
Parse Schema iOS subclass generation in Swift and ObjC.

A python script to generate Swift and ObjC subclasses from your Parse App Schema.

Tested with Swift 2.0 and Xcode 7-beta.

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

### Call `Parse.registerSubclasses()` in your AppDelegate
Register your subclasses in your AppDelegate.swift before `Parse.setApplicationId(applicationId: String, clientKey: String)`
```swift
@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

	var window: UIWindow?
    
	func application(application: UIApplication, didFinishLaunchingWithOptions launchOptions: [NSObject: AnyObject]?) -> Bool
	{
        Parse.registerSubclasses()
        Parse.setApplicationId(applicationId: String, clientKey: String)
       
        ...
         
    }
}
```

#### `-a` `PARSE_APP_ID`
Your Parse Application ID

#### `-m` `PARSE_MASTER_KEY`
Your Parse Master Key - **NEVER GIVE THIS TO ANYONE AND DO NOT SAVE IT TO YOUR REPO**

#### `-p` `SUBCLASS_PREFIX`
The prefix to use for your Subclasses

#### `-u` `SHOULD_SUBCLASS_USER`
PFUser will be subclassed as <`SUBCLASS_PREFIX`>User

#### `-l` `LANGUAGE`
The programming language to build your subclasses.  Valid inputs are "swift" or "objc". 

## Swift Example
```
$ python parse-schema.py -a <PARSE_APP_ID> -m <PARSE_MASTER_KEY> -p <SUBCLASS_PREFIX> -u -l swift
```
Auto-generated classes from Parse Data Schema

GSAddress.swift
```swift
import Parse

public enum GSAddressKey: String {
	case city = "city"
	case country = "country"
	case stateAbbrevation = "stateAbbrevation"
	case line2 = "line2"
	case line1 = "line1"
	case zipCode = "zipCode"
	case valid = "valid"
	case location = "location"
}

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

GSUser.swift
```swift
import Parse

public enum GSUserKey: String {
	case firstName = "firstName"
	case lastName = "lastName"
	case profileImage = "profileImage"
	case phone = "phone"
	case address = "address"
}

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

Parse+Subclasses.swift
```swift
import Parse

extension Parse {

	// Call this function before setApplicationId:clientKey: in your AppDelegate
	class func registerSubclasses() {
		GSAddress.registerSubclass()
		GSUser.registerSubclass()
	}
}
```

## ObjC Example
```
$ python parse-schema.py -a <PARSE_APP_ID> -m <PARSE_MASTER_KEY> -p <SUBCLASS_PREFIX> -u -l objc
```

Auto-generated classes from Parse Data Schema

GSAddress.h
```objective-c
#import <Parse/Parse.h>

extern const struct GSAddressKey {
	__unsafe_unretained NSString *city;
	__unsafe_unretained NSString *country;
	__unsafe_unretained NSString *stateAbbrevation;
	__unsafe_unretained NSString *line2;
	__unsafe_unretained NSString *line1;
	__unsafe_unretained NSString *zipCode;
	__unsafe_unretained NSString *valid;
	__unsafe_unretained NSString *location;
} GSAddressKey;

@interface GSAddress : PFObject<PFSubclassing>

+ (NSString *)parseClassName;

@property (nonatomic, strong) NSString *city;
@property (nonatomic, strong) NSString *country;
@property (nonatomic, strong) NSString *stateAbbrevation;
@property (nonatomic, strong) NSString *line2;
@property (nonatomic, strong) NSString *line1;
@property (nonatomic, strong) NSNumber *zipCode;
@property (nonatomic, assign) BOOL valid;
@property (nonatomic, strong) PFGeoPoint *location;

@end
```

GSAddress.m
```objective-c
#import "GSAddress.h"
#import <Parse/PFObject+Subclass.h>

const struct GSAddressKey GSAddressKey = {
	.city = @"city",
	.country = @"country",
	.stateAbbrevation = @"stateAbbrevation",
	.line2 = @"line2",
	.line1 = @"line1",
	.zipCode = @"zipCode",
	.valid = @"valid",
	.location = @"location",
};

@implementation GSAddress

+ (void)load {
	[self registerSubclass];
}

+ (NSString *)parseClassName {
	return @"Address";
}

@dynamic city;
@dynamic country;
@dynamic stateAbbrevation;
@dynamic line2;
@dynamic line1;
@dynamic zipCode;
@dynamic valid;
@dynamic location;

@end
```

GSUser.h
```objective-c
#import <Parse/Parse.h>

extern const struct GSUserKey {
	__unsafe_unretained NSString *firstName;
	__unsafe_unretained NSString *lastName;
	__unsafe_unretained NSString *profileImage;
	__unsafe_unretained NSString *phone;
	__unsafe_unretained NSString *address;
} GSUserKey;

@class GSAddress;

@interface GSUser : PFUser

+ (NSString *)parseClassName;

@property (nonatomic, strong) NSString *firstName;
@property (nonatomic, strong) NSString *lastName;
@property (nonatomic, strong) PFFile *profileImage;
@property (nonatomic, strong) NSNumber *phone;
@property (nonatomic, strong) GSAddress *address;

@end
```

GSUser.m
```objective-c
#import "GSUser.h"
#import <Parse/PFObject+Subclass.h>
#import "GSAddress.h"

const struct GSUserKey GSUserKey = {
	.firstName = @"firstName",
	.lastName = @"lastName",
	.profileImage = @"profileImage",
	.phone = @"phone",
	.address = @"address",
};

@implementation GSUser

+ (void)load {
	[self registerSubclass];
}

+ (NSString *)parseClassName {
	return @"_User";
}

@dynamic firstName;
@dynamic lastName;
@dynamic profileImage;
@dynamic phone;
@dynamic address;

@end
```

## Features
- Auto-generation of Parse keys and properties
- Custom subclass prefix
- Internal Parse classes are skipped: _User, _Session, _Role, _Installation)
- Internal Parse fields are skipped: 'objectId', 'ACL', 'createdAt', 'updatedAt'
- Internal Parse PFUser fields are skipped: 'authData', 'email', 'emailVerified', 'username', 'password', 'role'

## TODO
- Move Enums into Class declaration
- Suport custom Enum types
- Use Email/Password authentication: allows REST API to grab list of Parse Apps
	- User input for selecting app: extract Parse App ID
	- Move source code into a folder named after Parse App
- Use file templates instead of string concatenation for generating source code
- Create boilerplate Swift extensions for adding addtional methods
- Create brew package
- Document `Add Script` build phase for auto-generation in Xcode project
