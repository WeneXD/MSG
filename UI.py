import tkinter as tk
from tkinter import font
import requests as req
import time as t

ip="localhost"
port="8000"
addr=f'http://{ip}:{port}'
token=""

class mainFrame(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("512x384")
        self.minsize(512,384)
        self.maxsize(512,384)

        self.title_font=font.Font(family="Helvetica",size="24",weight="bold")

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

class StartPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller=controller
        Title=tk.Label(self,text="Room list",font=controller.title_font)
        Title.grid(column=0,row=0)
        
        self.RoomList=tk.Listbox(self)
        
        self.RoomList.config(width=50)
        self.RoomList.grid(column=0,row=1,sticky="W",pady=5)

        #button1=tk.Button(self,text="Join Room",command=lambda:controller.show_frame("Room"))
        #button2=tk.Button(self,text="Credits",command=lambda:controller.show_frame("Credits"))
        bt_clearRoomList=tk.Button(self,text="Refresh",command=self.refresh_list)

        #button1.grid(column=0,row=1,sticky="W")
        #button2.grid(column=0,row=2,sticky="W")
        bt_clearRoomList.grid(column=0,row=2)

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
                    self.RoomList.insert(int(id),f"{rm[0]} | {rm[1]} (Req pass)")

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