from fastapi import FastAPI
import threading as th
import room as r
from pydantic import BaseSettings

class Settings(BaseSettings):
    openapi_url:str="" #Change the string from "" to "/openapi.json" if you want to re-enable the docs.

settings=Settings()
app=FastAPI(openapi_url=settings.openapi_url)

@app.get("/")
def read_root():
    return "MSG"

@app.get("/get_rooms/")
def get_rooms():
    meow=r.get_rooms()
    return meow

#@app.post("/delete_room/")
#def delete_room(roomID:str):
#   return r.delete_room(roomID)

@app.post("/make_room/")
def make_room(name:str, username:str, pw:str | None=None):
    meow=r.make_room(name,username,pw)
    return meow

@app.post("/join_room/")
def join_room(roomID:str, name:str, pw: str | None=None):
    return r.join_room(roomID,pw,name)

@app.post("/leave_room/")
def leave_room(roomID:str,token:str):
    return r.leave_room(roomID,token)

@app.get("/get_users/")
def get_users(roomID:str,pw:str | None=None):
    return r.get_users(roomID,pw)

@app.get("/get_userinfo/")
def get_userinfo(roomID:str,userID:str,pw:str | None=None):
    return r.get_userinfo(roomID,userID,pw)

@app.post("/post_msg/")
def post_msg(roomID:str, token:str, msg:str, pw:str | None=None):
    return r.post_msg(roomID,pw,token,msg)

@app.get("/get_msg/")
def get_msg(roomID:str, token:str, pw:str | None=None):
    return r.get_msg(roomID,pw,token)

if __name__=="__main__":
    Inactive_RoomThread=th.Thread(target=r.inactive_room)
    Inactive_RoomThread.start()
    import uvicorn
    uvicorn.run(app,host="localhost", port=8000)
