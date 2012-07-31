# Streams bot for twitch.tv and own3d.tv streams.
# Python 2.7.3
# TODO: make executable later, as of now run via interpreter directly

from bs4 import BeautifulSoup
import re, urllib

from urlparse import urlparse

#dev-python/twisted 
#dev-python/twisted-words

from twisted.words.protocols import irc
from twisted.internet import protocol

import sqlite3 as sqlite

class Streams:
	_name = "Streams"
	_version = "0.1"
	_author = "potatoe"

	con = None
	cur = None

	def __init__(self):
		self.con = sqlite.connect('streams.db')
		self.cur = self.con.cursor()

	def say_Samo(self):
		print "Samo is a fag"
		return 0

	def sanitize(self, text):
		#Pythons inbuilt commands for sql connectors sanitize input accordingly afaik
		#However the function template can be used for a lof of things so i'm going to leave it here.
		return text

	def import_list(self, fname):
		#import bobs list of previously added streams so that we don't have to do it again
		file = open(fname, 'r')
		#fname must have full path
		for line in file:
			streamer = line.replace(' ', '').split('-')[0]
			if(re.match('.*=J$', streamer)):
				print "http://twitch.tv/" + streamer.split('=')[0]
				#self.parser_twitch(streamer.split('=')[0])
			elif(re.match('.*=O$', streamer)):
				print "Own3d.tv: " + streamer.split('=')[0]
		return 0

	def parser_twitch(self, user):
		APIDET = "http://api.justin.tv/api/channel/show/" + user + ".xml"
		APISTA = "http://api.justin.tv/api/stream/list.xml?channel=" + user #while live
		bs4parser = BeautifulSoup(urllib.urlopen(APIDET), features = 'xml')
		
		if(bs4parser.hash is None):
			print bs4parser.channel.id.text, bs4parser.channel.title.text
		elif(bs4parser.hash):
			print bs4parser.hash.error.text




temp = Streams()
#temp.import_list('streams.list')
temp.parser_twitch('ggnetsheevr')
