class EpubRetriever(object):
    def __init__(self, engineName=False):
        if engineName:
            mod = importlib.import_module("epubsearch.engines.%sengine" % engineName)
            self.engine = getattr(mod,'%sEngine' % engineName.capitalize())()
            print self.engine
