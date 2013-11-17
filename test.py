from epubsearch import EpubParser
from epubsearch import EpubIndexer
# from epubsearch import EpubRetriever

epub = EpubParser("moby-dick")

index = EpubIndexer("whoosh")
index.load(epub)

results = index.search("Moby", 2)
if results:
    print results['results'][0]
