# MSG
Chatroom software programmed in Python 3 with FastAPI and Tkinter.

Server runs on Uvicorn.

## You'll need to have Uvicorn, FastAPI, Requests and Python 3 installed to run this.
To install Uvicorn, FastAPI and Requests run `pip install uvicorn`, `pip install fastapi` and `pip install requests` on command prompt/terminal.

### Installing Python 3
On Windows and Mac head over to [Python's own site](https://www.python.org/downloads/)

On Linux open terminal and run `sudo apt-get install Python3`

## Running the server
To easily test the server out just run the `_server.bat`

Then after starting the server, run `_client.bat`

## Changing the IP Address and Port
To change the IP Address and Port you need to open both `UI.py` and `main.py`.

### `UI.py`
At the top you'll see 2 strings containing both the IP and the port. Those are the variables you'll need to change.

### `main.py`
At the bottom you'll see _uvicorn.run(app,host="localhost",port=8000)_ in which you'll want to change the host and port variables.

## That's all
You should now be all set to use my fun little project in anyway you'd like.
