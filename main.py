from fastapi import FastAPI, HTTPException, Body
from datetime import datetime, timedelta
from pydantic import BaseModel
from pymongo import MongoClient
import bcrypt
import certifi
import os
import jwt

app = FastAPI()

# Env vars with local fallbacks (remove fallbacks in production if desired)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Fallback for local
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")  # Secure this!
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserModel(BaseModel):
    token: str
    name: str
    email: str
    address: str
    city: str

class PostData(BaseModel):
    name: str
    email: str
    postText: str
    address: str
    city: str

def get_db_connection():
    """Helper to get MongoDB client per request (serverless-friendly)"""
    try:
        client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),  # Comment out if SSL errors persist
            serverSelectionTimeoutMS=5000
        )
        client.admin.command("ping")  # Test connection
        return client
    except Exception as e:
        raise ValueError(f"Failed to connect to MongoDB: {str(e)}")

def hash_password(password: str) -> str:
    """Hash the password using bcrypt and return as string"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify the entered password with stored hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode())

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Helper to generate JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Root route (no DB needed)
@app.get("/")
def home():
    """Root endpoint to confirm API is running"""
    return {"message": "Welcome to the Attendance API! 🚀"}

@app.get("/testingDone")
def test():
    """Test endpoint to confirm API is running"""
    return {"message": "Testing Done! 🚀"}

# Signup API
@app.post("/signup")
def signup(
    name: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    address: str = Body(...),
    city: str = Body(...)
):
    """Register a new user with hashed password"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        users_collection = db["users"]
        if users_collection.find_one({"email": email}):
            raise HTTPException(status_code=400, detail="User already exists")
        
        hashed_password = hash_password(password)
        new_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "address": address,
            "city": city
        }
        users_collection.insert_one(new_user)
        
        # Generate token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        
        # Return as UserModel
        return UserModel(
            token=access_token,
            name=name,
            email=email,
            address=address,
            city=city
        )
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# Login API
@app.post("/login")
def login(email: str = Body(...), password: str = Body(...)):
    """Login user by verifying email and password"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        users_collection = db["users"]
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Generate token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        
        # Return as UserModel
        return UserModel(
            token=access_token,
            name=user["name"],
            email=user["email"],
            address=user.get("address", ""),
            city=user.get("city", "")
        )
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# Home screen API
@app.get("/users")
def get_users():
    """Show all registered users (Home Screen)"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        users_collection = db["users"]
        users = list(users_collection.find({}, {"_id": 0, "password": 0}))
        return {"total_users": len(users), "users": users}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# Mark attendance API
@app.post("/mark_attendance")
def mark_attendance(email: str = Body(...)):
    """Mark attendance for a logged-in user"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        users_collection = db["users"]
        attendance_collection = db["attendance"]
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        record = {
            "email": email,
            "name": user["name"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        attendance_collection.insert_one(record)
        return {"message": f"Attendance marked for {user['name']}", "time": record["time"]}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attendance error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# View attendance API
@app.get("/attendance/{email}")
def view_user_attendance(email: str):
    """View attendance records for a specific user by email"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        attendance_collection = db["attendance"]
        records = list(attendance_collection.find({"email": email}, {"_id": 0}))
        if not records:
            raise HTTPException(status_code=404, detail=f"No attendance found for {email}")
        return {"total_records": len(records), "attendance": records}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attendance view error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# Delete user API
@app.delete("/users/{email}")
def delete_user(email: str):
    """Delete a user by email"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        users_collection = db["users"]
        result = users_collection.delete_one({"email": email})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": f"User '{email}' deleted successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# Update user name API
@app.put("/users/{email}")
def update_user_name(email: str, name: str = Body(...)):
    """Update only the user's name"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        users_collection = db["users"]
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        result = users_collection.update_one({"email": email}, {"$set": {"name": name}})
        if result.modified_count == 0:
            return {"message": "Name is already the same, nothing changed"}
        return {"message": f"User '{email}' name updated to '{name}'"}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# Filter user name API
@app.get("/users/filter/{name}")
def userSearch(name: str):
    """
    🔍 Search users by name (case-insensitive)
    """
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        users_collection = db["users"]
        users = list(users_collection.find({"name": {"$regex": name, "$options": "i"}}, {"_id": 0, "password": 0}))
        
        if not users:
            raise HTTPException(status_code=404, detail=f"No users found with name containing '{name}'")
        
        return {"total_users": len(users), "users": users}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# User count API
