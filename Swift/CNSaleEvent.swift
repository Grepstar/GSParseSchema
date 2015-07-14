import Parse

class CNSaleEvent : PFObject, PFSubclassing {
	override class func initialize() {
		struct Static {
			static var onceToken : dispatch_once_t = 0;
		}
		dispatch_once(&Static.onceToken) {
			self.registerSubclass()
		}
	}

	class func parseClassName() -> String {
		return "SaleEvent"
	}

	// MARK: Properties

	@NSManaged var baseEvent: CNEvent?
	@NSManaged var volunteers: [CNUser]
}