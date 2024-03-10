import jwt, datetime

class Auth:
    READ = 0x01
    COMMENT = 0x02
    PUBLISH = 0x04
    EDIT = 0x08
    DELETE = 0x16
    
    ADMIN = 0x01
    CREATOR = 0x02
    MODERATOR = 0x04
    READER = 0x08
    
    def __init__(self, secret_key, db, user_model):
        self.secret_key = secret_key
        self.db = db
        self.user_model = user_model
        
    def generate_token(self, user):
        return jwt.encode({"user": user._id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)}, self.secret_key, algorithm="HS256")
    
    def user_from_token(self, token):
        try:
            return self.user_model.get(jwt.decode(token, self.secret_key, algorithms=["HS256"])["user"])
        except:
            return None
        
    def renew_token(self, token):
        try:
            user = self.user_from_token(token)
            return self.generate_token(user)
        except:
            return None
        
    def authenticate(self, identity, password):
        user = self.user_model.get_by_identity(identity)
        if user and user.check_password(password):
            return self.generate_token(user)
        return False
    
    def generate_access_token(self, user, permissions, expiration):
        return jwt.encode({"user": user._id, "permissions": permissions, "exp": datetime.datetime.utcnow() + expiration}, self.secret_key, algorithm="HS256")
    
    def user_from_access_token(self, token):
        try:
            return self.user_model.get(jwt.decode(token, self.secret_key, algorithms=["HS256"])["user"])
        except:
            return None
        
    def permissions_from_access_token(self, token):
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])["permissions"]
        except:
            return None
        
    def renew_access_token(self, token):
        try:
            user = self.user_from_access_token(token)
            permissions = self.permissions_from_access_token(token)
            return self.generate_access_token(user, permissions, datetime.timedelta(days=30))
        except:
            return None
    
    #Decorator takes permissions and type codes
    def access_control(self, permissions, type, on_unauthorized=lambda request: ({"error": "Unauthorized"}, 401), on_forbidden=lambda request: ({"error": "Forbidden"}, 403)):
        def decorator(f):
            def wrapper(request, *args, **kwargs):
                if request.data["COOKIE"].get("JWT"):
                    user = self.user_from_access_token(request.data["COOKIE"]["JWT"])
                    if not user:
                        return on_unauthorized(request)
                    if not user.permissions & permissions == permissions:
                        return on_forbidden(request)
                    if user.type & type != type and user.type & self.ADMIN != self.ADMIN:
                        return on_forbidden(request)
                    return f(request, user, *args, **kwargs)

                if request.headers.get("Authorization"):
                    token = request.headers["Authorization"].split(" ")[1]
                    user = self.user_from_access_token(token)
                    if not user:
                        return on_unauthorized(request)
                    if not user.permissions & permissions == permissions:
                        return on_forbidden(request)
                    if user.type & type != type and user.type & self.ADMIN != self.ADMIN:
                        return on_forbidden(request)
                    return f(request, user, *args, **kwargs)

                return on_unauthorized(request)
            return wrapper
        return decorator