@app.get("/users/count")
def user_count():
    """Get total number of registered users"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        users_collection = db["users"]
        count = users_collection.count_documents({})
        return {"total_users": count}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Count error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# Attendance count API
@app.get("/attendance/count")
def attendance_count():
    """Get total number of attendance records"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        attendance_collection = db["attendance"]
        count = attendance_collection.count_documents({})
        return {"total_attendance_records": count}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attendance count error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# Create post API
@app.post("/post")
def post(posting: PostData):
    """Create a new post"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        post_collection = db["post"]
        result = post_collection.insert_one(posting.dict())
        new_post = post_collection.find_one({"_id": result.inserted_id})
        return serialize_doc(new_post)
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# Search post API
@app.get("/post/{name}")
def post_search(name: str):
    """Search post by name"""
    try:
        client = get_db_connection()
        db = client["attendance_system"]
        post_collection = db["post"]
        post = post_collection.find_one({"name": name})
        if not post:
            raise HTTPException(status_code=404, detail=f"No post found for '{name}'")
        return serialize_doc(post)
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post search error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

# from fastapi import FastAPI, HTTPException, Body
# from datetime import datetime, timedelta
# from pydantic import BaseModel
# from pymongo import MongoClient
# import bcrypt
# import certifi
# import os
# import jwt
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# app = FastAPI()

# # MongoDB connection
# MONGO_URI = os.getenv("MONGO_URI")
# if not MONGO_URI:
#     raise ValueError("MONGO_URI environment variable not set")

# try:
#     client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=60000)
#     client.admin.command("ping")  # Test connection
# except Exception as e:
#     raise ValueError(f"Failed to connect to MongoDB: {str(e)}")

# # Select database and collections
# db = client["attendance_system"]
# users_collection = db["users"]
# attendance_collection = db["attendance"]
# post_collection = db["post"]

# # Helper functions
# def hash_password(password: str) -> str:
#     """Hash the password using bcrypt and return as string"""
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

# def verify_password(password: str, hashed: str) -> bool:
#     """Verify the entered password with stored hash"""
#     return bcrypt.checkpw(password.encode('utf-8'), hashed.encode())

# # Root route
# @app.get("/")
# def home():
#     """Root endpoint to confirm API is running"""
#     return {"message": "Welcome to the Attendance API! 🚀"}

# @app.get("/testingDone")
# def test():
#     """Test endpoint to confirm API is running"""
#     return {"message": "Testing Done! 🚀"}


# # 
# # import jwt
# # from datetime import datetime, timedelta
# # from fastapi import Body, HTTPException
# # ... other imports (e.g., from your BaseModel, app, users_collection, etc.)

# # Assuming you have a JWT secret (set this in your config or env)
# JWT_SECRET = "your-secret-key"  # Replace with a secure secret
# JWT_ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Customize expiration

# class UserModel(BaseModel):
#     token: str
#     name: str
#     email: str
#     address: str
#     city: str

# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     """Helper to generate JWT token"""
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     return encoded_jwt

# # Signup API
# @app.post("/signup")
# def signup(
#     name: str = Body(...),
#     email: str = Body(...),
#     password: str = Body(...),
#     address: str = Body(...),
#     city: str = Body(...)
# ):
#     """Register a new user with hashed password"""
#     try:
#         if users_collection.find_one({"email": email}):
#             raise HTTPException(status_code=400, detail="User already exists")
        
#         hashed_password = hash_password(password)
#         new_user = {
#             "name": name,
#             "email": email,
#             "password": hashed_password,
#             "address": address,
#             "city": city
#         }
#         users_collection.insert_one(new_user)
        
#         # Generate token
#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token = create_access_token(
#             data={"sub": email}, expires_delta=access_token_expires
#         )
        
#         # Return as UserModel
#         return UserModel(
#             token=access_token,
#             name=name,
#             email=email,
#             address=address,
#             city=city
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")

# # Login API
# @app.post("/login")
# def login(email: str = Body(...), password: str = Body(...)):
#     """Login user by verifying email and password"""
#     user = users_collection.find_one({"email": email})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     if not verify_password(password, user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid password")
    
#     # Generate token
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": email}, expires_delta=access_token_expires
#     )
    
#     # Return as UserModel
#     return UserModel(
#         token=access_token,
#         name=user["name"],
#         email=user["email"],
#         address=user.get("address", ""),  # Default empty if not present
#         city=user.get("city", "")  # Default empty if not present
#     )





# # # Signup API
# # @app.post("/signup")
# # def signup(name: str = Body(...), email: str = Body(...), password: str = Body(...)):
# #     """Register a new user with hashed password"""
# #     try:
# #         if users_collection.find_one({"email": email}):
# #             raise HTTPException(status_code=400, detail="User already exists")
        
# #         hashed_password = hash_password(password)
# #         new_user = {"name": name, "email": email, "password": hashed_password}
# #         users_collection.insert_one(new_user)
        
# #         return {
# #             "status": "success",
# #             "message": "User registered successfully!",
# #             "user": {"name": name, "email": email}
# #         }
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")

# # # Login API

# # class UserModel(BaseModel):
# #     token: str
# #     name: str
# #     email: str
# #     address: str
# #     city: str
# # @app.post("/login")
# # def login(email: str = Body(...), password: str = Body(...)):
# #     """Login user by verifying email and password"""
# #     user = users_collection.find_one({"email": email})
# #     if not user:
# #         raise HTTPException(status_code=404, detail="User not found")
# #     if not verify_password(password, user["password"]):
# #         raise HTTPException(status_code=401, detail="Invalid password")
# #     return {"message": f"Welcome {user['name']}! Login successful."}










# # Home screen API
# @app.get("/users")
# def get_users():
#     """Show all registered users (Home Screen)"""
#     users = list(users_collection.find({}, {"_id": 0, "password": 0}))
#     return {"total_users": len(users), "users": users}

# # Mark attendance API
# @app.post("/mark_attendance")
# def mark_attendance(email: str = Body(...)):
#     """Mark attendance for a logged-in user"""
#     user = users_collection.find_one({"email": email})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     record = {
#         "email": email,
#         "name": user["name"],
#         "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     }
#     attendance_collection.insert_one(record)
#     return {"message": f"Attendance marked for {user['name']}", "time": record["time"]}

# # View attendance API
# @app.get("/attendance/{email}")
# def view_user_attendance(email: str):
#     """View attendance records for a specific user by email"""
#     records = list(attendance_collection.find({"email": email}, {"_id": 0}))
#     if not records:
#         raise HTTPException(status_code=404, detail=f"No attendance found for {email}")
#     return {"total_records": len(records), "attendance": records}

# # Delete user API
# @app.delete("/users/{email}")
# def delete_user(email: str):
#     """Delete a user by email"""
#     result = users_collection.delete_one({"email": email})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"message": f"User '{email}' deleted successfully"}

# # Update user name API
# @app.put("/users/{email}")
# def update_user_name(email: str, name: str = Body(...)):
#     """Update only the user's name"""
#     user = users_collection.find_one({"email": email})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     result = users_collection.update_one({"email": email}, {"$set": {"name": name}})
#     if result.modified_count == 0:
#         return {"message": "Name is already the same, nothing changed"}
#     return {"message": f"User '{email}' name updated to '{name}'"}

