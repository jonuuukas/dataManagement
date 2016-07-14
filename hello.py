import os
import json
import pwd
import os.path
import urllib2
import subprocess
import sys
import datetime
import xml.dom.minidom
from couchdb_interface import CouchDBInterface

from flask import Flask, send_from_directory, redirect, Response, make_response, request, jsonify
from subprocess import Popen, PIPE
app = Flask(__name__)
###original
WORK_DIR = '/afs/cern.ch/user/j/jsiderav/public/dataManagement/stuff'
couch = CouchDBInterface()
cred = '/afs/cern.ch/user/j/jsiderav/private/PdmVService.txt'
###
###Replaced with below
# WORK_DIR = '/home/dataManagement/stuff'
# couch = CouchDBInterface()
# cred = '/afs/cern.ch/user/j/jsiderav/private/PdmVService.txt'
@app.route("/", methods=["GET", "POST"])
def hello():
    """
    Opening function that directs to index.html
    """
    return send_from_directory('templates', 'index.html')
@app.route('/api/help', methods = ['GET'])
def help():
    """Print available functions."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)
def get_scram(__release):
    """
    By the given __release version checks with the scram architecture versions'
    and returns the architecture name if found
    """
    scram = ''
    xml_data = xml.dom.minidom.parseString(os.popen("curl -s --insecure 'https://cmssdt.cern.ch/SDT/cgi-bin/ReleasesXML/?anytype=1'").read())
    
    for arch in xml_data.documentElement.getElementsByTagName("architecture"):
        scram_arch = arch.getAttribute('name')
        for project in arch.getElementsByTagName("project"):
            release = str(project.getAttribute('label'))
            if release == __release:
                scram = scram_arch
    
    return scram

@app.route('/load_data', methods=["POST"])
def load_data():
    """
    Communicates with the CouchDB and returns the object
    according to it's _id as a JSON
    """
    data = json.loads(request.get_data())
    _id = data['_id']
    doc_data = couch.get_file(_id)
    return json.dumps(doc_data)

@app.route('/get_all_docs', methods=["GET"])
def get_all_docs():
    """
    Used in saveDocs() function to get all docs and later for the 
    object to be pushed in to the data list
    """
    info = couch.get_all_docs()
    return json.dumps(info)

@app.route('/update_file', methods=["POST"])
def update_file():
    """
    Gets the object from the browser and updates it in the CouchDB
    """
    data = json.loads(request.get_data())
    _id = data['_id']
    _rev = data['_rev']
    doc = json.dumps(data['doc'])
    doc_data = couch.update_file(_id, doc, _rev)
    return json.dumps(doc_data)

@app.route('/save_doc', methods=["POST"])
def save_doc():
    """
    Puts a newly created object to the CouchDB
    """
    data = request.get_data()
    doc_data = couch.put_file(data)
    return json.dumps(doc_data)

def get_bash(__release, _id, __scram):
    """
    Returns the stuff/tmp_execute.sh script that communicates with various CMSSW functions
    according to the current campaign submit data
    """
    #------------To checkout CMSSW---------------------
    WORKDIR = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M')
    comm = "#!/bin/bash\n"
    comm += "mkdir %s\n" %WORKDIR
    comm += "cd %s\n" %WORKDIR
    comm += "export SCRAM_ARCH=%s\n" %(__scram)
    comm += "source /afs/cern.ch/cms/cmsset_default.sh\n"
    comm += "scram project %s\n" % (__release)
    comm += "cd %s/src\n" % (__release)
    comm += "eval `scram runtime -sh`\n"
    comm += "cmsenv\n"
    comm += "git cms-addpkg Configuration/Skimming\n"
    #####################LOCAL REPO IS CURRENTLY BEING USED FOR THE WGET LINES#################
    comm += "wget https://raw.githubusercontent.com/jonuuukas/dataManagement/master/step_make.py\n"
    comm += "wget https://raw.githubusercontent.com/jonuuukas/dataManagement/master/couchdb_interface.py\n"
    ######################################SEE ABOVE, NOOB######################################
    comm += "python step_make.py --in=%s\n" % (_id)
    #-------------For wmcontrol.py---------------------
    comm += "source /afs/cern.ch/cms/PPD/PdmV/tools/wmclient/current/etc/wmclient.sh\n" 
    comm += "export PATH=/afs/cern.ch/cms/PPD/PdmV/tools/wmcontrol_testful:${PATH}\n"
    comm += "cat %s | voms-proxy-init -voms cms -pwstdin\n" %(cred)
    comm += "eval `scram runtime -sh`\n"
    comm += "export X509_USER_PROXY=$(voms-proxy-info --path)\n"
    comm += "wmcontrol.py --wmtest --req_file=master.conf\n"
    #--------------------------------------------------
    return comm 

@app.route('/submit_campaign', methods=["POST"])
def submit_campaign():
    """
    Executes the submit button by updating the current campaign, creating/executing the script in get_bash()
    Logs of the process can be found in the WORK_DIR variable location and a log is also uploaded to the CouchDB
    together with the object
    """
    data = json.loads(request.get_data())

    __release = data['CMSSW']
    _id = data['_id']
    _rev = data['_rev']
    doc = json.dumps(data['doc'])

    __scram = get_scram(__release)
    if __scram == '':
        return "No scram"
    #update document
    couch.update_file(_id, doc, _rev)
    #----------Creating & running bash file----------------------
    __curr_dir = os.getcwd()
    os.chdir(WORK_DIR)
    __exec_file = open("tmp_execute.sh", "w")
    __exec_file.write(get_bash(__release, _id, __scram))
    __exec_file.close()
    log_file = file('log.txt','w')
    err_file = file('log2.txt','w')
    ###changing close_fds to True
    proc = subprocess.Popen(['bash', 'tmp_execute.sh'],
                        stdout=log_file,stderr=err_file,close_fds=True)
    __ret_code = proc.wait()
    log_file.close()
    err_file.close()
    #-----------------Uploading log file-------------------------
    rev = couch.get_file(_id)['_rev']
    couch.upload_attachment(_id, rev, 'log.txt')

    os.chdir(__curr_dir) ## back to working dir
    return str(__ret_code)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
