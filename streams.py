# Streams bot for twitch.tv and own3d.tv streams.
# Python 2.7.3
# TODO: make executable later, as of now run via interpreter directly

from bs4 import BeautifulSoup
import re, urllib

from urlparse import urlparse

class Streams:
	_name = "Streams"
	_version = "0.1"
	_author = "potatoe"

	def say_Samo(self):
		print "Samo is a fag"
		return 0

temp = Streams()
temp.say_Samo()
