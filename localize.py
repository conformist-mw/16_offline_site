from lxml.html import fromstring, tostring, HtmlComment
import re
import os
import requests
match = re.compile(r'(\[if.*?)(<script.*?script>\s*)(<!\[endif\]$)', re.DOTALL)


def load_root(file):
    with open(file, 'r') as f:
        return fromstring(f.read())


def find_all_css(root):
    links = root.findall(".//link[@rel='stylesheet']")
    for link in links:
        file = requests.get(link.attrib['href'])
        fname = link.attrib['href'].rsplit('/', 1)[-1]
        with open('css/' + fname, 'w') as f:
            f.write(file.text)
        link.attrib['href'] = 'css/' + fname


def find_all_js(root):
    scrpits = root.findall(".//script[@src]")
    for script in scrpits:
        file = requests.get(script.attrib['src'])
        fname = script.attrib['src'].rsplit('/', 1)[-1]
        with open('js/' + fname, 'w') as f:
            f.write(file.text)
        script.attrib['src'] = 'js/' + fname


def handle_condcoms(root):
    comments = []
    for el in root.iter():
        if isinstance(el, HtmlComment):
            if 'script' in el.text:
                comments.append(el)
    for comment in comments:
        res = re.match(match, comment.text)
        com_root = fromstring(res.group(2))
        find_all_js(com_root)
        scr = [tostring(t).decode() for t in com_root.findall('.//script')]
        comment.text = res.group(1) + ''.join(scr) + res.group(3)


if __name__ == '__main__':
    if not os.path.exists('css'):
        os.mkdir('css')
    if not os.path.exists('js'):
        os.mkdir('js')
    html = load_root('index.html')
    find_all_js(html)
    find_all_css(html)
    handle_condcoms(html)
    with open('result.html', 'wb') as f:
        f.write(tostring(html))
