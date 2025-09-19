# import os
# import logging
# from dotenv import load_dotenv
# import cloudinary
# import cloudinary.uploader
# import cloudinary.api
# from pymongo import MongoClient
# import certifi
# from fastapi import FastAPI
# # from fastapi import UploadFile, File
# # Initialize FastAPI app
# app = FastAPI()

# # Configure logging
# logger = logging.getLogger(__name__)  # Fixed: __main__ to __name__
# logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
# logger.addHandler(handler)

# # Load environment variables
# load_dotenv()

# # MongoDB connection
# MONGO_URI = os.getenv("MONGO_URI")
# if not MONGO_URI:
#     logger.error("MONGO_URI environment variable not set")
#     raise ValueError("MONGO_URI environment variable not set")

# try:
#     client = MongoClient(
#         MONGO_URI,
#         tlsCAFile=certifi.where(),
#         serverSelectionTimeoutMS=60000,
#         connectTimeoutMS=30000,
#         socketTimeoutMS=30000,
#         retryWrites=True,
#         retryReads=True
#     )
#     client.admin.command("ping")  # Test connection
#     logger.info("Successfully connected to MongoDB")
# except Exception as e:
#     logger.error(f"Failed to connect to MongoDB: {str(e)}", exc_info=True)
#     raise ValueError(f"Failed to connect to MongoDB: {str(e)}")

# # Cloudinary configuration
# CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
# CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
# CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# try:
#     if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
#         logger.error("One or more Cloudinary environment variables are not set")
#         raise ValueError("One or more Cloudinary environment variables are not set")
    
#     cloudinary.config(
#         cloud_name=CLOUDINARY_CLOUD_NAME,
#         api_key=CLOUDINARY_API_KEY,
#         api_secret=CLOUDINARY_API_SECRET
#     )
#     cloudinary.api.ping()  # Test Cloudinary connection
#     logger.info("Successfully connected to Cloudinary")
# except Exception as e:
#     logger.error(f"Failed to configure Cloudinary: {str(e)}", exc_info=True)
#     logger.warning("Cloudinary is not configured. Image upload will be disabled.")

# # Example endpoint (add your existing endpoints here)
# @app.get("/testingDone")
# async def testing_done():
#     return {"message": "Testing Done! 🚀"}

# @app.post("/upload_image")
# async def upload_image(file: UploadFile = File(...)):
#     try:
#         # Upload to Cloudinary
#         upload_result = cloudinary.uploader.upload(file.file, folder="attendance_system")
#         image_url = upload_result.get("secure_url")
#         return {"image_url": image_url}
#     except Exception as e:
#         logger.error(f"Image upload failed: {str(e)}")
#         return {"detail": f"Image upload failed: {str(e)}"}

# Add your /upload_image, /signup, /post, etc., endpoints here
# from fastapi import FastAPI, HTTPException, Body, File, UploadFile
# from datetime import datetime
# from pydantic import BaseModel
# from pymongo import MongoClient
# import bcrypt
# import certifi
# import os
# import cloudinary.uploader  # type: ignore
# from dotenv import load_dotenv
# import cloudinary
# import cloudinary.uploader  # type: ignore
# import cloudinary.uploader
# import cloudinary.api
# import logging

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# app = FastAPI()

# # MongoDB connection
# MONGO_URI = os.getenv("MONGO_URI")
# if not MONGO_URI:
#     logger.error("MONGO_URI environment variable not set")
#     raise ValueError("MONGO_URI environment variable not set")

# try:
#     client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=60000)
#     client.admin.command("ping")  # Test connection
#     logger.info("Successfully connected to MongoDB")
# except Exception as e:
#     logger.error(f"Failed to connect to MongoDB: {str(e)}", exc_info=True)
#     raise ValueError(f"Failed to connect to MongoDB: {str(e)}")

# # Select database and collections
# db = client["attendance_system"]
# users_collection = db["users"]
# attendance_collection = db["attendance"]
# post_collection = db["post"]

# # Cloudinary configuration
# cloudinary.config(
#     cloud_name=os.getenv("puzzleApp"),
#     api_key=os.getenv("665944475181268"),
#     api_secret=os.getenv("HAbYE1y7-wP1BOcB6aXrsey-Q7M")
# )

# cloudinary_configured = False
# try:
#     if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
#         logger.error("One or more Cloudinary environment variables are missing")
#         raise ValueError("Cloudinary environment variables are not set")
    
#     cloudinary.config(
#         cloud_name=CLOUDINARY_CLOUD_NAME,
#         api_key=CLOUDINARY_API_KEY,
#         api_secret=CLOUDINARY_API_SECRET
#     )
#     # Test Cloudinary connection
#     cloudinary.api.ping()
#     logger.info("Successfully connected to Cloudinary")
#     cloudinary_configured = True
# except Exception as e:
#     logger.error(f"Failed to configure Cloudinary: {str(e)}", exc_info=True)
#     # Allow the app to start even if Cloudinary fails
#     logger.warning("Cloudinary is not configured. Image upload will be disabled.")

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