# # Filter user name API
# @app.get("/users/filter/{name}")
# def userSearch(name: str):
#     """
#     🔍 Search users by name (case-insensitive)
#     """
#     try:
#         users = list(users_collection.find({"name": {"$regex": name, "$options": "i"}}, {"_id": 0, "password": 0}))
        
#         if not users:
#             raise HTTPException(status_code=404, detail=f"No users found with name containing '{name}'")
        
#         return {"total_users": len(users), "users": users}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# # User count API
# @app.get("/users/count")
# def user_count():
#     """Get total number of registered users"""
#     count = users_collection.count_documents({})
#     return {"total_users": count}

# # Attendance count API
# @app.get("/attendance/count")
# def attendance_count():
#     """Get total number of attendance records"""
#     count = attendance_collection.count_documents({})
#     return {"total_attendance_records": count}

# # Post model
# class PostData(BaseModel):
#     name: str
#     email: str
#     postText: str
#     address: str
#     city: str

# # Helper to serialize MongoDB document
# def serialize_doc(doc):
#     doc["_id"] = str(doc["_id"])
#     return doc

# # Create post API
# @app.post("/post")
# def post(posting: PostData):
#     """Create a new post"""
#     result = post_collection.insert_one(posting.dict())
#     new_post = post_collection.find_one({"_id": result.inserted_id})
#     return serialize_doc(new_post)

# # Search post API
# @app.get("/post/{name}")
# def post_search(name: str):
#     """Search post by name"""
#     post = post_collection.find_one({"name": name})
#     if not post:
#         raise HTTPException(status_code=404, detail=f"No post found for '{name}'")
#     return serialize_doc(post)