import datetime
import json
import hashlib
import requests

def BaseModel(Database):
    class BaseModel:
        __abstract__ = True
        __database__ = Database
        __attributes__ = []
        __relationships__ = []
        __dataset_name__ = ""
        
        def __init__(self, _id=None, *args, **kwargs):
            if _id is not None:
                self._id = _id
            for key, value in kwargs.items():
                setattr(self, key, value) if key in self.__attributes__ + list(self.__relationships__.keys()) else None
            for attr in self.__attributes__:
                setattr(self, attr, None) if getattr(self, attr, None) is None else None
            for key, value in self.__relationships__.items():
                if getattr(self, key, None) is None:
                    setattr(self, key, [] if value[1].split('-')[2] == 'many' else None)                
                
        def __repr__(self):
            return f"{self.__class__.__name__}({', '.join([f'{key}={value}' for key, value in self.__dict__.items()])})"
        
        def save(self):
            self._id = self.__database__.save(self)
            
        def delete(self):
            self.__database__.delete(self)
            
        @classmethod
        def all(cls):
            return cls.__database__.all(cls)
        
        @classmethod
        def get(cls, _id):
            return cls.__database__.get(cls, _id)
        
        def exists(self):
            return self.__database__.exists(self)
        
        @classmethod
        def count(self):
            return self.__database__.count(self)
        
        def first(self, sort_key, sort_order):
            return self.__database__.filter(self, sort_key=sort_key, sort_order=sort_order, limit=1)[0]
        
        def last(self, sort_key, sort_order):
            return self.__database__.filter(self, sort_key=sort_key, sort_order=sort_order, limit=1, offset=self.count() - 1)[0]
        
        @classmethod
        def filter(cls, **kwargs):
            return cls.__database__.filter(cls, **kwargs)
        
        def to_dict(self):
            return {key: value for key, value in self.__dict__.items() if key in self.__attributes__ + list(self.__relationships__.keys()) + (['_id'] if '_id' in self.__dict__ else [])}

        @classmethod
        def from_dict(cls, data):
            return cls(**data)
        
        def to_json(self):
            return json.dumps(self.to_dict())
        
        @classmethod
        def from_json(cls, data):
            return cls.from_dict(json.loads(data))
        
        def reload(self):
            return self.__class__.get(self._id)
        
        @classmethod
        def collection_exists(cls):
            return cls.__database__.collection_exists(cls)
        
    return BaseModel

def User(Database):    
    class User(BaseModel(Database)):
        INACTIVE = "inactive"
        ACTIVE = "active"
        BANNED = "banned"
        
        READ = 0x01
        COMMENT = 0x02
        PUBLISH = 0x04
        EDIT = 0x08
        DELETE = 0x16
        
        ADMIN = 0x01
        CREATOR = 0x02
        MODERATOR = 0x04
        READER = 0x08
        
        __attributes__ = ['name', 'username', 'email', 'status', '_password', 'created_at', 'type', 'permissions', 'metadata', 'profile_picture', 'cover_picture']
        __relationships__ = {
            "posts": ("Posts", "one-to-many", "author"),
            "comments": ("Comments", "one-to-many", "author"),
            "likes": ("Likes", "one-to-many", "user"),
            "followers": ("Users", "many-to-many", "following"),
            "following": ("Users", "many-to-many", "followers")
        }
        __dataset_name__ = "Users"
        
        def __init__(self, name, username, email, _password, created_at="", status=ACTIVE, type=READER, permissions=0x01, metadata={}, profile_picture="", cover_picture="", posts=[], comments=[], likes=[], followers=[], following=[], _id=None):
            gravatar_profile = requests.get("https://www.gravatar.com/"+hashlib.md5(email.lower().encode()).hexdigest()+".json").json()
            gravatar_profile = gravatar_profile["entry"][0] if len(gravatar_profile["entry"]) > 0 else {}
            if profile_picture == "":
                profile_picture = "https://www.gravatar.com/avatar/"+hashlib.md5(email.lower().encode()).hexdigest()+"?d=identicon"
            if created_at == "":
                created_at = datetime.datetime.now()
            metadata.update({
                "gravatar": gravatar_profile,
            })
            super().__init__(_id, name=name, username=username, email=email, status=status, _password=_password, created_at=created_at, type=type, permissions=permissions, metadata=metadata, profile_picture=profile_picture, cover_picture=cover_picture, posts=posts, comments=comments, likes=likes, followers=followers, following=following)
        
        @property
        def types(self):
            types = []
            if User.ADMIN & self.type >> 0 == 1:
                types.append("admin")
            if User.CREATOR & self.type >> 1 == 1:
                types.append("creator")
            if User.MODERATOR & self.type >> 2 == 1:
                types.append("moderator")
            if User.READER & self.type >> 3 == 1:
                types.append("reader")
                
            return types
        
        @property
        def permissions_list(self):
            permissions = []
            if User.READ & self.permissions >> 0 == 1:
                permissions.append("read")
            if User.COMMENT & self.permissions >> 1 == 1:
                permissions.append("comment")
            if User.PUBLISH & self.permissions >> 2 == 1:
                permissions.append("publish")
            if User.EDIT & self.permissions >> 3 == 1:
                permissions.append("edit")
            if User.DELETE & self.permissions >> 4 == 1:
                permissions.append("delete")
                
            return permissions
        
        @property
        def password(self):
            return self._password
        
        @password.setter
        def password(self, value):
            self._password = hashlib.sha256(value.encode()).hexdigest()
            
        @classmethod
        def get_by_username(cls, username):
            result = cls.__database__.filter(cls, username=username)
            return result[0] if len(result) > 0 else None
        
        @classmethod
        def get_by_email(cls, email):
            result = cls.__database__.filter(cls, email=email)
            return result[0] if len(result) > 0 else None

        @classmethod
        def get_by_identity(cls, identity):
            result = (cls.__database__.filter(cls, username=identity) or cls.__database__.filter(cls, email=identity))
            return result[0] if len(result) > 0 else None
        
        def check_password(self, password):
            return self.password == hashlib.sha256(password.encode()).hexdigest()
        
    return User

