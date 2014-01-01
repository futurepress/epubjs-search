import importlib
import sys
import engines
from lxml import etree
import re

class EpubIndexer(object):
    epub = False
    engine = False

    def __init__(self, engineName=False, databaseName='indexdir'):
        if engineName:
            mod = importlib.import_module("epubsearch.engines.%sengine" % engineName)
            # import whooshengine as engine
            self.engine = getattr(mod,'%sEngine' % engineName.capitalize())(databaseName)
            print self.engine

    def load(self, epub):
        self.epub = epub
        self.engine.create()

        for spineItem in epub.spine:

            path = epub.base + "/" + spineItem['href']

            self.engine.add(path=path, href=spineItem['href'], title=spineItem['title'], cfiBase=spineItem['cfiBase'], spinePos=spineItem['spinePos'])

        self.engine.finished()

    def search(self, q, limit=None):
        rawresults = self.engine.query(q, limit)
        # print len(rawresults)
        r = {}
        r["results"] = []
        q = q.lower()

        for hit in rawresults:
            baseitem = {}
            baseitem['title'] = hit["title"]
            baseitem['href'] = hit["href"]
            baseitem['path'] = hit["path"]

            # find base of cfi
            cfiBase = hit['cfiBase'] + "!"

            with open(hit["path"]) as fileobj:
                tree = etree.parse(fileobj)
                parsedString = etree.tostring(tree.getroot())
                # case-insensitive xpath search
                xpath = './/*[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz") , "'+ q + '")]'
                #xpath = './/*[contains(text(),"'+ q +'")]'

                matchedList = tree.xpath(xpath)
                # print len(matchedList)
                for word in matchedList:
                    # copy the base
                    item = baseitem.copy()

                    # print word
                    # print word.getparent()
                    item['baseCfi'] = cfiBase
                    item['cfi'] = getCFI(cfiBase, word)
                    #print cfi

                    # Create highlight snippet in try / except
                    # because I'm not convinced its error free for all
                    # epub texts
                    try:
                        item['highlight'] = createHighlight(word.text, q) # replace me with above
                    except Exception as e:
                        print "Exception when creating highlight for query", q
                        print(e)
                        item['highlight'] = ''

                    #item['highlight'] = word.text
                    r["results"].append(item)

        ## Sort results by chapter
        r['results'] = sorted(r['results'], key=lambda x: getCFIChapter(x['baseCfi']))
        return r


def getCFI(cfiBase, word):

    cfi_list = []
    parent = word.getparent()
    child = word
    while parent is not None:
        i = parent.index(child)
        if 'id' in child.attrib:
            cfi_list.insert(0,str((i+1)*2)+'[' + child.attrib['id'] + ']')
        else:
            cfi_list.insert(0,str((i+1)*2))
        child = parent
        parent = child.getparent()

    cfi = cfiBase + '/' + '/'.join(cfi_list)
    return cfi

def getCFIChapter(cfiBase):
    cfiBase = re.sub(r'\[.*\]','',cfiBase)
    chapter_location = cfiBase[cfiBase.rfind('/')+1:cfiBase.find('!')]
    return int(chapter_location)

def createHighlight(text, query):
    tag = "<b class='match'>"
    closetag = "</b>"
    offset = len(query)

    leading_text = trimLength(text[:text.lower().find(query)],-10) + tag
    word = text[text.lower().find(query):text.lower().find(query)+offset]
    ending_text = closetag + trimLength(text[text.lower().find(query)+offset:],10)

    return leading_text + word + endWithPeriods(ending_text)

def trimLength(text, words):
    if words > 0:
        text_list = text.split(' ')[:words]
    else:
        text_list = text.split(' ')[words:]

    return ' '.join(text_list)

def endWithPeriods(text):
    if text[-1] not in '!?.':
        return text + ' ...'
    else:
        return text
