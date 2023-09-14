from pydantic import BaseModel
import re
import random as rd
import base64
import hashlib as hlib
import time as t

rd.seed()

room={}

###  CLASSES
class User(BaseModel):
    name:str
    token:str
    msgs:int=0
    lastActivity:float=t.time()

class Room(BaseModel):
    class Msg(BaseModel):
        name:str
        text:str
        time:str
    
    name:str=""
    pw:str | None=None
    msgs:list[Msg]
    msgTime:float=t.time()
    users:dict[str,User]
    time:float=t.time()

    def newMsg(self,token,Msg):
        userInRoom=False
        Name="Viljami :-DD"
        if not self.users: #Check if the room even has any users
            return {"out":False,"err":"Room doesn't have any users"}
        
        for us in self.users.values(): #Check if user is in the room
            if us.token==token:
                userInRoom=True
                Name=us.name
                us.lastActivity=t.time()
                us.msgs+=1
        
        if not userInRoom:
            return {"out":False,"err":"User not in room"}
        
        self.msgTime=t.time()
        mins=(self.msgTime-self.time)/60
        hours=0
        while mins>59:
            hours+=1
            mins-=60

        newMSG=self.Msg(name=Name,text=b64("dec",Msg),time=f"{int(hours)}:{int(mins)}")
        if len(self.msgs)>=10:
            del self.msgs[0]
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
            meow.append(f"\t{msg.name} [{msg.time}]\n{msg.text}\n")
        return meow

    def getUserInfo(self,uID):
        if str(uID) not in self.users: #Check if an user with the ID exists in the room.
            return {"out":False,"err":"User not found"}
        return {"name":self.users[uID].name, "msgs":self.users[uID].msgs, "lastActivity":int((t.time()-self.users[uID].lastActivity)/60)}

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

def make_room(Name,Username,Pw):
    cnt=1

    if len(Name)==0: return {"out":False,"err":"Room name missing"}
    if len(Name)!=len(re.sub(r"[^a-zA-Z0-9\ \-\_\ä\ö\å\:\;\^]","",Name)): return {"out":False,"err":"Room name contains invalid characters"}       #Check for illegal symbols in room name
    if len(Name)>30: return {"out":False,"err":f"Room's name is too long ({len(Name)}/25)"}

    meow=check_username(Username)
    if not meow["out"]: return meow

    if Pw is not None:
        if len(Pw)!=len(re.sub(r"[^a-zA-Z0-9\-\_\.]","",Pw)): return {"out":False,"err":"Pass contains invalid characters"} #Check for illegal symbols in room password
        Pw=enc_sha256(Pw) #Sha256 Encode the password
    if room:
        for id,rm in room.items():
            if int(id)==cnt:cnt+=1 #If room with count ID exists increase count's value.
            if rm.name==Name: #Also check if a room with the same name already exists.
                return {"out":False,"err":"Room with the name already exists"}

    newRoom=Room(name=Name,pw=Pw,users={},msgs=[],msgTime=t.time()) #Makes a new variable named newRoom which contains the new room.
    room[str(cnt)]=newRoom #Add newRoom to the room dict.
    Token=generate_token()
    newUser=User(name=Username,token=Token)
    room[str(cnt)].users["1"]=newUser
    return {"out":True,"roomID":cnt,"name":Name,"userID":"1","token":Token} #Return a positive outcome, roomID, room name.

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
        if room[rID].pw!=enc_sha256(pw): #Check if password is correct
            return {"out":False,"err":"Password is invalid"}

    meow=check_username(Name)
    if not meow["out"]: return meow
    
    Token=generate_token()
    if room[rID].users:
        for id,us in room[rID].users.items():
            if int(id)==cnt: cnt+=1 #If user with count ID exists increase count's value.
            if str(cnt) in room[rID].users: cnt+=1
            if us.token==Token:
                Token=generate_token()
            if us.name==Name: #Also check if a user with the same name already exists.
                return {"out":False,"err":"User with the name already exists"}
    
    newUser=User(name=Name, token=Token) #Makes a new variable named newUser which contain the new user.
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
        if room[rID].pw!=enc_sha256(pw): #Check if the password is correct.
            return {"out":False,"err":"Invalid Password"}
    
    if not room[rID].users: #Check if room has any users.
        return {"out":False,"err":"Room has no users"}
    
    meow=[]  #Create a list to contain the users.
    for id,us in room[rID].users.items(): #Loop through the room
        meow.append(f"{id} | {us.name}")

    return meow

def get_userinfo(rID,uID,pw):
    if rID not in room: #Check if room exists
        return {"out":False,"err":"Room not found"}
    if room[rID].pw is not None: #Check if room has password
        if room[rID].pw!=enc_sha256(pw): #Check if password is correct
            return {"out":False,"err":"Password is invalid"}
    
    return room[rID].getUserInfo(uID)

def check_username(Username):
    if len(Username)==0: return {"out":False,"err":"Username missing"}
    if len(Username)!=len(re.sub(r"[^a-zA-Z0-9\-\_\ä\ö\å\:\;]","",Username)): return {"out":False,"err":"Username contains invalid characters"}       #Check for illegal symbols in user's name
    if len(Username)!=len(re.sub(r"\s+","",Username)): return {"out":False,"err":"Username contains invalid characters"} 
    if len(Username)>15: return {"out":False,"err":f"Username is too long ({len(Username)}/15)"}
    return {"out":True}

###  MESSAGING
def post_msg(rID,pw,token,msg):
    if rID not in room: #Check if room exists.
        return {"out":False,"err":"Room not found"}
    if room[rID].pw is not None:    #Check if room has a password
        if room[rID].pw!=enc_sha256(pw):   #Check if the password is correct
            return {"out":False,"err":"Invalid Password"}
    
    return room[rID].newMsg(token,msg)

def get_msg(rID,pw,token):
    if rID not in room: #Check if room exists.
        return {"out":False,"err":"Room not found"}
    if room[rID].pw is not None:    #Check if room has a password
        if pw is None:
            return {"out":False,"err":"Room requires a password"}
        if room[rID].pw!=enc_sha256(pw):   #Check if the password is correct
            return {"out":False,"err":"Invalid Password"}
    
    return room[rID].getMsg(token)

###  OTHER
def generate_token():
    rd.seed()
    return enc_sha256(b64("enc",str(rd.randint(100000,10000000))))

def b64(x,y):
    if x=="enc": mBytes=y.encode("utf-8"); b64Bytes=base64.b64encode(mBytes); return b64Bytes.decode("utf-8")
    elif x=="dec": b64Bytes=y.encode("utf-8"); mBytes=base64.b64decode(b64Bytes); return mBytes.decode("utf-8")

def inactive_room():
    while True:
        t.sleep(30)
        if room:
            delList=[]
            print("\n\tScanning for inactive rooms")
            for id,rm in room.items():
                if int(t.time()-rm.msgTime)/60>30:
                    print(f"\troomID:{id} | Name: {rm.name} added to DeleteList")
                    delList.append(id)
            print("\tScan done")
            for x in delList:
                print(f"\tRoom [{room[x].name}] deleted")
                delete_room(x)
            print(f"\tDeleted {len(delList)} room(s)")


#https://medium.com/@dwernychukjosh/sha256-encryption-with-python-bf216db497f9
def enc_sha256(hash_string):
    sha_signature = \
        hlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature
