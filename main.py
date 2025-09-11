
# ------------------- IMPORTS -------------------
from fastapi import FastAPI, HTTPException, Body
from datetime import datetime
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
import os
from pymongo import MongoClient
import bcrypt  # For password hashing
app = FastAPI()
# Get MongoDB URI from environment variable, fallback to localhost if not set
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
# Connect to MongoDB using the URIs
client = MongoClient(MONGO_URI)

# Select your database and collections
db = client["attendance_system"]
users_collection = db["users"]
attendance_collection = db["attendance"]
post_collection = db["post"]
# # ------------------- FASTAPI APP -------------------
# app = FastAPI()

# # ------------------- DATABASE SETUP -------------------
# client = MongoClient("mongodb://localhost:27017/")  # Connect MongoDB
# # MONGO_URI = os.getenv("mongodb+srv://alihassan:<ah7163259>@cluster0.yewcqyy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# # Get MongoDB URI from environment variable (for Vercel / Atlas)
# # client = os.getenv(
# #     "MONGO_URI",  # Environment variable name
# #     "mongodb://localhost:27017/"  # Default local MongoDB fallback
# # )
# db = client["attendance_system"]                   # Database
# users_collection = db["users"]                     # Users collection
# attendance_collection = db["attendance"] 
#             # Users collection
# post_collection = db["post"] # Attendance collection

# ------------------- HELPER FUNCTIONS -------------------
def hash_password(password: str) -> str:
    """Hash the password using bcrypt and return as string"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify the entered password with stored hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode())

# ------------------- ROOT ROUTE -------------------
@app.get("/")
def home():
    """
    🌐 Root endpoint to confirm API is running
    """
    return {"message": "Welcome to the Attendance API! 🚀"}


@app.get("/testingDone")
def Test():
    """
    🌐 Root endpoint to confirm API is running
    """
    return {"message": "Testing Done! 🚀"}

# ------------------- SIGNUP API -------------------


# ya tarika  kar ha params ma value bahjnay k tarika like 
# @app.post("/signup")
# def signup(
#     name: str, email: str, password: str):
#     """
#     👤 Register a new user with hashed password
#     """
#     if users_collection.find_one({"email": email}):
#         raise HTTPException(status_code=400, detail="User already exists")

#     hashed_password = hash_password(password)
#     new_user = {"name": name, "email": email, "password": hashed_password}
#     users_collection.insert_one(new_user)

#     return {"message": "User registered successfully!"}


@app.post("/signup")
def signup(
    name: str = Body(...),
    email: str = Body(...),
    password: str = Body(...)
):
    """
    👤 Register a new user with hashed password
    """
    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(password)
    new_user = {"name": name, "email": email, "password": hashed_password}
    users_collection.insert_one(new_user)

    
    # ✅ Return professional JSON response
    return {
        "status": "success",
        "message": "User registered successfully!",
        "user": {
            "name": name,
            "email": email
        }
    }


# ------------------- LOGIN API -------------------
@app.post("/login")
def login(email: str, password: str):
    """
    🔑 Login user by verifying email and password
    """
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"message": f"Welcome {user['name']}! Login successful."}

# ------------------- HOME SCREEN API -------------------
@app.get("/users")
def get_users():
    """
    🏠 Show all registered users (Home Screen)
    """
    users = list(users_collection.find({}, {"_id": 0, "password": 0}))
    return {"total_users": len(users), "users": users}


# ------------------- MARK ATTENDANCE API -------------------
@app.post("/mark_attendance")
def mark_attendance(email: str):
    """
    📅 Mark attendance for a logged-in user
    """
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

# ------------------- VIEW ATTENDANCE API -------------------
# @app.get("/attendance")
# def view_attendance():
#     """
#     📜 View all attendance records
#     """
#     records = list(attendance_collection.find({}, {"_id": 0}))
#     return {"total_records": len(records), "attendance": records}
@app.get("/attendance/{email}")
def view_user_attendance(email: str):
    """
    📜 View attendance records for a specific user by email
    """
    records = list(attendance_collection.find({"email": email}, {"_id": 0}))
    
    if not records:
        raise HTTPException(status_code=404, detail=f"No attendance found for {email}")
    
    return {"total_records": len(records), "attendance": records}

# ------------------- Delete User -------------------
@app.delete("/users/{email}")
def delete_user(email: str):
    """
    ❌ Delete a user by username
    """
    result = users_collection.delete_one({"email": email})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User '{email}' deleted successfully"}


# ------------------- UPDATE USER NAME API -------------------
@app.put("/users/{email}")
def update_user_name(email: str, name: str):
    """
    ✏️ Update only the user's name
    """
    user = users_collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = users_collection.update_one(
        {"email": email},
        {"$set": {"name": name}}
    )

    if result.modified_count == 0:
        return {"message": "Name is already the same, nothing changed"}

    return {"message": f"User '{email}' name updated to '{name}'"}


# ------------------- Filter USER NAME API -------------------
@app.get("/users/filter/{name}")
def userSearch(name: str):
    """
    🔍 Search users by name (case-insensitive)
    """
    users = list(users_collection.find({"name": {"$regex": name, "$options": "i"}}, {"_id": 0, "password": 0}))
    
    if not users:
        raise HTTPException(status_code=404, detail=f"No users found with name containing '{name}'")
    
    return {"total_users": len(users), "users": users}

@app.get("/users/count")
def user_count():
    """
    📊 Get total number of registered users
    """
    count = users_collection.count_documents({})
    return {"total_users": count}

