#python 2.7.3
from bs4 import BeautifulSoup
import re, urllib
from urlparse import urlparse

class Streams:
	_name = "Streams"
	_author = "potatoe"
	_version = 0.1


	def checkurl(self, url):
		urlchk = urlparse(url)
		if re.match('.*twitch.tv$', urlchk.hostname, re.IGNORECASE):
			return (1, urlchk.path.strip('/'), url)
		elif re.match('.*own3d.tv$', urlchk.hostname, re.IGNORECASE):
			return (2, urlchk.path.strip('/'), url)
		return 0
	
	def t_getdetails(self, user):
		t_source = 'http://api.justin.tv/api/channel/show/' + user + '.xml'
		parser = BeautifulSoup(urllib.urlopen(t_source), features = 'xml')
		if parser.hash is None:
			return parser.channel.id.text, parser.channel.title.text
		return 0


temp = Streams();
print temp.t_getdetails(temp.checkurl('http://nl.twitch.tv/sing_sinsg')[1])
#print temp.checkurl('http://nl.twitch.tv/sing_sing')
