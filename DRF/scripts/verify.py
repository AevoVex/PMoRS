"""Run from any directory with the project's Python interpreter."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
jobs = [
    ('yatube', ['check']),
    ('yatube', ['makemigrations', '--check', '--dry-run']),
    ('yatube', ['test', 'api', 'lessons', '--verbosity', '2']),
    ('kittygram', ['check']),
    ('kittygram', ['makemigrations', '--check', '--dry-run']),
    ('kittygram', ['test', 'cats', '--verbosity', '2']),
    ('kittygram', ['check', '--settings=config.lesson_settings']),
    ('kittygram', ['makemigrations', '--check', '--dry-run', '--settings=config.lesson_settings']),
    ('kittygram', ['test', 'lessons', '--settings=config.lesson_settings', '--verbosity', '2']),
]

if __name__ == '__main__':
    for project, args in jobs:
        print(f'\n>>> {project}: manage.py {" ".join(args)}', flush=True)
        subprocess.run([sys.executable, 'manage.py', *args], cwd=ROOT / project, check=True)
    print('\n>>> Yatube: original upstream pytest suite', flush=True)
    subprocess.run([sys.executable, '-m', 'pytest'], cwd=ROOT / 'yatube', check=True)
    subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
    print('\nAll checks passed.', flush=True)
