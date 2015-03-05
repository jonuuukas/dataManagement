import os
import json
import pwd
import os.path

from flask import Flask, send_from_directory, redirect, Response, make_response, request
from subprocess import Popen, PIPE
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def hello():
    return send_from_directory('templates', 'index.html')

@app.route('/get_data', methods=["POST"])
def get_data():
    data = request.get_data()
    __release = (json.loads(data))['campaign1']['CMSSW']  #"CMSSW_7_4_0_pre6"
    #if os.path.isdir(os.path.join("..", __release, "src", "master.conf")):
    comm = "#!/bin/bash\n"
    comm += "cd ..\n"
    comm += "export SCRAM_ARCH=slc6_amd64_gcc472\n"
    comm += "source /afs/cern.ch/cms/cmsset_default.sh\n"
    comm += "scram p CMSSW %s\n" % (__release)
    comm += "cd %s/src\n" % (__release)
    comm += "eval `scram runtime -sh`\n"
    comm += "whoami\n"
    comm += "git-cms-addpkg Configuration/Skimming\n"
    comm += "cp ../../app/step_make.py .\n"#"cp ../../step_make.py .\n"
    comm += "cp ../../app/in.txt .\n"#"cp ../../in.txt .\n"
    comm += "python step_make.py --in=%s\n" % (json.dumps(data))
    __tmp_file = open("tmp_execute.sh", "w")
    __tmp_file.write(comm)
    __tmp_file.close()
    os.system("bash tmp_execute.sh")
    make = os.path.isfile(os.path.join(__release, "src", "master.conf"))

    if make:
        response = make_response(file('master.conf','r').read())
        response.headers['Content-Disposition'] = "attachment; filename=master.conf"
    else:
        response = json.dumps({"results" : make})

    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
