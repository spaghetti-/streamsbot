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
from twisted.internet import protocol, reactor

import sqlite3 as sqlite

class Streams:

	def __init__(self):
		self.con = sqlite.connect('streams.db')
		self.cur = self.con.cursor()
		self.admin = 'potatoe!alice@kill.yourself.now.doitfaggot.org'

	def say_Samo(self):
		print "Samo is a fag"
		return 0

	def sanitize(self, string):
		#Some faggots have retarded as fuck titles that need to be cleaned.
		#sqlite is too fucking retarded to do it on its own as well
		string = string.replace('"', '')
		#not for sure if this works but w/e
		if(type(string) == 'unicode'):
			return unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore')
		return string

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
				#self.parser_own3d(streamer.split('=')[0])
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
			#cmd = 'INSERT INTO streams(id, login, title, url) VALUES(' + id + ',"' + login + '","' + self.sanitize(title) + '","' + url + '")'
			self.add_twitch_stream(id, login, title, url)	
		elif(bs4parser.hash):
			print bs4parser.hash.error.text
			return 1


		return 0

	def parser_own3d(self, url, name):
		#nothing much to parse since I havent figured out their retarded API
		#cbb
		id = url.split("/")[len(url.split("/")) - 1]
		#url = 'http://own3d.tv/live/' + id
		self.add_own3d_stream(id, name, url)

	def truncateTable(self):
		drop = 'DROP TABLE streams'
		create = 'CREATE TABLE streams (id INTEGER PRIMARY KEY, server TEXT, login TEXT, title TEXT, url TEXT, live INT, viewers INT)'

		self.cur.execute(drop)
		self.con.commit()
		self.cur.execute(create)
		self.con.commit()

		return 0

	def add_twitch_stream(self, id, login, title, url):
		cmd = 'INSERT INTO streams(id, server, login, title, url) VALUES(' + id + ', "twitch", "' + login + '","' + self.sanitize(title) + '","' + url + '")'
		self.cur.execute(cmd)
		self.con.commit()

	def add_own3d_stream(self, id, name, url):
		cmd = 'INSERT INTO streams(id, server, login, title, url) VALUES(' + id + ', "own3d", "' + id + '","' + self.sanitize(name) + '","' + url + '")'
		self.cur.execute(cmd)
		self.con.commit()

	def exists(self, id):
		#TODO: check if id exists in db, if it does return 0
		#		if it doesn't return 1
		#		flipped return codes but w/e

		cmd = 'SELECT * FROM streams WHERE id=' + str(id)
		self.cur.execute(cmd)

		row = self.cur.fetchone()
		if(row is None):
			return 1
		return 0

	def update_twitch_stream(self, id, login):
		APISTA = "http://api.justin.tv/api/stream/list.xml?channel=" + login
		parser = BeautifulSoup(urllib.urlopen(APISTA), features = 'xml')

		if(parser.streams.stream is None):
			cmd = 'UPDATE streams SET live=0, viewers=0 WHERE id =' + id
			self.cur.execute(cmd)
			self.con.commit()
			return (0, 0)
		elif(parser.streams.stream.channel_count):
			cmd = 'UPDATE streams SET live=1, viewers=' + parser.streams.stream.channel_count.text + ' WHERE id=' + id
			self.cur.execute(cmd)
			self.con.commit()
			return (1, parser.streams.stream.channel_count.text)

	def update_own3d_stream(self, id):
		APISTA = 'http://api.own3d.tv/liveCheck.php?live_id=' + str(id)
		parser = BeautifulSoup(urllib.urlopen(APISTA), features = 'xml')
		if(parser.own3dReply.liveEvent.isLive.text == 'false'):
			cmd = 'UPDATE streams SET live=0, viewers=0 WHERE id =' + id
			self.cur.execute(cmd)
			self.con.commit()
			return (0, 0)
		elif(parser.own3dReply.liveEvent.isLive.text == 'true'):
			cmd = 'UPDATE streams SET live=1, viewers=' + parser.own3dReply.liveEvent.liveViewers.text + ' WHERE id=' + id
			self.cur.execute(cmd)
			self.con.commit()
			return (1, parser.own3dReply.liveEvent.liveViewers.text)

	def update_streams(self):
		cmd = 'SELECT * from streams'
		self.cur.execute(cmd)
		row = self.cur.fetchall()

		for streamer in row:
			if(streamer[1] == 'twitch'):
				print self.update_twitch_stream(str(streamer[0]), streamer[2])
			elif(streamer[1] == 'own3d'):
				print self.update_own3d_stream(str(streamer[0]))

	def get_live_streams(self):
		cmd = 'SELECT * from streams WHERE live=1 ORDER BY viewers DESC'
		self.cur.execute(cmd)
		row = self.cur.fetchall()
		#returns a list
		return row

	def get_count(self):
		cmd = 'SELECT * FROM streams'
		self.cur.execute(cmd)
		row = self.cur.fetchall()
		return len(row)

	def parse_for_channel(self, row):
		out = ''
		for i in row:
			if(i):
				if(i[1] == 'own3d'):
					out += i[4].replace('http://', 'www.') + '/' + i[3] + ' (' + str(i[6]) + ') '
				else:
					out += i[4].replace('http://', 'www.') + ' (' + str(i[6]) + ') '
				# www. to make it clickable in many clients
		return out

	def add(self, link):
		link = link.replace('.addstream ', '')
		print link
		url = urlparse(link.split(' ')[0])
		print url.hostname, url.path.strip('/')
		if(url.hostname == 'twitch.tv'):
			print 'adding: ', url.path.strip('/')
			self.parser_twitch(url.path.strip('/'))
			return 'Added, will update soon'
		elif(url.hostname == 'own3d.tv'):
			if(len(link.split(' ')) < 2):
				return 'Format: http://own3d.tv/live/11111'

			id = url.path.strip('/').split('/')[1]
			name = link.split(' ')[1]
			self.parser_own3d(link.split(' ')[0], name)
			print 'adding: ', id, name, link.split(' ')[0]
			return 'Added, will update soon'
		else:
			return 'Format of stream url: http://twitch.tv/username OR http://own3d.tv/live/streamid'

