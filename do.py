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
NODES_COMPILED_FILE = 'static/data/nodes.js'


def build_tme_url(username):
    return 'https://t.me/%s' % username


def get_tme_page(username):
    url = build_tme_url(username)
    html = urlopen(url).read().decode('utf-8')
    return html


def action_getlogo(username, html=None):
    if html is None:
        html = get_tme_page(username)
    match = RE_TME_IMG_URL.search(html)
    logo_path = 'static/logo/%s.jpg' % username
    if not match:
        print('No image found, using placeholder')
        shutil.copyfile(USER_PLACEHOLDER_IMAGE, logo_path)
    else:
        img_url = match.group(1)
        print('Downloading %s' % img_url)
        img_data = urlopen(img_url).read()
        with open(logo_path, 'wb') as out:
            out.write(img_data)
        print('Saved %d bytes to %s' % (len(img_data), logo_path))
    return logo_path


def action_add(username, parent):
    if username == '???':
        username = f'{parent}_user'
        name = '???'
        logo_path = 'static/logo/user.jpg'
        url = None
    else:
        html = get_tme_page(username)
        name = unescape(RE_TME_TITLE.search(html).group(1))
        logo_path = action_getlogo(username, html=html)
        url = build_tme_url(username)
    item = {
        'id': username,
        'name': name,
        'links': [parent],
        'imageUrl': logo_path,
        'url': url,
    }
    with open(NODES_JSON_FILE, encoding='utf-8') as inp:
        data = json.load(inp)
    print('Loaded %d items from JSON file' % len(data))
    data.append(item)
    print('Saved %d items to JSON file' % len(data))
    with open(NODES_JSON_FILE, 'w', encoding='utf-8') as out:
        out.write(json.dumps(data, indent=4, ensure_ascii=False))
    action_compile()


def action_compile():
    with open(NODES_JSON_FILE, encoding='utf-8') as inp:
        data = json.load(inp)
    with open(NODES_COMPILED_FILE, 'w', encoding='utf-8') as out:
        json_data = json.dumps(data, indent=4, ensure_ascii=False)
        out.write('dataNodes = %s;' % json_data)
    print('Saved %d items to JS compiled file %s' % (
        len(data), NODES_COMPILED_FILE
    ))


def main(**kwargs):
    action = sys.argv[1]
    if action == 'getlogo':
        username = sys.argv[2]
        gid = sys.argv[3]
        action_getlogo(username, gid)
    elif action == 'add':
        username = sys.argv[2]
        parent = sys.argv[3]
        action_add(username, parent)
    elif action == 'compile':
        action_compile()
    else:
        sys.stderr.write('Unknown action: %s' % action)
        sys.exit(1)


if __name__ == '__main__':
   main() 
