import importlib
import sys
import engines
from lxml import etree
import re

class EpubIndexer(object):
	epub = False
	engine = False

	def __init__(self, engineName=False):
		if engineName:
			mod = importlib.import_module("epubsearch.engines.%sengine" % engineName)
			# import whooshengine as engine
			self.engine = getattr(mod,'%sEngine' % engineName.capitalize())()
			print self.engine

	def load(self, epub):
		self.epub = epub
		self.engine.create()

		for spineItem in epub.spine:

			filename = epub.base + "/" + spineItem['href']

			self.engine.add(filename=filename, href=spineItem['href'], title=spineItem['title'], cfiBase=spineItem['cfiBase'], spinePos=spineItem['spinePos'])

		self.engine.finished()

	def search(self, q, limit=None):
		rawresults = self.engine.query(q, limit)
		# print len(rawresults)
		r = {}
		r["results"] = []

		for hit in rawresults:
			baseitem = {}
			baseitem['title'] = hit["title"]
			baseitem['href'] = hit["href"]
			baseitem['path'] = hit["path"]

			# find base of cfi
			cfiBase = hit['cfiBase'] + "/!"

			# for testing
			baseitem['highlight'] = hit["highlight"]
			
			with open(hit["path"]) as fileobj:
				tree = etree.parse(fileobj)
				parsedString = etree.tostring(tree.getroot())
				# html = etree.HTML(parsedString)
				xpath = './/*[contains(text(),"'+ q +'")]'
			 
				matchedList = tree.xpath(xpath)
				# print len(matchedList)

				for word in matchedList:
					# copy the base
					item = baseitem.copy()

					# print word
					# print word.getparent()
					path = tree.getpath(word.getparent())
					path = path.split('/');

					# path of cfi
					cfi = cfiBase

					for part in path:
						if part == '*':
							cfi += "2"
						elif part:
							match = re.search(r"\d+", part)
							if match:
								num = int(match.group())
								cfi += "/" + str(num*2)
					
					item['cfi'] = cfi
					
					# check for span -> add class to whole span
					
					# token words
					# if len tokens > 13
						# get 6 words before and 6 words after
						# append <b class='match'> + word + </b>

					item['highlight'] = word.text # replace me with above
					
					r["results"].append(item)		
		return r