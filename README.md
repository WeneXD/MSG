# MSG
Chatroom software programmed in Python 3 using Uvicorn, FastAPI and Tkinter.

### Requirements
[Python3](https://www.python.org/downloads/)

Uvicorn `pip install uvicorn`

FastAPI `pip install fastapi`

Requests `pip install requests`

## Running the server
To start the server run `_server.bat`

After that run `_client.bat`

## Changing the IP Address and Port
To change the IP Address and Port you need to open both `UI.py` and `main.py`.

### `UI.py`
At the top you'll see 2 strings containing both the IP and the port.

### `main.py`
At the bottom you'll see `uvicorn.run(app,host="localhost",port=8000)`. Host is the IP address and the port is self-explanatory.

Change the host from `localhost` (LAN) to `0.0.0.0` (WAN) to allow outside clients to connect.
