import os
import sys
from baseengine import BaseEngine
from cheshire3.baseObjects import Session
from cheshire3.server import SimpleServer
from cheshire3.internal import cheshire3Root
import json
import pdb

class Cheshire3Engine(BaseEngine):
    #schema = Schema(title=TEXT(stored=True), path=TEXT(stored=True), href=ID(stored=True), cfiBase=TEXT(stored=True), spinePos=TEXT(stored=True), content=TEXT)
    #database = 'db_tdo_simple_sru'
    cheshire_metadata_dir = '/cheshire3-metadata'
    session = Session()
    serverConfig = os.path.join(cheshire3Root, 'configs', 'serverConfig.xml')
    server = SimpleServer(session, serverConfig)
    queryFactory = None
    db = None
    sel = None


    def __initializeSelector(self):

        try:
            self.sel = self.db.get_object(self.session, 'titleXPathSelector')
        except ObjectDoesNotExistException:
            try:
                self.sel = self.db.get_object(self.session, 'titleSelector')
            except ObjectDoesNotExistException:
                pass

    def open(self):
        """ The Cheshire get_object line should throw an exception if it can't 
        open passed db
        """
        
        #pdb.set_trace()
        try:
            self.db = self.server.get_object(self.session, self.databaseName)
            self.session.database = self.databaseName
        except Exception, e:
            print "openning database {} failed".format(self.databaseName)

    def create(self):
        if not os.path.exists(self.databasePath):
            os.makedirs(self.databasePath)

        # create cheshire metadata directory if needed, then initialize with empty list
        metadata_path = self.databasePath + self.cheshire_metadata_dir  
        if not os.path.exists(metadata_path):
            os.makedirs(metadata_path)
        with open(metadata_path + '/' + self.databaseName, 'w') as f:
            json.dump({}, f)

        try:
            print "openning database {} to create".format(self.databasePath)
            os.system("cheshire3-init " + self.databasePath + " --database=" + self.databaseName)
        except Exception, e:
            print e

    def add(self, path='', href='', title='', cfiBase='', spinePos=''):
        # first, index the document in cheshire3 using unix commands
        os.system("cheshire3-load --database=" + self.databaseName + ' ' + path)
        
        doc_md = dict()
        doc_md[href] = {'path' : path, 'href' : href, 'title' : title, 'cfiBase' : cfiBase, 'spinePos' : spinePos}
        # title is not populated, so pulling filename from path prefix
        #filename = path[:path.find('/')] + '.json'
        metadata_path = self.databasePath + self.cheshire_metadata_dir
        with open(metadata_path + '/' + self.databaseName) as f_in:
            md_dict = json.load(f_in)
            
        md_dict.update(doc_md)

        with open(metadata_path + '/' + self.databaseName, 'w') as f_out:
            json.dump(md_dict, f_out)
        #print "Current Path for directory writing: " + os.getcwd()

    def finished(self):
        """ In Cheshire, there are no cleanup commands that are needed.  The add command
            will index specified documents fully and end, so a finished command is not required.
        """
        pass

    def query(self, q, limit=None):
        """ In Cheshire, the
        """

        if self.queryFactory == None:
            self.queryFactory = self.db.get_object(self.session, 'defaultQueryFactory')

        if self.sel is None:
            self.__initializeSelector()

        c3Query = self.queryFactory.get_query(self.session, q)
        rs = self.db.search(self.session, c3Query)

        # open up the json file with reader specific attributes
        metadata_path = self.databasePath + self.cheshire_metadata_dir  
        with open(metadata_path + '/' + self.databaseName) as f:
            db_md_dict = json.load(f)

        # loop through recordset, create new results list with dictionary of found values
        results = list()
        for rs_ins in rs:
            rec = rs_ins.fetch_record(self.session)
            # check the record titles
            titleData = self.sel.process_record(self.session, rec)
            fn_key = os.path.basename(titleData[3][0])
            #pdb.set_trace()
            results.append(db_md_dict[fn_key])

        return results



