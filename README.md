# GSParseSchema
Parse Schema Swift subclass generation.

A simple python script to generate Swift subclasses from your Parse App Schema.

## Usage
Edit main.py and customize the variables below.  Then run it!
```
$ python main.py
```
Voila!  You're custom classes will be generated in the Swift/ folder.  Drag and drop these into your project.

### `PARSE_APP_ID`
Your Parse Application ID

### `PARSE_MASTER_KEY`
Your Parse Master Key - NEVER GIVE THIS TO ANYONE AND DO NOT SAVE IT TO YOUR REPO

### `CUSTOM_CLASS_PREFIX`
The prefix to use for your Subclasses

### `SHOULD_SUBCLASS_USER`
If True, PFUser will be subclassed as `CUSTOM_CLASS_PREFIX`User

## Features
- Custom subclass prefix
- Internal Parse classes are skipped: _User, _Session, _Role, _Installation)
- Internal Parse fields are skipped: 'objectId', 'ACL', 'createdAt', 'updatedAt'
- If `SHOULD_SUBCLASS_USER` = True - Internal Parse User fields are skipped: 'authData', 'email', 'emailVerified', 'username', 'password', 'role'