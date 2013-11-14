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
                self.base = folder + os.path.dirname(rootfile)
                self.manifest = self.parseManifest(folder + rootfile)

            if self.tocPath:
                self.toc = self.parseToc(self.base + "/" + self.tocPath)

            self.spine = self.parseSpine(folder + rootfile)
        else :
            raise "No Rootfile found"

    def parseRootFile(self, folder):
        container = folder + "/META-INF/container.xml";
        rootfile = False;

        if os.path.isfile(container):
            tree = ET.parse(container)
            root = tree.getroot()

            for rootfiles in root:
                for rf in rootfiles:
                    rootfile = rf.attrib['full-path']
                    return rootfile # Stop at first rootfile for now

        else:
            raise("No container.xml found")
        return False;

    def parseManifest(self, filename):
        """
        Parse the content.opf file.  Is it good practice to close file used
        for ElementTree processing?
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
                if items[itemId]["media-type"] == "application/x-dtbncx+xml":
                    self.tocPath = items[itemId]["href"]

        return items

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
            Parse the content.opf file.  Is it good practice to close file used
            for ElementTree processing?
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

            print self.titles
            if self.titles and item["href"] in self.titles:
                item['title'] = self.titles[item["href"]]
            else:
                item['title'] = ''

            items.append(item)

            spinePos += 1

        return items
