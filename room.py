from pydantic import BaseModel
import re
import random as rd
import b64
rd.seed()

room={}

###  CLASSES
class User(BaseModel):
    name:str
    token:str
    msgs:int

class Room(BaseModel):
    class Msg(BaseModel):
        name:str
        text:str
    
    name:str
    pw:str | None=None
    msgs:list[Msg]
    users:dict[str,User]

    def newMsg(self,token,Msg):
        userInRoom=False
        Name="Viljami :-DD"
        if not self.users: #Check if the room even has any users
            return {"out":False,"err":"Room doesn't have any users"}
        
        for us in self.users.values(): #Check if user is in the room
            if us.token==token:
                userInRoom=True
                Name=us.name
        
        if not userInRoom:
            return {"out":False,"err":"User not in room"}
        
        newMSG=self.Msg(name=Name,text=Msg)
        if len(self.msgs)>=31:
            del self.msgs[1]
        self.msgs.append(newMSG)
        return {"out":True}

    def getMsg(self,Token):
        userInRoom=False
        for us in self.users.values(): #Check if user is in the room
            if us.token==Token:
                userInRoom=True

        if not userInRoom:
            return {"out":False,"err":"User not in room."}

        meow=[] #Create a list to contain the messages.
        if not self.msgs:
            meow.append("\tNo messages, try sending one.")
        for msg in self.msgs:
            meow.append(f"\t[{msg.name}]\n"+msg.text)
        return meow

###  ROOMS
def get_rooms():
    if not room: #Check if there are any rooms
        return {"out":False,"err":"no rooms"}
    meow={} #Make dict
    hasPw=False
    for id,rm in room.items():
        if rm.pw is not None:
            hasPw=True
        else: hasPw=False
        meow[len(meow)+1]=[id,rm.name,hasPw] #Fill dict with rooms
    return meow

def make_room(Name,Pw):
    cnt=1
    if len(Name)!=len(re.sub(r"[^a-zA-Z0-9\ \-\_]","",Name)): return {"out":False,"err":"Name contains invalid characters"}       #Check for illegal symbols in room name
    if Pw is not None:
        if len(Pw)!=len(re.sub(r"[^a-zA-Z0-9\-\_\.]","",Pw)): return {"out":False,"err":"Pass contains invalid characters"} #Check for illegal symbols in room password
    if room:
        for id,rm in room.items():
            if int(id)==cnt:cnt+=1 #If room with count ID exists increase count's value.
            if rm.name==Name: #Also check if a room with the same name already exists.
                return {"out":False,"err":"Room with the name already exists"}

    newRoom=Room(name=Name,pw=Pw,users=[],msgs=[]) #Makes a new variable named newRoom which contains the new room.
    room[str(cnt)]=newRoom #Add newRoom to the room dict.
    return {"out":True,"roomID":cnt,"name":Name} #Return a positive outcome, roomID, room name.

def delete_room(rID):
    if rID in room: #Check if room exists
        del room[rID]
        return {"out":True}
    return {"out":False,"err":"No room with current ID"}

def join_room(rID,pw,Name):
    cnt=1
    if rID not in room: #Check if room exists
        return {"out":False,"err":"Room not found"}
    if room[rID].pw is not None: #Check if room has password
        if room[rID].pw!=pw: #Check if password is correct
            return {"out":False,"err":"Password is invalid"}

    if len(Name)!=len(re.sub(r"[^a-zA-Z0-9\-\_]","",Name)): return {"out":False,"err":"Name contains invalid characters"}       #Check for illegal symbols in user's name
    Token=generate_token()
    if room[rID].users:
        for id,us in room[rID].users.items():
            if int(id)==cnt:cnt+=1 #If user with count ID exists increase count's value.
            if us.token==Token:
                Token=generate_token()
            if us.name==Name: #Also check if a user with the same name already exists.
                return {"out":False,"err":"User with the name already exists"}
    
    newUser=User(name=Name, token=Token, msgs=0) #Makes a new variable named newUser which contain the new user.
    room[rID].users[str(cnt)]=newUser #Add newUser to the users dict.
    return {"out":True,"userID":str(cnt),"token":Token}

def leave_room(rID,Token):
    id="wene"
    if rID not in room: #Check if room exists
        return {"out":False,"err":"Room not found"}
    for _id,us in room[rID].users.items():  #Loop through room's userlist
        if us.token==Token: #Check if an user has the correct token
            id=_id
    if id=="wene": #Check if the user was found
        return {"out":False,"err":"User not found"}
    
    del room[rID].users[id] #Delete user from userlist
    if not room[rID].users:
        del room[rID]
    
    return {"out":True}

def get_users(rID,pw):
    if rID not in room: #Check if room even exists.
        return {"out":False,"err":"Room not found"}

    if room[rID].pw is not None: #Check if the room has a password.
        if room[rID].pw!=pw: #Check if the password is correct.
            return {"out":False,"err":"Invalid Password"}
    
    if not room[rID].users: #Check if room has any users.
        return {"out":False,"err":"Room has no users"}
    
    meow=[]  #Create a list to contain the users.
    for id,us in room[rID].users.items(): #Loop through the room
        meow.append(f"{id} | {us.name}")

    return meow

###  MESSAGING
def post_msg(rID,pw,token,msg):
    if rID not in room: #Check if room exists.
        return {"out":False,"err":"Room not found"}
    if room[rID].pw is not None:    #Check if room has a password
        if room[rID]!=pw:   #Check if the password is correct
            return {"out":False,"err":"Invalid Password"}
    
    return room[rID].newMsg(token,msg)

def get_msg(rID,pw,token):
    if rID not in room: #Check if room exists.
        return {"out":False,"err":"Room not found"}
    if room[rID].pw is not None:    #Check if room has a password
        if room[rID]!=pw:   #Check if the password is correct
            return {"out":False,"err":"Invalid Password"}
    
    return room[rID].getMsg(token)

###  OTHER
def generate_token():
    print("gen token")
    rd.seed()
    return b64.b64("enc",str(rd.randint(100000,10000000)))