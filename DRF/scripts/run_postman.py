"""Run the course collection against an isolated temporary Yatube database."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError

from smoke_http import ROOT, SERVER_CODE, request

SEED = '''
from django.contrib.auth import get_user_model
from posts.models import Group
User = get_user_model()
User.objects.create_superuser('root', 'root@admin.ru', '5eCretPaSsw0rD')
User.objects.create_user('regular_user', 'user@not-admin.ru', 'iWannaBeAdmin')
Group.objects.create(title='TestGroup', slug='test-group', description='Some text.')
'''


def main():
    executable = shutil.which('postman.cmd' if os.name == 'nt' else 'postman')
    if not executable:
        raise SystemExit('Postman CLI is required for this optional check.')
    project = ROOT / 'yatube'
    source = project / 'postman_collection/CRUD_for_yatube.postman_collection.json'
    with tempfile.TemporaryDirectory(prefix='yatube-postman-') as directory:
        folder = Path(directory)
        env = dict(os.environ, DJANGO_DB_PATH=str(folder / 'test.sqlite3'),
                   DJANGO_SETTINGS_MODULE='yatube_api.settings', PYTHONIOENCODING='utf-8')
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], cwd=project, env=env,
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run([sys.executable, 'manage.py', 'shell', '-c', SEED], cwd=project, env=env,
                       check=True, stdout=subprocess.DEVNULL)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        # Only replace the fixed local port; all upstream assertions stay intact.
        collection = json.loads(source.read_text(encoding='utf-8'))

        def update_urls(items):
            for item in items:
                if 'item' in item:
                    update_urls(item['item'])
                elif 'request' in item:
                    url = item['request']['url']
                    if url['raw'].startswith('http://127.0.0.1:8000/'):
                        url['raw'] = url['raw'].replace(':8000/', f':{port}/', 1)
                        url['port'] = str(port)
                    else:
                        raise ValueError('The collection contains an unexpected target URL')

        update_urls(collection['item'])
        local_collection = folder / 'collection.json'
        local_collection.write_text(json.dumps(collection, ensure_ascii=False), encoding='utf-8')
        with (folder / 'server.log').open('w+', encoding='utf-8') as log:
            process = subprocess.Popen(
                [sys.executable, '-c', SERVER_CODE, str(port)], cwd=project, env=env,
                stdin=subprocess.PIPE, stdout=log, stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            )
            try:
                deadline = time.monotonic() + 20
                while True:
                    if process.poll() is not None:
                        raise RuntimeError('Server failed to start')
                    try:
                        request(f'http://127.0.0.1:{port}', '/api/v1/posts/', expected=401)
                        break
                    except (URLError, TimeoutError):
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(0.1)
                result = subprocess.run([
                    executable, 'collection', 'run', str(local_collection),
                    '--no-report-events', '--no-insecure-file-read', '--working-dir', str(folder),
                    '--disable-unicode', '--timeout-request', '5000', '--timeout', '120000',
                ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=150)
                output = result.stdout + '\n' + result.stderr
                (ROOT / 'docs/postman-results.txt').write_text(output, encoding='utf-8')
                print(output)
                return result.returncode
            finally:
                try:
                    process.communicate(input=b'stop\n', timeout=10)
                except subprocess.TimeoutExpired:
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                       stdout=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        process.kill()
                    process.wait()


if __name__ == '__main__':
    sys.exit(main())
