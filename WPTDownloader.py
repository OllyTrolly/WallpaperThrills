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

    urls = []

    while len(urls) < config.images:
        urls.extend(get_urls(low_aspect, high_aspect))
    create_directory()
    download(urls)
    sys.exit()


def get_urls(low_aspect, high_aspect):

    urls = []

    # Create URL soup for parsing with Beautiful Soup
    url = "http://deadendthrills.com"
    if config.shuffle:
        url = url + "/random/"

    ua_spoof_request = urllib.request.Request(url, headers={'User-Agent': r'Mozilla/5.0 \
    (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'})

    try:
        html_text = urllib.request.urlopen(ua_spoof_request).read()
    except urllib.error.HTTPError as exception:
        sys.exit("ERROR - Could not get Dead End Thrills page for the following reason: " + format(exception))

    soup = BeautifulSoup(html_text, 'html.parser')

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
