import pathlib
import re
from typing import List

import lxml
import lxml.etree
import requests


def get_wiktionary(word: str, ses: requests.Session = None) -> str:
    word = word.strip().replace(" ", "_")
    url = f"https://en.wiktionary.org/wiki/{word}"
    resp = (ses or requests).get(url)
    resp.raise_for_status()
    return resp.text


def parse_audio_urls(content: str) -> List[str]:
    """Parse the URL of the MP3 / OGG links from <audio><source></source></audio> tags."""
    html = lxml.etree.HTML(content)
    # unique_candidates
    urls = list(set(html.xpath("//audio/source/@src")))
    #only_english
    urls = [
        u for u in urls
        if re.search('(^|(?<![a-z]))(en)g?(?![a-z])', u.rsplit('/', 1)[-1], re.I)
    ]
    # us mp3 first
    urls = sorted(urls, key=lambda u: ('-us' in u.lower(), 'mp3' in u), reverse=True)

    # ensure https
    urls = [
        (f"https:{u}" if u.startswith('//') else u)
        for u in urls
    ]
    return urls

def download_file(url: str, storage_dir='.', ses: requests.Session = None) -> str:
    storage_dir = pathlib.Path(storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    fname = url.rsplit('/')[-1]
    fpath = storage_dir / fname
    if fpath.exists():
        print(f"File {fpath} already exists, skipping download.")
        return fname
    resp = (ses or requests).get(url)
    resp.raise_for_status()

    with open(fpath, "wb") as f:
        f.write(resp.content)
    return fname
