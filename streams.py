# Streams bot for twitch.tv and own3d.tv streams.
# Python 2.7.3
# TODO: make executable later, as of now run via interpreter directly

from bs4 import BeautifulSoup
import re, urllib

from urlparse import urlparse
import unicodedata

#dev-python/twisted 
#dev-python/twisted-words

from twisted.words.protocols import irc
from twisted.internet import protocol

import sqlite3 as sqlite

class Streams:
	_name = "Streams"
	_version = "0.1"
	_author = "potatoe"


	def __init__(self):
		self.con = sqlite.connect('streams.db')
		self.cur = self.con.cursor()

	def say_Samo(self):
		print "Samo is a fag"
		return 0

	def sanitize(self, string):
		#Some faggots have retarded as fuck titles that need to be cleaned.
		#sqlite is too fucking retarded to do it on its own as well
		string = string.replace('"', '')
		return unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore')

	def import_list(self, fname):
		#import bobs list of previously added streams so that we don't have to do it again
		file = open(fname, 'r')
		#fname must have full path
		for line in file:
			streamer = line.replace(' ', '').split('-')[0]
			if(re.match('.*=J$', streamer)):
				print "http://twitch.tv/" + streamer.split('=')[0]
				self.parser_twitch(streamer.split('=')[0])
			elif(re.match('.*=O$', streamer)):
				print "Own3d.tv: " + streamer.split('=')[0]
		return 0

	def parser_twitch(self, user):
		APIDET = "http://api.justin.tv/api/channel/show/" + user + ".xml"
		APISTA = "http://api.justin.tv/api/stream/list.xml?channel=" + user #while live
		bs4parser = BeautifulSoup(urllib.urlopen(APIDET), features = 'xml')
		
		if(bs4parser.hash is None):
			id = bs4parser.channel.id.text
			title = bs4parser.channel.title.text
			login = bs4parser.channel.login.text
			url = 'http://twitch.tv/' + login
			print 'Working on ' + login 
			#cmd = "INSERT INTO streams(id, login, title, url) VALUES(" + id + ",'" + login + "','" + title + ","" + url + "")"
			cmd = 'INSERT INTO streams(id, login, title, url) VALUES(' + id + ',"' + login + '","' + self.sanitize(title) + '","' + url + '")'
			print cmd
			self.cur.execute(cmd)
			self.con.commit()
		elif(bs4parser.hash):
			print bs4parser.hash.error.text

		return 0

	def resetTable(self):
		drop = 'DROP TABLE streams'
		create = 'CREATE TABLE streams (id INTEGER PRIMARY KEY, login TEXT, title TEXT, url TEXT, live INT, viewers INT)'

		self.cur.execute(drop)
		self.con.commit()
		self.cur.execute(create)
		self.con.commit()

		return 0




temp = Streams()
temp.import_list('streams.list')
#temp.parser_twitch('nookiedota')
