from whoosh.index import create_in
import whoosh.index as index
from whoosh.fields import *
from bs4 import BeautifulSoup
from whoosh.qparser import QueryParser

class WhooshEngine(object):
    # whoosh
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), href=ID(stored=True), cfiBase=TEXT(stored=True), spinePos=TEXT(stored=True), content=TEXT)
    indexdir = ''

    def __init__(self, indexdir="indexdir"):
        self.indexdir = indexdir

        try:
            self.ix = index.open_dir("indexdir")
        except Exception, e:
            raise "No DB"

    def create(self):
        try:
            self.ix = index.open_dir("indexdir")
        except Exception, e:
            self.create()
            print "No DB, creating"

        self.writer = self.ix.writer()
    
    def add(self, filename='', href='', title='', cfiBase='', spinePos=''):
        text = self.__get_text(filename)
        self.writer.add_document(title=unicode(title.decode('utf-8')), path=unicode(filename), href=unicode(href), cfiBase=unicode(cfiBase), spinePos=unicode(spinePos), content=unicode(text))
        print "Indexed: " + title + ' | ' + filename + ' | ' + href + ' | ' + str(spinePos)

    def finished(self):
        self.writer.commit()

    def query(self, q, limit=None):
        with self.ix.searcher() as searcher:
            results = []
            parsedQuery = QueryParser("content", self.ix.schema).parse(q)
            hits = searcher.search(parsedQuery, limit=limit)

            for hit in hits:
                item = {}
                item['title'] = hit["title"].encode("utf-8")
                item['href'] = hit["href"].encode("utf-8")
                item['path'] = hit["path"].encode("utf-8")
                item['title'] = hit["title"].encode("utf-8")
                item['cfiBase'] = hit["cfiBase"].encode("utf-8")
                item['spinePos'] = hit["spinePos"].encode("utf-8")

                with open(hit["path"]) as fileobj:
                    filecontents = fileobj.read().decode("utf-8")
                    item['highlight'] = hit.highlights("content", text=filecontents).encode("utf-8")

                results.append(item)

            return results

    def __get_text(self, filename):
        # html = urllib.urlopen('http://www.nytimes.com/2009/12/21/us/21storm.html').read()
        html = open(filename, "r")
        soup = BeautifulSoup(html)
        texts = soup.findAll(text=True)

        def visible(element):
                if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
                        return False
                elif re.match('<!--.*-->', str(element.encode('utf-8'))):
                        return False
                return True

        visible_texts = filter(visible, texts)

        contents = ' '.join([s for s in visible_texts])

        return contents.strip() #.encode('utf-8')
