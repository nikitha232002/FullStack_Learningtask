from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL="sqlite:///./text.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base=declarative_base()

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,index=True)
    email=Column(String,unique=True,index=True)

Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html") as f:
        return f.read()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()   

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode=True

@app.post("/users/",response_model=UserResponse)
def create_user(user: UserCreate , db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[UserResponse])   
def read_users(skip: int=0, limit:int=10, db: Session = Depends(get_db)):
    users=db.query(User).offset(skip).limit(limit).all()
    return users







