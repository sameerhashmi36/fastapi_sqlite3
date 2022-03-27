import uvicorn
from fastapi import FastAPI, Depends, Form, Cookie
from pydantic import BaseModel
from sqlalchemy import Boolean, Column,   Integer, String

from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal

from fastapi.responses import Response

from fastapi import Depends


#model
class Users(Base):
    __tablename__='users'
    iid = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, index=True)

#schema
class UsersSchema(BaseModel):
    iid:int 
    email:str 
    password:str

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

app = FastAPI()

async def get_user_by_email(email: str, db: Session):
    return db.query(Users).filter(Users.email == email).first()

@app.post('/register')
async def registerfunc(iid = Form(...), email = Form(...), password = Form(...), db:Session=Depends(get_db)):
    ##### db work to put data into db
    people = Users(iid=iid, email=email, password=password)
    # print("1111111",people)
    db.add(people)
    # print("22222222222",people)
    db.commit()
    db.refresh(people)
    return people

# global flag
# flag = False
@app.post('/login')
async def loginfunc(response : Response, is_login : str =  Cookie(None), email = Form(...), password = Form(...), db:Session=Depends(get_db)):
    if is_login == '1':
        return {"message":"you are already logged in"}

    results = db.query(Users).filter(Users.email == email).first()

    ### creating cookies
    content = {"message":"seesion cookies"}
    # response = JSONResponse(content=content)

    ########    #########
    # NOTE: Working using flag
    # global flag
    ########    #########

    if email == results.email and password == results.password:
        response.set_cookie(key='is_login',value='1')

        ########    #########
        # NOTE: Working using flag
        # flag = True
        ########    #########

        return "You are logged in. Your user id is {}".format(str(results.iid))
    
    ########    #########
    # if not results.email:
    #     raise InvalidCredentialsException
    # elif password != results.password:
    #     raise InvalidCredentialsException
    ########    #########

@app.post("/logout")
async def logout(response : Response, is_login : str =  Cookie(None)):
    print(is_login)
    if is_login=='1':
        # response.set_cookie(key='is_login',value='0')
        response.delete_cookie(key='is_login', domain='127.0.0.1')
        return {"message":"user logged out"}
    else:
        return {"message":"user already logged out"}


    # NOTE: Working using flag
    # global flag
    # if flag != False:
    #     flag = False
    #     response.set_cookie(key='is_login',value='0')
    #     return "Logged Out"
    # else:
    #     flag = False
    #     return "You are already out"



### Testing sqlite3 query access

@app.post("/test")
async def fetch_data(db:Session=Depends(get_db)):
    # print("Hello")
    results = db.query(Users).filter(Users.iid == 1).first()
    return  results.email

####### Run the code using python main.py ########
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8001, debug=True)