# # Signup API
# @app.post("/signup")
# def signup(name: str = Body(...), email: str = Body(...), password: str = Body(...)):
#     """Register a new user with hashed password"""
#     try:
#         if users_collection.find_one({"email": email}):
#             raise HTTPException(status_code=400, detail="User already exists")
        
#         hashed_password = hash_password(password)
#         new_user = {"name": name, "email": email, "password": hashed_password}
#         users_collection.insert_one(new_user)
        
#         return {
#             "status": "success",
#             "message": "User registered successfully!",
#             "user": {"name": name, "email": email}
#         }
#     except Exception as e:
#         logger.error(f"Signup error: {str(e)}", exc_info=True)
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
#     return {"message": f"Welcome {user['name']}! Login successful."}

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
#         logger.error(f"Search error: {str(e)}", exc_info=True)
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

# # Updated Post model
# class PostData(BaseModel):
#     name: str
#     email: str
#     postText: str
#     address: str
#     city: str
#     image_url: str | None = None  # Optional image URL field

# # Helper to serialize MongoDB document
# def serialize_doc(doc):
#     doc["_id"] = str(doc["_id"])
#     return doc

# # Image upload API
# @app.post("/upload_image")
# async def upload_image(file: UploadFile = File(...)):
#     """Upload an image to Cloudinary and return the URL"""
#     if not cloudinary_configured:
#         logger.error("Cloudinary is not configured, cannot upload image")
#         raise HTTPException(status_code=503, detail="Image upload is disabled due to Cloudinary configuration failure")
    
#     try:
#         logger.debug(f"Uploading file: {file.filename}, content_type: {file.content_type}, size: {file.size} bytes")
        
#         # Validate file type
#         if not file.content_type.startswith("image/"):
#             logger.warning(f"Invalid file type: {file.content_type}")
#             raise HTTPException(status_code=400, detail="File must be an image (e.g., jpg, png)")
        
#         # Validate file size (max 10MB for Cloudinary free tier)
#         max_size = 10 * 1024 * 1024  # 10MB in bytes
#         if file.size > max_size:
#             logger.warning(f"File too large: {file.size} bytes, max allowed: {max_size} bytes")
#             raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
#         # Upload file to Cloudinary
#         upload_result = cloudinary.uploader.upload(
#             file.file,
#             folder="attendance_system",
#             resource_type="image"
#         )
#         logger.debug(f"Cloudinary upload response: {upload_result}")
        
#         # Get the secure URL of the uploaded image
#         image_url = upload_result.get("secure_url")
#         if not image_url:
#             logger.error("Cloudinary did not return a secure URL")
#             raise HTTPException(status_code=500, detail="Failed to retrieve image URL from Cloudinary")
        
#         return {"image_url": image_url}
#     except Exception as e:
#         logger.error(f"Image upload failed: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

# # Updated Create post API
# @app.post("/post")
# def create_post(posting: PostData):
#     """Create a new post with optional image URL"""
#     try:
#         logger.debug(f"Creating post: {posting.dict()}")
#         result = post_collection.insert_one(posting.dict())
#         new_post = post_collection.find_one({"_id": result.inserted_id})
#         return serialize_doc(new_post)
#     except Exception as e:
#         logger.error(f"Post creation failed: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Post creation failed: {str(e)}")

# # Search post API
# @app.get("/post/{name}")
# def post_search(name: str):
#     """Search post by name"""
#     post = post_collection.find_one({"name": name})
#     if not post:
#         raise HTTPException(status_code=404, detail=f"No post found for '{name}'")
#     return serialize_doc(post)

# # Get all posts API
# @app.get("/posts")
# def get_all_posts():
#     """Get all posts"""
#     posts = list(post_collection.find())
#     return {
#         "total_posts": len(posts),
#         "posts": [serialize_doc(post) for post in posts]
#     }

from fastapi import FastAPI, HTTPException, Body, File, UploadFile
from datetime import datetime
from pydantic import BaseModel
from pymongo import MongoClient
import bcrypt
import certifi
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Load environment variables
load_dotenv()

app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set")

try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=60000)
    client.admin.command("ping")  # Test connection
except Exception as e:
    raise ValueError(f"Failed to connect to MongoDB: {str(e)}")

# Select database and collections
db = client["attendance_system"]
users_collection = db["users"]
attendance_collection = db["attendance"]
post_collection = db["post"]

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    raise ValueError("Cloudinary environment variables not set")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