#TODO: Find out how to initialize the fucking class inside this.
#nvm global var data

class StreamsBot(irc.IRCClient):

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
    	self.msg('Q@CServe.quakenet.org', 'auth user pass')
    	self.mode(self, True, '+x', user=self.nickname)
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname)

    def joined(self, channel):
        print "Joined %s." % (channel)

    def privmsg(self, user, channel, msg):
    	usernick = user.split('!', 1)[0]
    	if re.match('^.streams$', msg):
    		#data = Streams()
    		self.msg(channel, str(data.parse_for_channel(data.get_live_streams())))
        elif msg == '.update':
			if re.match(data.admin, user):
				#data = Streams()
				data.update_streams()
				self.msg(channel, 'Database updated')
			else:
				self.msg(channel, 'Not sufficient privileges for user %s' % usernick)

        elif(re.match('^.addstream', msg)):
			if re.match(data.admin, user):
				self.msg(channel, data.add(msg))
			else:
				self.msg(channel, 'MSG %s to add links' % data.admin)


class StreamsBotFactory(protocol.ClientFactory):
    protocol = StreamsBot

    def __init__(self, channel, nickname='RSB'):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason)


#temp = Streams()
#temp.update_streams()
#print temp.get_count()
#temp.truncateTable()
#temp.import_list('streams.list')

if __name__ == '__main__':
	#f = StreamsBotFactory('#test')
	#reactor.connectTCP('irc.quakenet.org', 6667, f)
	global data
	data = Streams()
	reactor.connectTCP('irc.quakenet.org', 6667, StreamsBotFactory('#samo.dota'))
	reactor.run()
#	data.add('http://own3d.tv/live/72641 phantomfag')
#	print data.add('http://twitch.tv/snigsing')
#	print data.add('http://own3d.tv/live/72641')
    #temp = Streams()
    #print temp.parse_for_channel(temp.get_live_streams())
    #print temp.parse_for_channel(temp.get_live_streams())
