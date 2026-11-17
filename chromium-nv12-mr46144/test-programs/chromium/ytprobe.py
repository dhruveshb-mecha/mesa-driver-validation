#!/usr/bin/env python3
# ytprobe.py URL QUALITY SECONDS : navigate the chromium page (CDP), set YouTube quality, sample <video> playback stats
import socket,base64,os,json,struct,sys,time,urllib.request,subprocess
url,qual,secs=sys.argv[1],sys.argv[2],int(sys.argv[3])
tg=[t for t in json.load(urllib.request.urlopen("http://127.0.0.1:9222/json")) if t["type"]=="page"][0]
host,port,path=("127.0.0.1",9222,tg["webSocketDebuggerUrl"].split("9222",1)[1])
s=socket.create_connection((host,port)); k=base64.b64encode(os.urandom(16)).decode()
s.send(f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {k}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
buf=b""
while b"\r\n\r\n" not in buf: buf+=s.recv(4096)
buf=buf.split(b"\r\n\r\n",1)[1]
def send(o):
    d=json.dumps(o).encode(); m=os.urandom(4); n=len(d)
    h=b"\x81"+(bytes([0x80|n]) if n<126 else b"\xfe"+struct.pack(">H",n) if n<65536 else b"\xff"+struct.pack(">Q",n))
    s.send(h+m+bytes(b^m[i%4] for i,b in enumerate(d)))
def rd(n):
    global buf
    while len(buf)<n: buf+=s.recv(65536)
    r,buf=buf[:n],buf[n:]; return r
def recv():
    while True:
        b0,b1=rd(2); n=b1&0x7f
        if n==126: n=struct.unpack(">H",rd(2))[0]
        elif n==127: n=struct.unpack(">Q",rd(8))[0]
        d=rd(n)
        if b0&0x0f==1: return json.loads(d)
i=0
def call(method,**p):
    global i; i+=1; send({"id":i,"method":method,"params":p})
    while True:
        r=recv()
        if r.get("id")==i: return r
def ev(js):
    r=call("Runtime.evaluate",expression=js,returnByValue=True)
    return r.get("result",{}).get("result",{}).get("value")
call("Page.navigate",url=url); time.sleep(12)
JS_STAT="""(()=>{const v=document.querySelector('video');if(!v)return null;const q=v.getVideoPlaybackQuality();
const p=document.getElementById('movie_player');const ad=p&&p.classList.contains('ad-showing');
return JSON.stringify({t:+v.currentTime.toFixed(1),paused:v.paused,total:q.totalVideoFrames,dropped:q.droppedVideoFrames,w:v.videoWidth,h:v.videoHeight,ad:ad,
 res:p&&p.getPlaybackQuality&&p.getPlaybackQuality(),title:document.title.slice(0,40)})})()"""
ev("(()=>{const v=document.querySelector('video');if(v){v.muted=true;v.play()}})()")
ev(f"(()=>{{const p=document.getElementById('movie_player');if(p&&p.setPlaybackQualityRange){{p.setPlaybackQualityRange('{qual}','{qual}')}}}})()")
t0=time.time(); first=None
while time.time()-t0<secs:
    cpu=subprocess.run("ps -eo pcpu,comm | awk '/chrom/{s+=$1} END{print s}'",shell=True,capture_output=True,text=True).stdout.strip()
    st=ev(JS_STAT); print(f"{time.time()-t0:5.1f}s cpu={cpu} {st}",flush=True)
    time.sleep(5)
