import os
import json
import pwd
import os.path
import urllib2
import subprocess
import sys
from couchdb_interface import *

from flask import Flask, send_from_directory, redirect, Response, make_response, request
from subprocess import Popen, PIPE
app = Flask(__name__)

couch = CouchDBInterface('http://moni.cern.ch:5984/')

@app.route("/", methods=["GET", "POST"])
def hello():
    return send_from_directory('templates', 'index.html')

@app.route('/load_data', methods=["POST"])
def load_data():
    data = request.get_data()
    _id = (json.loads(data))['_id']
    doc_data = couch.get_file(_id)
    return json.dumps(doc_data)

@app.route('/get_all_docs', methods=["GET"])
def get_all_docs():
    info = couch.get_all_docs()
    return json.dumps(info)

@app.route('/update_file', methods=["POST"])
def update_file():
    data = request.get_data()
    _id = (json.loads(data))['_id']
    doc = json.dumps((json.loads(data))['doc'])
    _rev = (json.loads(data))['_rev']
    doc_data = couch.update_file(_id, doc, _rev)
    return json.dumps(doc_data)

@app.route('/save_doc', methods=["POST"])
def save_doc():
    data = request.get_data()
    doc_data = couch.put_file(data)
    print doc_data
    return json.dumps(doc_data)

@app.route('/submit_campaign', methods=["POST"])
def submit_campaign():
    data = request.get_data()

    __release = (json.loads(data))['CMSSW']
    _id = (json.loads(data))['_id']
    _rev = (json.loads(data))['_rev']
    doc = json.dumps((json.loads(data))['doc'])

    #update document
    couch.update_file(_id, doc, _rev)
    #chekout CMSSW
    comm = "#!/bin/bash\n"
    comm += "pwd\n"
    comm += "cd ..\n"
    if os.path.isdir(os.path.join("..", __release)):
        comm += "rm -rf %s\n" %__release
    comm += "export SCRAM_ARCH=slc6_amd64_gcc481\n"
    comm += "source /afs/cern.ch/cms/cmsset_default.sh\n"
    comm += "scram p CMSSW %s\n" % (__release)
    comm += "cd %s/src\n" % (__release)
    comm += "eval `scram runtime -sh`\n"
    comm += "git-cms-addpkg Configuration/Skimming\n"
    comm += "cp ../../dataManagement/step_make.py .\n"
    comm += "cp ../../dataManagement/couchdb_interface.py .\n"
    comm += "python step_make.py --in=%s\n" % (_id)
    #----------------------------------
    comm += "source /afs/cern.ch/cms/PPD/PdmV/tools/wmclient/current/etc/wmclient.sh\n" 
    comm += "export PATH=/afs/cern.ch/cms/PPD/PdmV/tools/wmcontrol:${PATH}\n"
    comm += "cat /afs/cern.ch/user/m/mliutkut/private/PdmVService.txt | voms-proxy-init -voms cms -pwstdin\n"
    comm += "eval `scram runtime -sh`\n"
    comm += "export X509_USER_PROXY=$(voms-proxy-info --path)\n"
    comm += "wmcontrol.py --wmtest --req_file=master.conf\n"
    #---------------------------------------
    __tmp_file = open("tmp_execute.sh", "w")
    __tmp_file.write(comm)
    __tmp_file.close()
    
    log_file = file('log.txt','w')
    err_file = file('log2.txt','w')
    proc = subprocess.Popen(['bash', 'tmp_execute.sh'],
                        stdout=log_file,stderr=err_file)
    __ret_code = proc.wait()
    log_file.close()
    err_file.close()

    rev = couch.get_file(_id)['_rev']
    couch.upload_attachment(_id, rev, 'log.txt')
    return str(__ret_code)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
