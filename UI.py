import tkinter as tk
from tkinter import font
import requests as req
import time as t
import threading as th
import base64

#https://stackoverflow.com/a/7557028
#Used as a template

ip="127.0.0.1"
port="8000"
addr=f'http://{ip}:{port}'

def b64(x,y):
    if x=="enc": mBytes=y.encode("utf-8"); b64Bytes=base64.b64encode(mBytes); return b64Bytes.decode("utf-8")
    elif x=="dec": b64Bytes=y.encode("utf-8"); mBytes=base64.b64decode(b64Bytes); return mBytes.decode("utf-8")

class mainFrame(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("MSG")
        self.geometry("512x384")
        self.minsize(512,384)
        self.maxsize(512,384)
        self.roomName=""
        self.roomID="0"
        self.roomPW=""
        self.userID="0"
        self.token=""

        self.title_font=font.Font(family="Javanese Text",size="24",weight="bold")
        self.im_font=font.Font(family="Javanese Text",size="12",weight="bold")
        self.alert_font=font.Font(family="KacstBook",size="8")
        self.name_vcmd=(self.register(self.name_validate),'%P')
        self.rmname_vcmd=(self.register(self.rmname_validate),'%P')
        self.msg_vcmd=(self.register(self.msg_validate),'%P')

        container=tk.Frame(self,width=512,height=384)
        container.pack(side="top",fill="both",expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        self.frames={}
        for F in (Roomlist,Room,Room_Users):
            page_name=F.__name__
            frame=F(parent=container,cont=self)
            self.frames[page_name]=frame

            frame.grid(row=0,column=0,sticky="nsew")

        self.show_frame("Roomlist")

    def show_frame(self,page_name):
        frame=self.frames[page_name]
        frame.tkraise()
    
    def name_validate(self,P):
        if len(P)>=16:
            return False
        if len(P)<16:
            return True

    def rmname_validate(self,P):
        if len(P)>=26:
            return False
        if len(P)<26:
            return True

    def msg_validate(self,P):
        if len(P)>=151:
            return False
        if len(P)<151:
            return True
    
class Roomlist(tk.Frame):
    def __init__(self,parent,cont):
        tk.Frame.__init__(self,parent)
        self.cont=cont
        Title=tk.Label(self,text="Room list",font=cont.title_font)
        Title.grid(column=0,row=0)

        ### USER
        #Name Label & Entrybox
        name_label=tk.Label(self,text="Name",font=cont.im_font)
        name_label.place(height=20,width=50,x=310,y=85)
        self.name_entry=tk.Entry(self,validate="key",validatecommand=cont.name_vcmd)
        self.name_entry.place(x=310,y=100,width=175)

        #Room Password Label & Entrybox
        usPW_label=tk.Label(self,text="Room Password",font=cont.im_font)
        usPW_label.place(height=20,width=125,x=310,y=135)
        self.usPW_entry=tk.Entry(self)
        self.usPW_entry.place(x=310,y=150,width=175)

        #Join Button
        join_button=tk.Button(self,text="Join",command=self.join_room)
        join_button.place(x=310,y=175)

        ### ROOM CREATION
        #Room Name Label & Entrybox
        rmname_label=tk.Label(self,text="Room Name",font=cont.im_font)
        rmname_label.place(height=20,width=95,x=410,y=260)
        self.rmname_entry=tk.Entry(self,validate="key",validatecommand=cont.rmname_vcmd)
        self.rmname_entry.place(x=325,y=275,width=175)

        #Room Password Label & Entrybox
        rmPW_label=tk.Label(self,text="Room Password",font=cont.im_font)
        rmPW_label.place(height=20,width=125,x=380,y=310)
        self.rmPW_entry=tk.Entry(self)
        self.rmPW_entry.place(x=325,y=325,width=175)

        #Room Create Button
        create_button=tk.Button(self,text="Create & Join",command=self.create_room)
        create_button.place(x=420,y=350)

        #Alert Label
        self.alert_label=tk.Label(self,text="",font=cont.alert_font)
        self.alert_label.place(x=0,y=360)

        #Roomlist
        self.RoomList=tk.Listbox(self)
        self.refresh_list()

        #Setting up Roomlist
        self.RoomList.config(width=50)
        self.RoomList.grid(column=0,row=1,sticky="W",pady=5)

        #button2=tk.Button(self,text="Credits",command=lambda:controller.show_frame("Credits"))
        bt_clearRoomList=tk.Button(self,text="Refresh",command=self.refresh_list)

        #button2.grid(column=0,row=2,sticky="W")
        bt_clearRoomList.grid(column=0,row=2,pady=10)

    def refresh_list(self):
        self.RoomList.delete(0,tk.END) #Clear roomlist
        try:    #Send request to server.
            resp=req.get(addr+"/get_rooms/")
            resp.raise_for_status()
        except (req.exceptions.ConnectionError, req.exceptions.Timeout):    #Server timed out/Server down  
            self.RoomList.insert(1,"(Timed out/Server Down)")
            self.cont.title("MSG (Server down)")
            return
        except req.exceptions.HTTPError:    #False request
            self.RoomList.insert(1,"(HTTP Error)")
            return
        else:   #Got an answer from the server.
            self.cont.title("MSG")
            meow=resp.json()
            if 'err' in meow:
                self.RoomList.insert(1,"(No Rooms, try creating one)")
            else:
                for id,rm in meow.items():
                    if not rm[2]:
                        self.RoomList.insert(int(id),f"{rm[0]} | {rm[1]}")
                    else:
                        self.RoomList.insert(int(id),f"{rm[0]} | {rm[1]} | req pass")

    def create_room(self):
        if len(self.cont.token)!=0:
            print("TAB Out Of Bounds")
            return
        username=self.name_entry.get()
        name=self.rmname_entry.get()
        pw=self.rmPW_entry.get()
        if len(name)==0: #Check if user has given a room name.
            self.alert_label.config(text="Error: Insert Room Name")
            return
        if len(username)==0:
            self.alert_label.config(text="Error: Insert Username")
            return
        try:    #Send request to server.
            if len(pw)!=0: #Check if user has given a room password.
                resp=req.post(addr+f"/make_room/?name={name}&username={username}&pw={pw}")
            else:
                resp=req.post(addr+f"/make_room/?name={name}&username={username}")
            resp.raise_for_status()
        except (req.exceptions.ConnectionError, req.exceptions.Timeout):    #Server timed out/Server down
            self.alert_label.config(text="Error: Timed out/Server down")
            return
        except req.exceptions.HTTPError:    #False request
            self.alert_label.config(text="Error: HTTP Error")
            return
        else: #Got an answer from the server.
            meow=resp.json()
            if 'err' in meow:
                self.alert_label.config(text=f"Error: {meow['err']}")
                return
            self.cont.roomName,self.cont.roomPW,self.cont.roomID,self.cont.userID,self.cont.token=meow['name'],pw,meow['roomID'],meow['userID'],meow['token']
            self.cont.frames['Room'].alert_label.config(text=f"Room [{self.cont.roomName}] succesfully created!")
            self.cont.title(f"MSG | Room [{self.cont.roomName}]")
            self.cont.frames['Room'].auto_refresh_activate()
            self.cont.show_frame("Room")

    def join_room(self):
        if len(self.cont.token)!=0:
            print("TAB Out Of Bounds")
            return
        name=self.name_entry.get()
        if len(name)==0: #Check if user has given himself a name.
            self.alert_label.config(text="Error: Insert name")
            return
        usPW=self.usPW_entry.get()
        rmSelect=self.RoomList.get(tk.ACTIVE)
        if rmSelect=="(No Rooms, try creating one)":
            return
        room=rmSelect.split(" | ")
        try:    #Send request to server.
            if len(room)==3:
                resp=req.post(addr+f"/join_room/?roomID={room[0]}&name={name}&pw={usPW}")
            else:
                resp=req.post(addr+f"/join_room/?roomID={room[0]}&name={name}")
            resp.raise_for_status()
        except (req.exceptions.ConnectionError, req.exceptions.Timeout):    #Server timed out/Server down
            self.alert_label.config(text="Error: Timed out/Server down")
            return
        except req.exceptions.HTTPError:    #False request
            self.alert_label.config(text="Error: HTTP Error")
            return
        else:   #Got an answer from the server.
            meow=resp.json()
            print(meow)
            if 'err' in meow:
                self.alert_label.config(text=f"Error: {meow['err']}")
                return
            self.cont.frames['Room'].alert_label.config(text="Successfully joined")
            self.cont.roomID,self.cont.roomName,self.cont.userID,self.cont.token=room[0],room[1],meow['userID'],meow['token']
            if len(room)==3:
                self.cont.roomPW=usPW
            self.cont.title(f"MSG | Room [{self.cont.roomName}]")
            self.cont.frames['Room'].auto_refresh_activate()
            self.cont.show_frame("Room")

class Room(tk.Frame):
    def __init__(self,parent,cont):
        tk.Frame.__init__(self,parent)
        self.cont=cont

        self.msgEvent=th.Event()
        self.msgThread=th.Thread(target=self.auto_refresh)

        #MESSAGE BOX
        self.msg_box=tk.Text(self)
        self.msg_box.place(x=2,y=2,width=508,height=320)
        self.msg_box.config(state=tk.DISABLED)

        #MESSAGE ENTRYBOX
        self.msg_entry=tk.Entry(self,validate="key",validatecommand=cont.msg_vcmd)
        self.msg_entry.place(x=2,y=324,width=460,height=20)

        #MESSAGE SEND BUTTON
        self.msg_button=tk.Button(self,text="=>",command=self.msg_send)
        self.msg_button.place(x=464,y=324,width=45,height=20)

        #ALERT LABEL
        self.alert_label=tk.Label(self,text="",font=cont.alert_font)
        self.alert_label.place(x=43,y=360)

        #LEAVE BUTTON
        leave_button = tk.Button(self,text="Leave",command=self.leave_room)
        leave_button.place(x=2,y=355)

        #USERS BUTTON
        users_button = tk.Button(self,text="Users",command=self.userlist)
        users_button.place(x=470,y=355)

    def leave_room(self):
        try:    #Send request to server.
            resp=req.post(addr+f"/leave_room/?roomID={self.cont.roomID}&token={self.cont.token}")
            resp.raise_for_status()
        except (req.exceptions.ConnectionError, req.exceptions.Timeout):    #Server timed out/Server down
            self.cont.frames['Roomlist'].alert_label.config(text="Error: Timed out/Server down")
            self.auto_refresh_deactivate()
            self.cont.frames['Roomlist'].refresh_list()
            self.cont.token=""
            self.cont.show_frame("Roomlist")
            return
        except req.exceptions.HTTPError:    #False request
            self.alert_label.config(text="Error: HTTP Error")
            return
        else:   #Got an answer from the server.
            meow=resp.json()
            if 'err' in meow:
                self.cont.frames['Roomlist'].alert_label.config(text=f"Error: {meow['err']}")
            self.auto_refresh_deactivate()
            self.cont.frames['Roomlist'].refresh_list()
            self.cont.token=""
            self.cont.show_frame("Roomlist")

    def msg_send(self):
        msg=b64("enc",self.msg_entry.get())
        if len(msg)==0:
            self.alert_label.config(text="Error: Cannot send empty message.")
            return
        try:    #Send request to server.
            if len(self.cont.roomPW)==0:
                resp=req.post(addr+f"/post_msg/?roomID={self.cont.roomID}&token={self.cont.token}&msg={msg}")
            else:
                resp=req.post(addr+f"/post_msg/?roomID={self.cont.roomID}&token={self.cont.token}&msg={msg}&pw={self.cont.roomPW}")
            resp.raise_for_status()
        except (req.exceptions.ConnectionError, req.exceptions.Timeout):    #Server timed out/Server down  
            self.cont.title(f"MSG | Room: {self.cont.roomName} (Timed out/Server down)")
            self.alert_label.config(text="Error: Timed out/Server down")
            return
        except req.exceptions.HTTPError:    #False request
            self.alert_label.config(text="(HTTP Error)")
            return
        else:   #Got an answer from the server.
            meow=resp.json()
            if 'err' in meow:
                self.alert_label.config(text=f"Error: {meow['err']}")
                return
            self.msg_entry.delete(0,tk.END)
            self.msg_refresh()

    def msg_refresh(self):
        try:    #Send request to server.
            if len(self.cont.roomPW)==0:
                resp=req.get(addr+f"/get_msg/?roomID={self.cont.roomID}&token={self.cont.token}")
            else:
                resp=req.get(addr+f"/get_msg/?roomID={self.cont.roomID}&token={self.cont.token}&pw={self.cont.roomPW}")
            resp.raise_for_status()
        except (req.exceptions.ConnectionError, req.exceptions.Timeout):    #Server timed out/Server down  
            self.cont.title(f"MSG | Room: [{self.cont.roomName}] (Timed out/Server down)")
            self.alert_label.config(text="Error: Timed out/Server down")
            return
        except req.exceptions.HTTPError:    #False request
            self.alert_label.config(text="(HTTP Error)")
            return
        else:   #Got an answer from the server.
            meow=resp.json()
            if 'err' in meow:
                self.alert_label.config(text=f"Error: {meow['err']}")
                if meow['err']=="Room not found":
                    self.auto_refresh_deactivate()
                    self.cont.frames['Roomlist'].alert_label.config(text=f"Error: {meow['err']}")
                    self.cont.frames['Roomlist'].refresh_list()
                    self.cont.token=""
                    self.cont.show_frame("Roomlist")
                return
            self.msg_box.config(state=tk.NORMAL)
            self.msg_box.delete('1.0',tk.END)
            for x in meow:
                self.msg_box.insert(tk.END,x)
            self.msg_box.see(tk.END)
            self.msg_box.config(state=tk.DISABLED)
            
    def auto_refresh(self):
        print(self.msgThread)
        while True:
            self.msg_refresh()
            t.sleep(1)
            if self.msgEvent.is_set():
                break
        del self.msgThread
        self.msgThread=th.Thread(target=self.auto_refresh)
        print(self.msgThread)

    def auto_refresh_activate(self):
        self.msgEvent.clear()
        self.msgThread.start()

    def auto_refresh_deactivate(self):
        self.msgEvent.set()

    def userlist(self):
        self.cont.title(f"MSG | Room [{self.cont.roomName}] (Users)")
        self.auto_refresh_deactivate()
        self.cont.frames['Room_Users'].get_users()
        self.cont.frames['Room_Users'].bt_return.forget()
        self.cont.show_frame("Room_Users")

class Room_Users(tk.Frame):
    def __init__(self,parent,cont):
        tk.Frame.__init__(self,parent)
        self.cont=cont
        Title=tk.Label(self,text="Users",font=cont.title_font)
        Title.grid(column=0,row=0)

        #USERLIST
        self.UserList=tk.Listbox(self)
        self.UserList.config(width=50)
        self.UserList.grid(column=0,row=1,sticky="W",pady=5)

        ###USER INFO
        self.UserInfo=tk.Label(self,text="Info",font=self.cont.im_font)
        self.UserInfo.place(x=390,y=75)

        #USER NAME
        self.userName=tk.Label(self,text="Name: ")
        self.userName.place(x=305,y=105)

        #USER MESSAGE AMOUNT
        self.UserMSGs=tk.Label(self,text="Messages: ")
        self.UserMSGs.place(x=305,y=125)

        #USER LAST ACTIVE
        self.UserLastActive=tk.Label(self,text="Last Active: ")
        self.UserLastActive.place(x=305,y=145)

        #FETCH USER INFO BUTTON
        bt_user_info=tk.Button(self,text="Fetch info",command=self.fetch_info)
        bt_user_info.place(x=375,y=190)

        #RETURN BUTTON
        self.bt_return=tk.Button(self,text="Return",command=self.Return)
        self.bt_return.grid(column=0,row=2,pady=10)

        #ALERT LABEL
        self.alert_label=tk.Label(self,text="",font=cont.alert_font)
        self.alert_label.place(x=0,y=360)

    def get_users(self):
        if len(self.cont.token)==0:
            print("TAB Out Of Bounds")
            return
        t.sleep(1) #Tactical Lag :-D "Temporary Fix"
        try:    #Send request to server.
            if len(self.cont.roomPW)==0:
                resp=req.get(addr+f"/get_users/?roomID={self.cont.roomID}")
            else:
                resp=req.get(addr+f"/get_users/?roomID={self.cont.roomID}&pw={self.cont.roomPW}")
            resp.raise_for_status()
        except (req.exceptions.ConnectionError, req.exceptions.Timeout):    #Server timed out/Server down  
            self.cont.title(f"MSG | Room: [{self.cont.roomName}] (Users) (Timed out/Server down)")
            self.alert_label.config(text="Error: Timed out/Server down")
            return
        except req.exceptions.HTTPError:    #False request
            self.alert_label.config(text="(HTTP Error)")
            return
        else:   #Got an answer from the server.
            meow=resp.json()
            self.UserList.delete(0,tk.END)
            if 'err' in meow:
                self.alert_label.config(text=f"Error: {meow['err']}")
                if meow['err']=="Room not found":
                    self.cont.frames['Roomlist'].alert_label.config(text=f"Error: {meow['err']}")
                    self.cont.frames['Roomlist'].refresh_list()
                    self.cont.token=""
                    self.cont.show_frame("Roomlist")
                return
            for user in meow:
                self.UserList.insert(tk.END,user)
            
    def fetch_info(self):
        if len(self.cont.token)==0:
            print("TAB Out Of Bounds")
            return
        userSelect=self.UserList.get(tk.ACTIVE)
        user=userSelect.split(" | ")
        try:    #Send request to server.
            if len(self.cont.roomPW)!=0:
                resp=req.get(addr+f"/get_userinfo/?roomID={self.cont.roomID}&userID={user[0]}&pw={self.cont.roomPW}")
            else:
                resp=req.get(addr+f"/get_userinfo/?roomID={self.cont.roomID}&userID={user[0]}")
            resp.raise_for_status()
        except (req.exceptions.ConnectionError, req.exceptions.Timeout):    #Server timed out/Server down  
            self.alert_label.config(text="Error: Timed out/Server Down")
            self.cont.title(f"MSG | Room [{self.cont.roomName}] (Users) (Timed out/Server Down)")
            return
        except req.exceptions.HTTPError:    #False request
            self.alert_label.config(text="Error: HTTP Error")
            return
        else:   #Got an answer from the server.
            meow = resp.json()
            if 'err' in meow:
                self.alert_label.config(text=f"Error: {meow['err']}")
                if meow['err']=="Room not found":
                    self.cont.frames['Roomlist'].alert_label.config(text=f"Error: {meow['err']}")
                    self.cont.frames['Roomlist'].refresh_list()
                    self.cont.token=""
                    self.cont.show_frame("Roomlist")
                return
            self.userName.config(text=f"Name: {meow['name']}")
            self.UserMSGs.config(text=f"Messages: {meow['msgs']}")
            if meow['lastActivity']<1:
                self.UserLastActive.config(text="Last Active: Just now")
            else:
                self.UserLastActive.config(text=f"Last Active: {meow['lastActivity']} min(s) ago")

    def Return(self):
        self.cont.title(f"MSG | Room [{self.cont.roomName}]")
        self.cont.frames['Room'].auto_refresh_activate()
        self.cont.show_frame('Room')



if __name__=="__main__":
    app=mainFrame()
    app.mainloop()
