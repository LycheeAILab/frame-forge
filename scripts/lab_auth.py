"""Frame Forge browser authorization. Never reads provider credentials."""
import argparse
import json
import os
from pathlib import Path
import secrets
import time
import urllib.error
import urllib.request
from urllib.parse import urlencode, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser

BASE = 'https://lab.lycheeai.com.cn'

class AuthError(RuntimeError):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def token_path():
    root = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local')) if os.name == 'nt' else Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    return root / 'LycheeAILab' / 'frame-forge-token.json'

def load_token():
    try:
        token = json.loads(token_path().read_text(encoding='utf-8'))['accessToken']
        return token if isinstance(token, str) and token.startswith('lych_live_') else None
    except (OSError, ValueError, KeyError, TypeError):
        return None

def save_token(token):
    path = token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + secrets.token_hex(8))
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as file:
        json.dump({'accessToken': token}, file)
    os.replace(temp, path)

def validate_token(token):
    request = urllib.request.Request(BASE + '/api/skill-auth/me', headers={'Authorization': 'Bearer ' + token, 'User-Agent': 'FrameForge-Skill'})
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
            return response.status == 200
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            return False
        raise AuthError('Lab 暂时不可用，请稍后重试') from None
    except (urllib.error.URLError, TimeoutError):
        raise AuthError('无法连接 Lab；未清除现有登录状态') from None

def browser_login(timeout=180):
    state, result = secrets.token_urlsafe(32), {}
    class Callback(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != '/callback':
                self.send_error(404); return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 4096:
                    self.send_error(400); return
                fields = parse_qs(self.rfile.read(length).decode('utf-8'), strict_parsing=True)
                received, token = fields.get('state', [''])[0], fields.get('api_key', [''])[0]
                if not secrets.compare_digest(received, state) or not token.startswith('lych_live_'):
                    self.send_error(403); return
            except (ValueError, UnicodeError):
                self.send_error(400); return
            result['token'] = token
            body = '<meta charset="utf-8"><h2>Frame Forge 已授权</h2><p>请返回智能体继续创作。</p>'.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body)
        def log_message(self, *_):
            pass
        def setup(self):
            super().setup()
            self.connection.settimeout(5)
    with HTTPServer(('127.0.0.1', 0), Callback) as server:
        url = BASE + '/skill-auth?' + urlencode({'callback': f'http://127.0.0.1:{server.server_port}/callback', 'state': state, 'skill': 'Frame Forge'})
        print('请在 LycheeAILab 登录并授权：\n' + url, flush=True)
        webbrowser.open(url)
        deadline = time.monotonic() + timeout
        while not result and time.monotonic() < deadline:
            server.timeout = min(1, deadline - time.monotonic())
            server.handle_request()
    token = result.get('token')
    if not token or not validate_token(token):
        raise AuthError('未完成 Lab 授权，请重新登录')
    save_token(token)
    return token

def authorized_token(login=False):
    token = load_token()
    if token and validate_token(token):
        return token
    if login:
        return browser_login()
    raise AuthError('请先运行 lab_auth.py login 完成 Lab 登录')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['login', 'status', 'logout'])
    args = parser.parse_args()
    if args.command == 'logout':
        token_path().unlink(missing_ok=True)
        print(json.dumps({'authenticated': False, 'localCredentialRemoved': True})); return
    if args.command == 'status':
        token = load_token()
        print(json.dumps({'authenticated': bool(token and validate_token(token))})); return
    authorized_token(login=True)
    print(json.dumps({'authenticated': True}))

if __name__ == '__main__':
    try:
        main()
    except AuthError as error:
        print(json.dumps({'ok': False, 'message': str(error)}, ensure_ascii=False))
        raise SystemExit(1)
