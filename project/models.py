from project import db


class PropertyType(str, db.enum.Enum):
    RENT = "rent"
    SALE = "sale"

class Account(db.Model): 
    __tablename__ = 'UserAccounts'
    userID = db.Column('userID', db.Integer, primary_key=True, unique=True)
    userName = db.Column('userName', db.String(100), unique=True)
    password = db.Column('password', db.String(100))
    email = db.Column('email', db.String(100))
    savedListings = db.Column('savedListings', db.Integer)
    address = db.Column('address', db.String(100))

    def __init__ (self, userID, userName, password, email, savedListings, address):
        self.userID = userID
        self.userName = userName
        self.password = password
        self.email = email
        self.savedListings = savedListings
        self.address = address

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Property(db.Model):
    __tablename__ = 'Property'
    id = db.Column('id', db.String(100), primary_key=True)
    clusterId = db.Column('clusterId', db.String(100))
    type = db.Column('type', db.Enum(PropertyType))
    # UserSaved = Column('UserSaved', )

    def __init__(self, id, clusterId, type):
        self.id = id
        self.clusterId = clusterId
        self.type = type
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserSavedProperty(db.Model):
    __tablename__ = 'savedListings'
    userID = db.Column('userID', db.String(100))
    propertyId = db.Column('propertyId', db.String(100))
    property = db.Column('property', db.PickleType) 
    __table_args__ = (db.
        db.PrimaryKeyConstraint(userID, propertyId),
        {},
    )

    def __init__(self, userID, propertyId, property):
        self.userID = userID
        self.propertyId = propertyId
        self.property = property

    def as_dict(self):
        dicout = {}
        for col in self.__table__.columns:
            if col.name=="userID":
                dicout["userID"] = getattr(self, col.name)
            if col.name=="propertyId":
                dicout["propertyId"] = getattr(self, col.name)
            if col.name=="property":
                dicout["property"] = db.pickle.loads(getattr(self,col.name))

        return dicout