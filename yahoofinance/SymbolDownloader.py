import urllib.request
import string

from bs4 import BeautifulSoup

class SymbolDownloader:
	"""Abstract class"""
	
	def __init__(self, type):
		self.symbols = {}
		self.type = type
		self.nextq = string.ascii_lowercase[0]
		self.items = 0
		self.totalItems = 0
	
	def fetchHtml(self):
		request = urllib.request.urlopen("http://finance.yahoo.com/lookup/"+self.type+
											"?s="+self.nextq+"&t=S&m=ALL&r=&b="+str(self.items))
		return request.read().decode('utf-8')
		
	def makeSoup(self, html):
		return BeautifulSoup(html) # Screw Imacros! Long live BeautifulSoup~
	
	def getSymbolsContainer(self, soup):
		symbolsContainer = soup.find("table", { "class" : "yui-dt" }).tbody
		return symbolsContainer
	
	def decodeSymbolsContainer(self, symbolsContainer):
		raise Exception("Function to extract symbols must be overwritten in subclass. Generic symbol downloader does not know how.")
	
	def getQuery(self):
		return self.nextq
	
	def getQueryNr(self):
		return string.ascii_lowercase.index(self.nextq)
	
	def getTotalQueries(self):
		return len(string.ascii_lowercase)
	
	def getTotalItemsFromSoup(self, soup):
		try:
			div = soup.find(id="pagination")
			yikkes = str(div).split("of")[1].split("|")[0]
			yikkes = "".join([char for char in yikkes if char in string.digits])
			return int( yikkes )
		except Exception as ex:
			pass
		return -1;
	
	def getItems(self):
		return self.items
	
	def getTotalItems(self):
		return self.totalItems
	
	def fetchNextSymbols(self):
		html = self.fetchHtml()
		soup = self.makeSoup(html)
		try:
			symbolsContainer = self.getSymbolsContainer(soup)
		except:
			if self.getQueryNr()+1 >= len(string.ascii_lowercase):
				self.items = 0
				self.nextq = string.ascii_lowercase[0]
				return []
			else:
				self.nextq = string.ascii_lowercase[self.getQueryNr()+1]
				self.items = 0
				self.totalItems = -1
				return self.fetchNextSymbols()
		symbols = self.decodeSymbolsContainer(symbolsContainer)
		for symbol in symbols:
			self.symbols[symbol.ticker] = symbol
		self.items = self.items + len(symbols)
		self.totalItems = self.getTotalItemsFromSoup(soup)
		return symbols
	
	def isDone(self):
		return self.nextq == string.ascii_lowercase[0] and self.items == 0 and len(self.symbols) > 0
	
	def getCollectedSymbols(self):
		return self.symbols.values()
	
	def getCollectedSymbolsSize(self):
		return len(self.symbols)
	
	def getRowHeader(self):
		return ["Ticker", "Name", "Exchange"]

