# import stuff

class Cheshire3Engine(object):

    def __init__(self, indexdir="indexdir"):
        pass

    def create(self):
        pass

    def add(self, filename='', href='', title='', cfiBase='', spinePos=''): 
        '''
        load one file at a time
        '''

    def finished(self):
        pass

    def query(self, q, limit=None):
        '''
        item['title']
        item['href']
        item['path']
        item['title']
        item['cfiBase']
        item['spinePos']
        '''
        results = []

        for hit in hits:
            item = {}
            item['title'] = hit.title
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
