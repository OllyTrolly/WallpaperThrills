#Boilerplate for pynsist
#!python3.4
import sys
sys.path.insert(1, 'pkgs')

from bs4 import BeautifulSoup
from win32com.shell import shell, shellcon
import re
import os
import errno
import urllib.request
import configparser

#Read in variables from config.ini
config = configparser.RawConfigParser()
configPath = os.path.dirname(os.path.realpath(__file__)) + "\config.ini"
config.read(configPath)

myWidth = config.getint('Resolution', 'width')
myHeight = config.getint('Resolution', 'height')
fuzziness = config.getint('Resolution', 'fuzziness')

images = config.getint('Download', 'images')
if images > 20:
	images = 20
shuffle = config.getboolean('Download', 'shuffle')

measure = config.get('Update', 'measure')
number = config.getint('Update', 'number')

#Calculate desired bounds of aspect ratio
myAspect = myWidth / myHeight
loAspect = myAspect * (fuzziness / 100)
hiAspect = myAspect * (2 - (fuzziness / 100))

urls = []
wallpaperDir = shell.SHGetFolderPath(0, shellcon.CSIDL_MYPICTURES, None, 0) + "/WallpaperThrills"
	
def getUrls():
	#Create URL soup for parsing with Beautiful Soup
	url = "http://deadendthrills.com"
	if(shuffle) :
		url = url + "/random/"

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

def createDirectory():
	#Try to create Images directory
	try:
		os.makedirs(wallpaperDir)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

def download():
	#Download number of requested images from list of URLs
	for x in range(1, images + 1) :
		print("Downloading image " + str(x) + " of " + str(images))
		urllib.request.urlretrieve(urls[x - 1], wallpaperDir + "/IMG" + str(x) + ".png")

while len(urls)<images:
	getUrls()
createDirectory()
download()
sys.exit()