@app.get("/attendance/count")
def attendace_count():
    """
    📊 Get total number of attendance records
    """
    count = attendance_collection.count_documents({})
    return {"total_attendance_records": count}

# Model
class PostData(BaseModel):
    name: str
    email: str
    postText: str
    address: str
    city: str

# Helper to convert MongoDB document to JSON-serializable dict
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc
# ya simple us model ko return karta ha jo hum ny banaya ha

@app.post("/post")
def post(posting: PostData):
    # Insert the data
    result = post_collection.insert_one(posting.dict())
    
    # Find inserted document
    new_post = post_collection.find_one({"_id": result.inserted_id})
    
    # Return the full document
    return serialize_doc(new_post)


@app.get("/post/{name}")
def postSearch(name: str):
    """
    🔍 Search post by name
    """
    post = post_collection.find_one({"name": name})
    
    if not post:
        raise HTTPException(status_code=404, detail=f"No post found for '{name}'")
    
    return serialize_doc(post)

# serialize_doc(new_post)
    # return serialize_doc(new_post)




# from fastapi import FastAPI, HTTPException, Depends


# app = FastAPI()


# @app.get("/")
# def  name():
#     return {"message": "Syed Ali Mesum Naqvi"}
# @app.get("/father")
# def  fatherName():
#     return {"message": "Syed Ali Kausar Naqvi"}  


# userList = []  # پہلے ایک global list بنا لو


# @app.post("login")
# def login(email: str, password: str):
#     if email.strip() == "" or password.strip() == "":
#         raise HTTPException(status_code=400, detail="Email and Password cannot be empty")
#     elif email=="": 
#         raise HTTPException(status_code=401, detail="Invalid email or password")
#     return {"message": "Login Successful"}

# @app.post("/addUser/{name}")
# def addUser(name: str):
#     userList.append(name)
#     return {"message": f"User {name} added!", "count": len(userList), "users": userList}


# @app.get("/userList")
# def  UserList():
#     return {"message": userList, "count": len(userList)}




# # main.py
# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
# from typing import Dict
# from datetime import datetime

# app = FastAPI()
# security = HTTPBasic()

# # Dummy Users (Admin will create these)
# users_db = {
#     "ali": "1234",
#     "sara": "5678",
#     "ahmed": "abcd"
# }

# # Attendance Records
# attendance_db: Dict[str, list] = {
#     "ali": [],
#     "sara": [],
#     "ahmed": []
# }


# # Authentication function
# def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
#     username = credentials.username
#     password = credentials.password

#     # Check if user exists and password matches
#     if username in users_db and users_db[username] == password:
#         return username
#     raise HTTPException(status_code=401, detail="Invalid username or password")


# # Home Route
# @app.get("/")
# def home():
#     return {"message": "Welcome to the Academy Attendance API"}


# # Mark Attendance
# @app.post("/attendance")
# def mark_attendance(current_user: str = Depends(get_current_user)):
#     today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     attendance_db[current_user].append(today)
#     return {"message": f"Attendance marked for {current_user} at {today}"}


# # View Attendance
# @app.get("/attendance")
# def view_attendance(current_user: str = Depends(get_current_user)):
#     return {"user": current_user, "attendance": attendance_db[current_user]}


# @app.get("/admin/attendance/{username}")
# def admin_view_attendance(username: str, current_user: str = Depends(get_current_user)):
#     if current_user != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")
#     if username not in attendance_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"user": username, "attendance": attendance_db[username]}
    




# a=5;
# b=6;
# print("The sum is:", a+b);
# a, b = 5, 2
# print(a + b, a > b, a == b)
# # name = input("Enter your name: ")

# x=input("Enter a number: ");
# y=input("Enter another number: ");
# print("The sum is:", int(x)+int(y));
# # print("Welcome", name)
# x = 10
# if x > 0:
#     print("Positive")
# elif x == 0:
#     print("Zero")
# else:
#     print("Negative")
    

# for i in range(10+1):
#     print(i)
# class BankAccount:
#     def __init__(self, balance,years):
#         self.__balance = balance 
#         print("Account created with balance:", self.__balance)
#         # private variable

#     def show_balance(self):
#         print("Balance:", self.__balance)
        
        

# acc = BankAccount(1000)


# class AddClass():
#     def __init__(self, a,b):
#         self.a = a
#         self.b = b
        
#     def add(self):
#         return print("Sum =", self.a + self.b);
    
    
#     def subtruct(self):
#         return print("Sum =", self.a - self.b);
    
    
#     def division(self):
#         return print("Sum =", self.a // self.b);
    
    
#     def multiply(self):
#         return print("Sum =", self.a * self.b);
        
        
    
        
# obj=AddClass(5,3)
# obj.add()
# obj.division()
# obj.multiply()


# acc.show_balance()

# bank=BankAccount(5000)
# bank.show_balance()
# print(acc.__balance)  ❌ error: direct access nahi


        

# def add(a, b):
#     print("Sum =", a+b)

# add(5, 3)
# add(10, 7)
# def greet(name):
#     print("Hello", name)
    
    
#     greet("Alice")



# def valueAdd(a,b):
#      print("Sum =", a+b)
     
# valueAdd(4,12)

# for m in range(10):
#     print(m)
# x = 10
# y = 3
# print(x // y)

# for i  in range(0, 30,2):
#     print(i)    
    
# for i in range(1, 11):
#     if i % 2 == 0:
#         print(i, "is even")
#     else:
#         print(i, "is odd")

# source venv/bin/activate