def Post(Database):
    class Post(BaseModel(Database)):
        DRAFT = "draft"
        PUBLISHED = "published"
        ARCHIVED = "archived"
        
        __attributes__ = ['title', 'content', 'status', 'created_at', 'metadata', 'slug']
        __relationships__ = {
            "comments": ("Comments", "one-to-many", "post"),
            "likes": ("Likes", "one-to-many", "post"),
            "author": ("Users", "many-to-one", "posts"),
        }
        __dataset_name__ = "Posts"
        
        @classmethod
        def get_by_slug(cls, slug):
            return cls.__database__.filter(cls, slug=slug)[0]
        
    return Post

def Comment(Database):
    class Comment(BaseModel(Database)):
        APPROVED = "approved"
        PENDING = "pending"
        REJECTED = "rejected"
        REPORTED = "reported"
        REMOVED = "removed"
        
        __attributes__ = ['content', 'status', 'created_at', 'metadata']
        __relationships__ = {
            "likes": ("Likes", "one-to-many", "target"),
            "author": ("Users", "many-to-one", "comments"),
            "post": ("Posts", "many-to-one", "comments"),
            "replies": ("Replies", "one-to-many", "comment")
        }
        __dataset_name__ = "Comments"
        
    return Comment

def Reply(Database):
    class Reply(BaseModel(Database)):
        APPROVED = "approved"
        PENDING = "pending"
        REJECTED = "rejected"
        REPORTED = "reported"
        REMOVED = "removed"
        
        __attributes__ = ['content', 'status', 'created_at', 'metadata']
        __relationships__ = {
            "likes": ("Likes", "one-to-many", "target"),
            "author": ("Users", "many-to-one", "comments"),
            "comment": ("Comments", "many-to-one", "replies")
        }
        __dataset_name__ = "Replies"
        
    return Reply

def Like(Database):
    class Like(BaseModel(Database)):
        __attributes__ = ['created_at', 'metadata']
        __relationships__ = {
            "user": ("Users", "many-to-one", "likes"),
            "target": ("Posts", "many-to-one", "likes")
        }
        __dataset_name__ = "Likes"
        
    return Like
    
def Follow(Database):
    class Follow(BaseModel(Database)):
        APPROVED = "approved"
        PENDING = "pending"
        REJECTED = "rejected"
        
        __attributes__ = ['follower', 'following', 'status', 'created_at', 'metadata']
        __relationships__ = {
            "follower": ("Users", "many-to-one", "following"),
            "following": ("Users", "many-to-one", "followers")
        }
        __dataset_name__ = "Follows"
        
    return Follow

models = {
    "Users": User,
    "Posts": Post,
    "Comments": Comment,
    "Replies": Reply,
    "Likes": Like,
    "Follows": Follow
}