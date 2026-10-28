"""Real HTTP verification on fresh temporary databases; leaves no running servers."""
import datetime as dt
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SERVER_CODE = '''
import sys
import threading
from django.core.wsgi import get_wsgi_application
from wsgiref.simple_server import make_server
server = make_server('127.0.0.1', int(sys.argv[1]), get_wsgi_application())
worker = threading.Thread(target=server.serve_forever, daemon=True)
worker.start()
sys.stdin.readline()
server.shutdown()
worker.join()
server.server_close()
'''


def request(base, path, data=None, token=None, scheme='Token', method=None, expected=200):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'{scheme} {token}'
    body = json.dumps(data).encode() if data is not None else None
    req = Request(base + path, data=body, headers=headers, method=method)
    try:
        response = urlopen(req, timeout=5)
    except HTTPError as error:
        response = error
    with response:
        payload = response.read()
        if response.status != expected:
            raise AssertionError(f'{req.method} {path}: {response.status}, expected {expected}: {payload[:500]!r}')
        return json.loads(payload) if payload else None


def verify(project):
    with tempfile.TemporaryDirectory(prefix=f'drf-{project}-') as directory:
        env = dict(os.environ, DJANGO_DB_PATH=str(Path(directory) / 'test.sqlite3'),
                   DJANGO_SETTINGS_MODULE='config.settings', PYTHONIOENCODING='utf-8')
        for args in [('migrate', '--noinput'), ('seed_demo',), ('seed_demo',)]:
            subprocess.run([sys.executable, 'manage.py', *args], cwd=ROOT / project,
                           env=env, check=True, stdout=subprocess.DEVNULL)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        base = f'http://127.0.0.1:{port}'
        with (Path(directory) / 'server.log').open('w+', encoding='utf-8') as log:
            process = subprocess.Popen(
                [sys.executable, '-c', SERVER_CODE, str(port)],
                cwd=ROOT / project, env=env, stdin=subprocess.PIPE, stdout=log, stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            )
            try:
                endpoint = '/api/v1/posts/' if project == 'yatube' else '/cats/'
                deadline = time.monotonic() + 20
                while True:
                    if process.poll() is not None:
                        raise RuntimeError('Development server exited before readiness')
                    try:
                        request(base, endpoint, expected=401)
                        break
                    except (URLError, TimeoutError):
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(0.1)
                if project == 'yatube':
                    token_url, key, scheme = '/api/v1/api-token-auth/', 'token', 'Token'
                    payload = {'text': 'HTTP smoke'}
                else:
                    token_url, key, scheme = '/auth/jwt/create/', 'access', 'Bearer'
                    payload = {'name': 'HTTP smoke', 'color': 'Gray', 'birth_year': dt.date.today().year}
                login = {'username': 'alice', 'password': 'Demo-Learning-42!'}
                tokens = request(base, token_url, login)
                token = tokens[key]
                other = request(base, token_url, {**login, 'username': 'bob'})[key]
                if project == 'yatube':
                    groups = request(base, '/api/v1/groups/', token=token)
                    payload['group'] = groups[0]['id']
                    request(base, f'/api/v1/groups/{groups[0]["id"]}/', token=token)
                initial = request(base, endpoint, token=token, scheme=scheme)
                assert len(initial) == 2, 'Repeated seed_demo must not duplicate data'
                item = request(base, endpoint, payload, token, scheme, expected=201)
                detail = f'{endpoint}{item["id"]}/'
                request(base, detail, token=token, scheme=scheme)
                request(base, detail, payload, other, scheme, method='PATCH', expected=403)
                request(base, detail, payload, token, scheme, method='PATCH')
                request(base, detail, payload, token, scheme, method='PUT')
                if project == 'yatube':
                    assert item['author'] == 'alice'
                    comments = f'{detail}comments/'
                    comment = request(base, comments, {'text': 'HTTP comment', 'author': 'alice'}, other, expected=201)
                    assert comment['author'] == 'bob'
                    comment_url = f'{comments}{comment["id"]}/'
                    request(base, comment_url, {'text': 'Changed'}, token, method='PATCH', expected=403)
                    request(base, comment_url, {'text': 'Changed'}, other, method='PATCH')
                    wrong_url = f'/api/v1/posts/{initial[0]["id"]}/comments/{comment["id"]}/'
                    request(base, wrong_url, token=other, expected=404)
                    request(base, comment_url, token=other, method='DELETE', expected=204)
                if project == 'kittygram':
                    refreshed = request(base, '/auth/jwt/refresh/', {'refresh': tokens['refresh']})
                    request(base, '/cats/', token=refreshed['access'], scheme=scheme)
                request(base, detail, token=token, scheme=scheme, method='DELETE', expected=204)
                request(base, detail, token=token, scheme=scheme, expected=404)
                print(f'{project}: real HTTP CRUD, authentication, forbidden writes and idempotent seed OK')
            except BaseException:
                log.flush()
                log.seek(0)
                print(log.read(), file=sys.stderr)
                raise
            finally:
                try:
                    process.communicate(input=b'stop\n', timeout=10)
                except subprocess.TimeoutExpired:
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], check=False,
                                       stdout=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        process.kill()
                    process.wait()


if __name__ == '__main__':
    for name in ['yatube', 'kittygram']:
        verify(name)
