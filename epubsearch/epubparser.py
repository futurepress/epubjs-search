from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from lxml import etree

import os

class EpubParser(object):
    base = ''
    manifest = {}
    titles = {}
    spine = []
    spineElementNum = str(6) #replace this with xml check for which child of root 'spine' is x 2

    def __init__(self, path):
        folder = path  + "/"
        if os.path.isdir(folder) == True:
            rootfile = self.parseRootFile(folder)
            if rootfile:
                self.rootfile = rootfile
                self.base = folder + os.path.dirname(rootfile)
                self.manifest = self.parseManifest(folder + rootfile)
                self.tocPath = self.getTocPath(self.manifest)

            if self.tocPath:
                self.toc = self.parseToc(self.base + "/" + self.tocPath)

            self.spine = self.parseSpine(folder + rootfile)
        else :
            raise EpubError("No Rootfile found")

    def parseRootFile(self, folder):
        container = folder + "/META-INF/container.xml";

        if os.path.isfile(container):
            tree = ET.parse(container)
            root = tree.getroot()

            for rootfiles in root:
                for rf in rootfiles:
                    rootfile = rf.attrib['full-path']
                    return rootfile # Stop at first rootfile for now

        else:
            raise EpubError('No container.xml found')

        return False;

    def parseMetadata(self, filename):
        raise NotImplementedError

    def parseManifest(self, filename):
        """
        Parse the content.opf file.
        """
        namespaces = {'xmlns': 'http://www.idpf.org/2007/opf',
            'dc':'http://purl.org/dc/elements/1.1/',
            'dcterms':'http://purl.org/dc/terms/'}

        print "Parsing Manifest"

        items = {}

        # begin parsing content.opf
        tree = ET.parse(filename)
        root = tree.getroot()
        # extract item hrefs and place in return list
        for child in root.findall('xmlns:manifest/xmlns:item', namespaces=namespaces):
            itemId = child.attrib['id'];

            if not itemId in items:
                items[itemId] = {}
                items[itemId]["href"] = child.attrib['href']
                items[itemId]["media-type"] = child.attrib['media-type']

        return items

    def getTocPath(self, manifest):
        """
        From the manifest items, find the item for the Toc
        Return the Toc href
        """
        if "ncxtoc" in manifest:
            return manifest["ncxtoc"]["href"]
        else:
            for item in manifest.values():
                if item["media-type"] == "application/x-dtbncx+xml":
                    return item["href"]

        raise EpubError("No Toc File Found")

    def parseToc(self, filename):
        namespaces = {'xmlns': 'http://www.daisy.org/z3986/2005/ncx/'}

        print "Parsing TOC"

        items = []

        # begin parsing content.opf
        #tree = ET.parse(filename)
        #root = tree.getroot()
        tree = etree.parse(filename)
        root = tree.getroot()

        # extract item hrefs and place in return list
        for navPoint in root.findall('xmlns:navMap/xmlns:navPoint', namespaces=namespaces):
            navLabel = navPoint.find('xmlns:navLabel', namespaces=namespaces)
            title = navLabel.getchildren()[0].text.encode("utf-8")
            href = navPoint.getchildren()[1].attrib['src'].encode("utf-8")
            item = {}

            item['id'] = navPoint.attrib['id']
            item['title'] = title
            self.titles[href] = title
            items.append(item)

        return items

    def parseSpine(self, filename):
        """
            Parse the content.opf file.
        """
        namespaces = {'xmlns': 'http://www.idpf.org/2007/opf',
                'dc':'http://purl.org/dc/elements/1.1/',
                'dcterms':'http://purl.org/dc/terms/'}

        print "Parsing Spine"

        spinePos = 1;

        items = []

        # begin parsing content.opf
        tree = ET.parse(filename)
        root = tree.getroot()
        # extract item hrefs and place in return list
        for child in root.findall('xmlns:spine/xmlns:itemref', namespaces=namespaces):
            item = {}

            item["idref"] = child.attrib['idref']
            item["spinePos"] = spinePos;

            item["cfiBase"] = "/".join([self.spineElementNum, str(spinePos*2)])

            if item["idref"] in self.manifest:
                item["href"] = self.manifest[item["idref"]]['href']

            # print self.titles
            if self.titles and item["href"] in self.titles:
                item['title'] = self.titles[item["href"]]
            else:
                item['title'] = ''

            items.append(item)

            spinePos += 1

        return items

class EpubError(Exception):
    pass
