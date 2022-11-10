import base64
def b64(x,y):
    if x=="enc": mBytes=y.encode("ascii"); b64Bytes=base64.b64encode(mBytes); return b64Bytes.decode("ascii")
    elif x=="dec": b64Bytes=y.encode("ascii"); mBytes=base64.b64decode(b64Bytes); return mBytes.decode("ascii")