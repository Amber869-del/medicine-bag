import json, os, shutil, subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, quote
import urllib.request
ROOT=os.path.dirname(os.path.abspath(__file__)); HLS=os.path.join(ROOT,'work','hls'); os.makedirs(HLS,exist_ok=True); proc=None
class Handler(SimpleHTTPRequestHandler):
 def do_POST(self):
  global proc
  n=int(self.headers.get('Content-Length','0')); data=json.loads(self.rfile.read(n)); p=urlparse(self.path).path
  if p=='/api/stream/start':
   try:
    rtsp=str(data.get('url','')); 
    if not rtsp.lower().startswith('rtsp://'): raise ValueError('RTSP 位址格式不正確')
    if not shutil.which('ffmpeg'): raise RuntimeError('找不到 FFmpeg')
    if proc and proc.poll() is None: proc.terminate()
    for f in os.listdir(HLS):
     try: os.remove(os.path.join(HLS,f))
     except OSError: pass
    proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-rtsp_transport','tcp','-i',rtsp,'-an','-c:v','copy','-f','hls','-hls_time','1','-hls_list_size','4','-hls_flags','delete_segments+append_list',os.path.join(HLS,'live.m3u8')],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)); self.reply({'playlist':'/hls/live.m3u8'})
   except Exception as e:self.reply({'error':str(e)},400)
  elif p=='/api/google-image':
   try:
    name=str(data.get('name','')); key=str(data.get('key','')); cx=str(data.get('cx',''))
    if not key or not cx: self.reply({'image':None}); return
    u='https://www.googleapis.com/customsearch/v1?key='+quote(key)+'&cx='+quote(cx)+'&searchType=image&num=5&q='+quote(name+' 藥品')
    with urllib.request.urlopen(u,timeout=15) as r: items=json.load(r).get('items',[])
    self.reply({'image':items[0].get('link') if items else None})
   except Exception as e:self.reply({'image':None,'error':str(e)})
  else:self.send_error(404)
 def reply(self,x,code=200):
  b=json.dumps(x,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def translate_path(self,p):
  p=urlparse(p).path
  if p.startswith('/hls/'):return os.path.join(HLS,p[5:])
  return os.path.join(ROOT,p.lstrip('/') or 'index.html')
 def log_message(self,*a):pass
print('網站：http://localhost:8081');ThreadingHTTPServer(('localhost',8081),Handler).serve_forever()
