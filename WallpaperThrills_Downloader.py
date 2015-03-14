import re
import os
import errno
import urllib.request
import configparser
from bs4 import BeautifulSoup

#Read in variables from config.ini
config = configparser.RawConfigParser()
config.read('config.ini')

myWidth = config.getint('Resolution', 'width')
myHeight = config.getint('Resolution', 'height')
fuzziness = config.getint('Resolution', 'fuzziness')

images = config.getint('Download', 'images')
shuffle = config.getboolean('Download', 'shuffle')

measure = config.get('Update', 'measure')
number = config.getint('Update', 'number')

url = "http://deadendthrills.com"
if(shuffle) :
	url = url + "/random/"

urls = []

#Calculate desired bounds of aspect ratio
myAspect = myWidth / myHeight
loAspect = myAspect * (fuzziness / 100)
hiAspect = myAspect * (2 - (fuzziness / 100))

#Create URL soup for parsing with Beautiful Soup
htmlText = urllib.request.urlopen(url).read()
soup = BeautifulSoup(htmlText)

#Find all 'a' tags with a href to a PNG
for a in soup.find_all('a') :
	if a.has_attr('href') :
		match = re.search("\.png", a.get('href'))
		if (match) :
			#Check aspect ratio is within desired bounds
			width = int(a.img.get('width'))
			height = int(a.img.get('height'))
			detAspect = width / height
			if (detAspect >= loAspect) and (detAspect <= hiAspect) :
				urls.append(a.get('href'))

#Try to create Images directory
try:
	os.makedirs("Images")
except OSError as exception:
	if exception.errno != errno.EEXIST:
		raise

#Download number of requested images from list of URLs
for x in range(1, images + 1) :
	urllib.request.urlretrieve(urls[x - 1], "Images/IMG" + str(x) + ".png")
