#!/usr/bin/env python
import os
import json
import pwd
import os.path
import urllib2
import subprocess
import sys  
import datetime
import xml.dom.minidom
import imp
from couchdb_interface import CouchDBInterface

from flask import Flask, send_from_directory, redirect, Response, make_response, request, jsonify
from subprocess import Popen, PIPE
app = Flask(__name__)
###original
WORK_DIR = '/afs/cern.ch/user/j/jsiderav/public/dataManagement/stuff'
WORKDIR = ''
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
    data['doc']['alca'] = data['alca']
    data['doc']['skim'] = data['skim']
    data['doc']['lumi'] = data['lumi']
    doc = json.dumps(data['doc'])
    doc_data = couch.update_file(_id, doc, _rev)
    return json.dumps(doc_data)

@app.route("/get_skim_matrix_value", methods=["GET", "POST"])
def get_skim_matrix_val():
    """
    Downloads the autoSkim matrix from the Git repo and passes it to Angular controller which
    updates the text field
    """
    file = "temporarySkim.py"
    data = json.loads(request.get_data())
    url = "https://raw.githubusercontent.com/cms-sw/cmssw/"+data['CMSSW']+"/Configuration/Skimming/python/autoSkim.py"
    response = urllib2.urlopen(url)
    fh = open(file, 'w')
    fh.write(response.read())
    fh.close()
    temp = imp.load_source("matrix","temporarySkim.py")
    return json.dumps(temp.autoSkim)

@app.route("/get_alca_matrix_value", methods=["GET", "POST"])
def get_alca_matrix_val():
    """
    Downloads the autoAlca matrix from the Git repo and passes it to Angular controller which
    updates the text field
    """
    file = "temporaryAlca.py"
    data = json.loads(request.get_data())
    url = "https://raw.githubusercontent.com/cms-sw/cmssw/"+data['CMSSW']+"/Configuration/AlCa/python/autoAlca.py"
    response = urllib2.urlopen(url)
    fh = open(file, 'w')
    fh.write(response.read())
    fh.close()
    temp2 = imp.load_source("matrix","temporaryAlca.py")
    return json.dumps(temp2.AlCaRecoMatrix)

@app.route('/save_doc', methods=["POST"])
def save_doc():
    """
    Puts a newly created object to the CouchDB
    """
    data = request.get_data()
    doc_data = couch.put_file(data)
    return json.dumps(doc_data)

def get_test_bash(__release, _id, __scram):
    """
    Small bash script generator which will initialize cms environment,
    and generate config files for the cmsRun command
    """
    #------------To get the config files of the datasets---------------------
    WORKDIR = "Test_Folder"
    comm = "#!/bin/bash\n"
    comm += "mkdir %s\n" %WORKDIR
    comm += "cd %s\n" %WORKDIR
    comm += "export SCRAM_ARCH=%s\n" %(__scram)
    comm += "source /afs/cern.ch/cms/cmsset_default.sh\n"
    comm += "scram project %s\n" % (__release)
    comm += "cd %s/src\n" % (__release)
    comm += "rm step_make.py\n"
    comm += "rm couchdb_interface.py\n"
    comm += "wget https://raw.githubusercontent.com/jonuuukas/dataManagement/master/step_make.py\n"
    comm += "wget https://raw.githubusercontent.com/jonuuukas/dataManagement/master/couchdb_interface.py\n"
    # comm += "eval `scram runtime -sh`\n"
    comm += "eval `scram runtime -sh` && python step_make.py --in=%s\n" % (_id)
    comm += "cat %s | voms-proxy-init -voms cms -pwstdin\n" %(cred)
    return comm

