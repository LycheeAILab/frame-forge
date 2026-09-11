"""Authenticated image client with persistent idempotency and polling."""
import argparse, hashlib, io, json, secrets, time, os
from pathlib import Path
import urllib.request, urllib.error
from urllib.parse import urlparse
from lab_auth import BASE, NoRedirect, authorized_token, AuthError

def reference_png(path):
    if not path: return None
    from PIL import Image, ImageOps
    with Image.open(path) as source:
        if source.width*source.height>40_000_000: raise ValueError('图片尺寸过大')
        buffer=io.BytesIO();ImageOps.exif_transpose(source).convert('RGBA').save(buffer,format='PNG')
    value=buffer.getvalue()
    if len(value)>10*1024*1024: raise ValueError('参考图片超过10MB')
    return value

def multipart(fields,image):
    boundary='FrameForge'+secrets.token_hex(16);parts=[]
    for name,value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    if image: parts.extend([f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="reference.png"\r\nContent-Type: image/png\r\n\r\n'.encode(),image,b'\r\n'])
    parts.append(f'--{boundary}--\r\n'.encode())
    return b''.join(parts),'multipart/form-data; boundary='+boundary

def request(token,path,body=None,kind=None):
    headers={'Authorization':'Bearer '+token}
    if kind: headers['Content-Type']=kind
    try:
        with urllib.request.build_opener(NoRedirect()).open(urllib.request.Request(BASE+path,data=body,headers=headers),timeout=30) as response:
            return json.loads(response.read(1024*1024))
    except urllib.error.HTTPError as error:
        if error.code in (401,403): raise AuthError('Lab 登录已失效，请重新登录') from None
        raise RuntimeError(f'Lab 请求未完成（HTTP {error.code}），保留原任务后重试查询') from None

def write_state(path,value):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value),encoding='utf-8');temp.replace(path)

def download(url,output):
    parsed=urlparse(url)
    if parsed.scheme!='https' or not (parsed.hostname or '').endswith('.myqcloud.com'): raise ValueError('图片下载地址无效')
    with urllib.request.build_opener(NoRedirect()).open(url,timeout=60) as response: data=response.read(30*1024*1024+1)
    if len(data)>30*1024*1024 or not data.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError('图片文件无效')
    temp=output.with_suffix('.download');temp.write_bytes(data);temp.replace(output)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prompt-file',type=Path,required=True);parser.add_argument('--image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--size',choices=['1024x1024','768x1024','1024x768'],default='1024x1024')
    args=parser.parse_args();token=authorized_token();prompt=args.prompt_file.read_text(encoding='utf-8').strip()
    if not prompt or len(prompt)>16000: raise ValueError('创作描述为空或过长')
    image=reference_png(args.image);output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
    state_path=output.with_name('.'+output.name+'.frame-forge.json')
    digest=hashlib.sha256(prompt.encode()+args.size.encode()+(image or b'')).hexdigest()
    if state_path.exists():
        state=json.loads(state_path.read_text(encoding='utf-8'))
        if state['digest']!=digest: raise ValueError('输出位置属于另一项创作，请使用新文件名')
    else:
        if output.exists(): raise ValueError('输出文件已存在，请使用新文件名')
        state={'requestId':secrets.token_hex(16),'digest':digest}
        # Exclusive creation prevents parallel clients allocating different IDs.
        fd=os.open(state_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as file: json.dump(state,file)
    if not state.get('jobId'):
        body,kind=multipart({'clientRequestId':state['requestId'],'prompt':prompt,'size':args.size},image)
        result=request(token,'/api/frame-forge/jobs',body,kind)
        state['jobId']=result['jobId'];write_state(state_path,state)
    deadline=time.monotonic()+960
    while time.monotonic()<deadline:
        result=request(token,'/api/frame-forge/jobs/'+state['jobId'])
        if result['status']=='completed':
            if not result.get('images'): raise RuntimeError('图片尚未就绪，请查询原任务')
            download(result['images'][0]['url'],output)
            print(json.dumps({'ok':True,'output':str(output)},ensure_ascii=False));return
        if result['status']=='failed' or result.get('message'): raise RuntimeError(result.get('message') or '图片未完成')
        print('正在创作图片…',flush=True);time.sleep(10)
    raise RuntimeError('图片仍在处理，请稍后使用同一命令查询，不要重新提交')

if __name__=='__main__':
    try: main()
    except (AuthError,RuntimeError,ValueError,OSError,urllib.error.URLError) as error:
        message=str(error) if isinstance(error,(AuthError,RuntimeError,ValueError)) else '连接或文件操作失败；请保留原任务并重试查询'
        print(json.dumps({'ok':False,'message':message},ensure_ascii=False));raise SystemExit(1)
