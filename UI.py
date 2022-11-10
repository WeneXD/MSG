import tkinter as tk
from tkinter import font
import requests as req
import time as t

ip="localhost"
port="8000"
addr=f'http://{ip}:{port}'
token="mo"

class mainFrame(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("MSG | Roomlist")
        self.wm_attributes("-toolwindow",'True')
        self.geometry("512x384")
        self.minsize(512,384)
        self.maxsize(512,384)

        self.title_font=font.Font(family="Javanese Text",size="24",weight="bold")
        self.im_font=font.Font(family="Javanese Text",size="12",weight="bold")
        self.alert_font=font.Font(family="KacstBook",size="8")
        self.name_vcmd=(self.register(self.name_validate),'%P')

        container=tk.Frame(self,width=512,height=384)
        container.pack(side="top",fill="both",expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        self.frames={}
        for F in (StartPage,Room,Credits):
            page_name=F.__name__
            frame=F(parent=container,controller=self)
            self.frames[page_name]=frame

            frame.grid(row=0,column=0,sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self,page_name):
        frame=self.frames[page_name]
        frame.tkraise()
    
    def name_validate(self,P):
        if len(P)>=16:
            return False
        if len(P)<16:
            return True
    

class StartPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller=controller
        Title=tk.Label(self,text="Room list",font=controller.title_font)
        Title.grid(column=0,row=0)

        #Name Label & Entrybox
        name_label=tk.Label(self,text="Name",font=controller.im_font)
        name_label.place(height=20,width=50,x=310,y=100)
        self.name_entry=tk.Entry(self,validate="key",validatecommand=controller.name_vcmd)
        self.name_entry.place(x=310,y=115)
        #Room Password Label & Entrybox
        rmPW_label=tk.Label(self,text="Room Password",font=controller.im_font)
        rmPW_label.place(height=20,width=125,x=310,y=150)
        self.rmPW_entry=tk.Entry(self)
        self.rmPW_entry.place(x=310,y=165)
        #Join Button
        join_button=tk.Button(self,text="Join",command=self.join_room)
        join_button.place(x=310,y=190)
        #Alert Label
        self.alert_label=tk.Label(self,text="",font=controller.alert_font)
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

        resp=req.get(addr+"/get_rooms/")
        meow=resp.json()
        if 'err' in meow:
            self.RoomList.insert(1,"(No Rooms, try creating one)")
        else:
            for id,rm in meow.items():
                if not rm[2]:
                    self.RoomList.insert(int(id),f"{rm[0]} | {rm[1]}")
                else:
                    self.RoomList.insert(int(id),f"{rm[0]} | {rm[1]} | req pass")

    def join_room(self):
        name=self.name_entry.get()
        if len(name)==0:
            self.alert_label.config(text="Error: Insert name")
            return
        rmPW=self.rmPW_entry.get()
        rmSelect=self.RoomList.get(tk.ACTIVE)
        if rmSelect=="(No Rooms, try creating one)":
            return
        room=rmSelect.split(" | ")
        if len(room)==3:
            resp=req.post(addr+f"/join_room/?roomID={room[0]}&name={name}&pw={rmPW}")
        else:
            resp=req.post(addr+f"/join_room/?roomID={room[0]}&name={name}")
        meow=resp.json()
        print(meow)
        if 'err' in meow:
            self.alert_label.config(text=f"Error: {meow['err']}")
            return
        self.alert_label.config(text="Successfully joined")
        token=meow['token']
        

class Room(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller=controller
        Title=tk.Label(self,text="Room",font=controller.title_font)
        Title.grid(column=0,row=0)
        button = tk.Button(self,text="Leave room",command=lambda: controller.show_frame("StartPage"))
        
        button.grid(column=0,row=1,sticky="W")

class Credits(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller=controller
        Title=tk.Label(self,text="Credits",font=controller.title_font)
        Title.grid(column=0,row=0)
        button = tk.Button(self,text="Leave credits",command=lambda: controller.show_frame("StartPage"))
        button.grid(column=0,row=1,sticky="W")


if __name__=="__main__":
    app=mainFrame()
    app.mainloop()
