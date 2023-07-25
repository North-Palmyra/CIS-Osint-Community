#!/usr/bin/env python3
from pprint import pprint
import json
import re
from urllib.request import urlopen
import sys
import re
import shutil
from html import unescape

RE_TME_IMG_URL = re.compile(
    r'<img class="tgme_page_photo_image" src="(.+)"'
)
RE_TME_TITLE = re.compile(
    r'tgme_page_title[^>]+>\s*<span[^>]+>([^<]+)'
)
USER_PLACEHOLDER_IMAGE = 'static/logo/user.jpg'
NODES_JSON_FILE = 'data/nodes.json'

def load_json():
    with open(NODES_JSON_FILE, encoding='utf-8') as inp:
        data = json.load(inp)
    print('Загружено узлов: %d' % len(data))
    return data

def save_json(data):
    with open(NODES_JSON_FILE, 'w', encoding='utf-8') as out:
        out.write(json.dumps(data, indent=4, ensure_ascii=False).replace('\r\n', '\n'))
    print('Сохранено узлов: %d' % len(data))


def build_tme_url(username):
    return 'https://t.me/%s' % username


def get_tme_page(username):
    url = build_tme_url(username)
    html = urlopen(url).read().decode('utf-8')
    return html


def get_logo(username, html=None):
    if username.startswith('???'):
        return 'static/logo/user.jpg'
    if html is None:
        html = get_tme_page(username)
    match = RE_TME_IMG_URL.search(html)
    logo_path = 'static/logo/%s.jpg' % username
    if not match:
        print('Для %s не найдена картинка, используем заглушку' % username)
        shutil.copyfile(USER_PLACEHOLDER_IMAGE, logo_path)
    else:
        img_url = match.group(1)
        print('Загрузка %s' % img_url)
        img_data = urlopen(img_url).read()
        with open(logo_path, 'wb') as out:
            out.write(img_data)
        print('Сохранено %d байт в %s' % (len(img_data), logo_path))
    return logo_path


def get_data(username, links):
    if username.startswith('???'):
        name = '???'
        logo_path = get_logo(username)
        url = None
    else:
        html = get_tme_page(username)
        name = unescape(RE_TME_TITLE.search(html).group(1))
        logo_path = get_logo(username, html=html)
        url = build_tme_url(username)
    item = {
        'id': username,
        'name': name,
        'links': links,
        'imageUrl': logo_path,
        'url': url,
    }
    return item


def action_add(username, parent):
    data = load_json();
    data.append(get_data(username, [parent]))
    save_json(data)


def action_update(full=False):
    data = load_json()
    for i, info in enumerate(data):
        if 'noUpdate' in info and info['noUpdate']:
            print('Обновлять запрещено: %s', info['id'])
        elif full:
            data[i] = get_data(info['id'], info['links'])
        else:
            data[i]['imageUrl'] = get_logo(info['id'])
    save_json(data)


def main(**kwargs):
    action = sys.argv[1]
    if action == 'update':
        action_update()
    elif action == 'updateLogo': 
        action_update(False)  
    elif action == 'add':
        username = sys.argv[2]
        parent = sys.argv[3]
        if username == '???':
            username = '???%s' % parent
        action_add(username, parent)
    else:
        sys.stderr.write('Unknown action: %s' % action)
        sys.exit(1)


if __name__ == '__main__':
   main() 