# Helper functions
def hash_password(password: str) -> str:
    """Hash the password using bcrypt and return as string"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify the entered password with stored hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode())

# Root route
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
def signup(name: str = Body(...), email: str = Body(...), password: str = Body(...)):
    """Register a new user with hashed password"""
    try:
        if users_collection.find_one({"email": email}):
            raise HTTPException(status_code=400, detail="User already exists")
        
        hashed_password = hash_password(password)
        new_user = {"name": name, "email": email, "password": hashed_password}
        users_collection.insert_one(new_user)
        
        return {
            "status": "success",
            "message": "User registered successfully!",
            "user": {"name": name, "email": email}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")

# Login API
@app.post("/login")
def login(email: str = Body(...), password: str = Body(...)):
    """Login user by verifying email and password"""
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"message": f"Welcome {user['name']}! Login successful."}

# Home screen API
@app.get("/users")
def get_users():
    """Show all registered users (Home Screen)"""
    users = list(users_collection.find({}, {"_id": 0, "password": 0}))
    return {"total_users": len(users), "users": users}

# Mark attendance API
@app.post("/mark_attendance")
def mark_attendance(email: str = Body(...)):
    """Mark attendance for a logged-in user"""
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

# View attendance API
@app.get("/attendance/{email}")
def view_user_attendance(email: str):
    """View attendance records for a specific user by email"""
    records = list(attendance_collection.find({"email": email}, {"_id": 0}))
    if not records:
        raise HTTPException(status_code=404, detail=f"No attendance found for {email}")
    return {"total_records": len(records), "attendance": records}

# Delete user API
@app.delete("/users/{email}")
def delete_user(email: str):
    """Delete a user by email"""
    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User '{email}' deleted successfully"}

# Update user name API
@app.put("/users/{email}")
def update_user_name(email: str, name: str = Body(...)):
    """Update only the user's name"""
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = users_collection.update_one({"email": email}, {"$set": {"name": name}})
    if result.modified_count == 0:
        return {"message": "Name is already the same, nothing changed"}
    return {"message": f"User '{email}' name updated to '{name}'"}

# Filter user name API
@app.get("/users/filter/{name}")
def userSearch(name: str):
    """
    🔍 Search users by name (case-insensitive)
    """
    try:
        users = list(users_collection.find({"name": {"$regex": name, "$options": "i"}}, {"_id": 0, "password": 0}))
        
        if not users:
            raise HTTPException(status_code=404, detail=f"No users found with name containing '{name}'")
        
        return {"total_users": len(users), "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# User count API
@app.get("/users/count")
def user_count():
    """Get total number of registered users"""
    count = users_collection.count_documents({})
    return {"total_users": count}

# Attendance count API
@app.get("/attendance/count")
def attendance_count():
    """Get total number of attendance records"""
    count = attendance_collection.count_documents({})
    return {"total_attendance_records": count}

# Post model
class PostData(BaseModel):
    name: str
    email: str
    postText: str
    address: str
    city: str

# Helper to serialize MongoDB document
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Create post API
@app.post("/post")
def post(posting: PostData):
    """Create a new post"""
    result = post_collection.insert_one(posting.dict())
    new_post = post_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_post)

# Search post API
@app.get("/post/{name}")
def post_search(name: str):
    """Search post by name"""
    post = post_collection.find_one({"name": name})
    if not post:
        raise HTTPException(status_code=404, detail=f"No post found for '{name}'")
    return serialize_doc(post)

# Get all posts API
@app.get("/posts")
def getallPost():
    """Get all posts"""
    posts = list(post_collection.find())
    return {
        "total_posts": len(posts),
        "posts": [serialize_doc(post) for post in posts]
    }

# Image upload API
@app.post("/upload_image")
async def upload_image(email: str = Body(...), file: UploadFile = File(...)):
    """Upload an image to Cloudinary for a user"""
    try:
        # Verify user exists
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, and GIF are allowed.")

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder="attendance_system",
            public_id=f"{email}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            resource_type="image"
        )

        # Store image metadata in MongoDB
        image_record = {
            "email": email,
            "name": user["name"],
            "image_url": upload_result["secure_url"],
            "public_id": upload_result["public_id"],
            "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db["images"].insert_one(image_record)

        return {
            "message": f"Image uploaded successfully for {user['name']}",
            "image_url": upload_result["secure_url"],
            "upload_time": image_record["upload_time"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload error: {str(e)}")

# from fastapi import FastAPI, HTTPException, Body
# from datetime import datetime

# from pydantic import BaseModel
# from pymongo import MongoClient
# import bcrypt
# import certifi
# import os
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

# # Signup API
# @app.post("/signup")
# def signup(name: str = Body(...), email: str = Body(...), password: str = Body(...)):
#     """Register a new user with hashed password"""
#     try:
#         if users_collection.find_one({"email": email}):
#             raise HTTPException(status_code=400, detail="User already exists")
        
#         hashed_password = hash_password(password)
#         new_user = {"name": name, "email": email, "password": hashed_password}
#         users_collection.insert_one(new_user)
        
#         return {
#             "status": "success",
#             "message": "User registered successfully!",
#             "user": {"name": name, "email": email}
#         }
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
#     return {"message": f"Welcome {user['name']}! Login successful."}



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



# @app.get("/posts")
# def getallPost():
#     """Get all posts"""
#     posts = list(post_collection.find())
#     return {
#             "total_posts": len(posts),
#         "posts": [serialize_doc(posts) for post in posts]
#     }