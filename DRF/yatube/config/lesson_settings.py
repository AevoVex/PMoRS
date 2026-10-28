import os
from .settings import *  # noqa: F403

stage = os.environ.get('YATUBE_STAGE', 'functions')
if stage not in {'functions', 'apiview', 'viewset'}:
    raise ValueError('YATUBE_STAGE must be functions, apiview or viewset')
ROOT_URLCONF = f'lessons.urls_{stage}'