def get_submit_bash(__release, _id, __scram):
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
    comm += "cmsenv\n"
    # comm += "git cms-addpkg Configuration/Skimming\n"
    comm += "eval `scram runtime -sh`\n"
    # comm += "mkdir Configuration\n"
    # comm += "mkdir Skimming\n"
    # comm += "cd Configuration/Skimming\n"
    # comm += "wget https://raw.githubusercontent.com/cms-sw/cmssw/CMSSW_8_0_1/Configuration/Skimming/python/autoSkim.py\n"
    #####################LOCAL REPO IS CURRENTLY BEING USED FOR THE WGET LINES#################
    comm += "wget https://raw.githubusercontent.com/jonuuukas/dataManagement/master/step_make.py\n"
    comm += "wget https://raw.githubusercontent.com/jonuuukas/dataManagement/master/couchdb_interface.py\n"
    ######################################SEE ABOVE, NOOB######################################
    comm += "python step_make.py --in=%s\n" % (_id)
    #-------------For wmcontrol.py---------------------
    comm += "source /afs/cern.ch/cms/PPD/PdmV/tools/wmclient/current/etc/wmclient.sh\n" 
    comm += "export PATH=/afs/cern.ch/cms/PPD/PdmV/tools/wmcontrol_testful:${PATH}\n"
    comm += "cat %s | voms-proxy-init -voms cms -pwstdin\n" %(cred)
    comm += "echo 'executing scram runtime'\n"
    comm += "eval `scram runtime -sh`\n"
    comm += "echo 'executing export'\n"
    comm += "export X509_USER_PROXY=$(voms-proxy-info --path)\n"
    comm += "echo 'executing step wmcontrol.py'\n"
    comm += "wmcontrol.py --wmtest --req_file=master.conf\n"
    #--------------------------------------------------
    return comm 

@app.route('/test_campaign', methods=["GET","POST"])
def test_campaign():
    """
    Creates a bash script that will proceed with the config file generation and
    will run the cmsRun command without injecting it to request manager.
    Runs tests with all the datasets of the campaign and return jsons
    should be processed by the dataset name in controllers.js
    """
    data = json.loads(request.get_data())
    __release = data['CMSSW']
    _id = data['_id']
    _rev = data['_rev']
    req = data['req']
    doc = json.dumps(data['doc'])
    __scram = get_scram(__release)
    if __scram == '':
        return "No scram"
    #----------Creating & running bash file----------------------
    couch.update_file(_id, doc, _rev) #lets try this
    __curr_dir = os.getcwd()
    os.chdir(WORK_DIR)
    print("changed dir to /stuff")
    __exec_file = open("tmp_test.sh", "w")
    __exec_file.write(get_test_bash(__release, _id, __scram))
    __exec_file.close()
    log_file = file('logTest.txt','w')
    err_file = file('log2Test.txt','w')
    proc = subprocess.Popen(['bash', 'tmp_test.sh'],
                        stdout=log_file,stderr=err_file,close_fds=True)
    log_file.close()
    err_file.close()
    #_ret_code = proc.wait()
    print("finished running tmp_test")
    #raise Exception(str(_ret_code))
    #-----------------Running the cmsRun command-------------------------
    os.chdir("Test_Folder" + '/' + __release + '/' + "src/")
    cfgFile = open("master.conf","r")
    i = 0   #loop needed to cycle through all the datasets and differ gathered information based on the dataset name
    dynamicLogger={}
    print ("starting the loop thrtough master.conf")
    rev = couch.get_file(_id)['_rev']
    
    for line in cfgFile:
        if line.startswith("cfg_path="):

            arg = line[9:]
            dynamicLogger[req.keys()[i]] = {}
            log_file = file(str(i)+ "log.txt", "w+")
            err_file = file(str(i)+ "errLog.txt", "w+")

            proc = subprocess.call(('eval `scram runtime -sh` && cmsRun -n 10 %s') %(arg),stdout=log_file,stderr=err_file, shell=True, close_fds=True)

            log_file.seek(0)
            err_file.seek(0)
            dynamicLogger[req.keys()[i]]['stderr']= err_file.read() 
            dynamicLogger[req.keys()[i]]['stdout']= log_file.read()

            log_file.close()
            err_file.close()
            couch.upload_attachment(_id, rev, str(i)+ "errLog.txt")

            
            
            if str(dynamicLogger[req.keys()[i]]['stderr']).find("Begin fatal exception"):
                dynamicLogger['flag']="Fatality"    #subzero ftw
            i+=1
    cfgFile.close()
#-----------------Uploading log file-------------------------
    print("finished looping. returning to the AngularJS")
    os.chdir(__curr_dir) ## back to working dir
    return json.dumps(dynamicLogger)

@app.route('/submit_campaign', methods=["POST"])
def submit_campaign():
    """
    Executes the submit button by updating the current campaign, creating/executing the script in get_submit_bash()
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
    couch.update_file(_id, doc, _rev)
    #----------Creating & running bash file----------------------
    __curr_dir = os.getcwd()
    os.chdir(WORK_DIR)
    __exec_file = open("tmp_execute.sh", "w")
    __exec_file.write(get_submit_bash(__release, _id, __scram))
    __exec_file.close()
    log_file = file('log.txt','w')
    err_file = file('log2.txt','w')
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
