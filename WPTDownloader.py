#!python3.6

# IMPORTS #

# Own packages
import config

# Stdlib packages
import re
import os
import errno
import sys
import urllib.request
import urllib.error

# Library packages
from bs4 import BeautifulSoup

sys.path.insert(1, 'pkgs')


def main():

    # Limit of 20 to prevent hammering of server
    if config.images > 20:
        config.images = 20

    # Calculate desired bounds of aspect ratio
    abs_aspect = config.width / config.height
    low_aspect = abs_aspect * (config.fuzziness / 100)
    high_aspect = abs_aspect * (2 - (config.fuzziness / 100))

    if config.shuffle and config.search:
        print("ERROR - Only one of config values 'shuffle' and 'search' can be True, exiting...")
        sys.exit(1)

    if config.shuffle:
        url = 'http://deadendthrills.com/random'
    elif config.search:
        try:
            url = search_game_index(config.game_name)
        except Exception:
            print('ERROR - Could not find specified game (' + config.game_name + ') in index, exiting...')
            sys.exit(1)
    else:
        url = 'http://deadendthrills.com'

    urls = []

    while len(urls) < config.images:
        urls.extend(get_image_urls(url, low_aspect, high_aspect))
    create_directory()
    download(urls)
    sys.exit()


def get_image_urls(url, low_aspect, high_aspect):

    urls = []

    soup = extract_soup(url)

    # Find all 'a' tags with a href to a PNG
    for a in soup.find_all('a'):
        if a.has_attr('href'):
            match = re.search("\.png", a.get('href'))
            if match:
                # Check aspect ratio is within desired bounds
                width = int(a.img.get('width'))
                height = int(a.img.get('height'))
                img_aspect = width / height
                if (img_aspect >= low_aspect) and (img_aspect <= high_aspect):
                    urls.append(a.get('href'))

    return urls


def extract_soup(url):

    print('Extracting soup for URL: ' + url)

    ua_spoof_request = urllib.request.Request(url, headers={'User-Agent': r'Mozilla/5.0 \
    (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/61.0.3163.100 Safari/537.36'})

    try:
        html_text = urllib.request.urlopen(ua_spoof_request).read()
    except urllib.error.HTTPError as exception:
        sys.exit("ERROR - Could not get Dead End Thrills page for the following \
        reason: " + format(exception))

    return BeautifulSoup(html_text, 'html.parser')


def search_game_index(game_name):
    base_url = "http://deadendthrills.com/game-index/?currentpage="
    pages_left = True
    page_number = 1
    game_url = None

    soup = extract_soup(base_url + str(page_number))

    while pages_left:
        try:
            game_url = search_game_index_page(game_name, soup)
        except Exception:
            print('Game not found on index page ' + str(page_number) + ', checking next page')

        if game_url:
            return game_url

        page_number += 1

        prev_soup = soup
        soup = extract_soup(base_url + str(page_number))

        if prev_soup.body.section == soup.body.section:
            pages_left = False

    raise Exception('Game not found')


def search_game_index_page(game_name, soup):

    for div in soup.find_all("div", "gameindexblock"):
        for child in div.h2:
            if str(child).lower() == game_name.lower():
                return div.parent.parent.parent.parent.get('href')

    raise Exception('Game not found')


def create_directory():

    # Try to create Images directory
    try:
        os.makedirs(config.download_location)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def download(urls):

    # Download number of requested images from list of URLs
    for x in range(1, config.images + 1):
        print("Downloading image " + str(x) + " of " + str(config.images))
        urllib.request.urlretrieve(urls[x - 1], config.download_location + "/IMG" + str(x) + ".png")


if __name__ == '__main__':
    sys.exit(main())
