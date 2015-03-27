import json
import os
import urllib2

class CouchDBInterface:
    """
    A class as interface to couchdb via HTTP protocol
    """

    def __init__ (self, db_url):
        """
        init a class
        """
        self.url_address = db_url
        self.opener = urllib2.build_opener(urllib2.HTTPHandler)

    def put_file(self, stringToPut):
        request = urllib2.Request(self.url_address + '/campaigns', data=stringToPut)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'POST'
        url = self.opener.open(request)
        return json.loads(url.read())


    def get_file(self, fileID):
        """
        method to get a document from couchDB when specified a document ID
        """
        request = urllib2.Request(self.url_address +'/campaigns/' + fileID)
        request.add_header('Content-Type', 'text/plain')
        request.get_method = lambda: 'GET'
        try:
            url = self.opener.open(request)
            return json.loads(url.read())
        except:
            print "Failed"

    def delete_file(self, fileID, rev):
        """
        method to delete a document from couchDB when specified a document ID
        """
        request = urllib2.Request(self.url_address+'/campaigns/'+fileID+'?rev='+rev)
        request.add_header('Content-Type', 'text/plain')
        request.get_method = lambda: 'DELETE'
        try:
            url = self.opener.open(request)
            return json.loads(url.read())
        except:
            print "Failed delete"

    def update_file(self, fileID, stringToPut,rev):
        ##string must be a updated file name with the newest revision, it will be updated by DB itself
        request = urllib2.Request(self.url_address+'/campaigns/'+fileID + "?rev=" + rev, data=stringToPut)
        request.add_header('Content-Type', 'text/plain')
        request.get_method = lambda: 'PUT'
        url = self.opener.open(request)
        return json.loads(url.read())

    def upload_attachment(self, fileID, rev, up_file):
        with open(up_file, mode='r') as in_file:
            out_data =  in_file.read()
        request = urllib2.Request(self.url_address+'/campaigns/'+fileID + "/log.txt"+"?rev=" + rev)
        request.add_header('Content-Type', 'text/plain')
        request.add_header('Content-Length', len(out_data))
        request.add_data(out_data)
        request.get_method = lambda: 'PUT'
        url = self.opener.open(request)
        return json.loads(url.read())

    def get_head(self, fileID):
        request = urllib2.Request(self.url_address+'/campaigns/'+fileID)
        request.get_method = lambda : 'HEAD'
        url = self.opener.open(request)
        print url.info().__str__()
        print url.read()
        print url.__getitem__()
        return ""#json.loads(url.read())

    def get_all_docs(self):
        request = urllib2.Request(self.url_address+'/campaigns/_all_docs')
        request.get_method = lambda : 'GET'
        request.add_header('Content-Type', 'text/plain')
        url = self.opener.open(request)
        return json.loads(url.read())
