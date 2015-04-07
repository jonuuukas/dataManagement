import json
import os
import optparse
import urllib2
from couchdb_interface import CouchDBInterface

class MasterConfMaker:
    """
    A class that forms master.conf file
    """

    def __init__(self, doc_id, DB_url):
        """
        init a class
        """
        print "doc_id: %s" %doc_id
        self.couch = CouchDBInterface(DB_url)
        self.cmsD = True
        self.data = self.couch.get_file(doc_id)
    
    def makeMaster(self):
        """
        method to form configuration files
        """
        GT = self.data['data']['GT']
        drive = self.data['drive']
        del drive['Default']
        
        #make master config header
        master = file('master.conf','w')
        header = "[DEFAULT]\n"
        header += "group=ppd\n"
        header += "user=mliutkut\n"
        header += "request_type=ReReco\n"
        header += "release=%s\n"
        header += "globaltag=%s\n" % (os.getenv('CMSSW_VERSION'), GT)
        master.write(header)
        
        runlists = {}
        for era in ['A','B','C','D']:
            runlist_link = 'http://cms-pdmv.web.cern.ch/cms-pdmv/doc/DCS-json-2012eras/DCSjson-2012%s.txt'%era
            runlists['2012%s'%era] = eval(os.popen('curl -s %s'%runlist_link).read())
        era = self.data['data']['era']

        #read all drivers and execute
        for ds in drive:
            cfg = ''
            skim_file = ''
            mini_file = ''
            for action in drive[ds]:
                com = drive[ds][action]
                print com
                if com != '' and com != {}:
                    os.system(com)
                    if action == 'reco':
                        param = com.split()
                        index = param.index("--python") + 1
                        cfg = param[index]
                    if action == 'skim':
                        param = com.split()
                        index = param.index("--python_filename") + 1
                        skim_file = param[index]
                    if action == 'mini':
                        param = com.split()
                        index = param.index("--python_filename") + 1
                        mini_file = param[index]

            site=''
            ds = ds.split("/")[1]
            prio=int(self.data['data']['prio'])
            dataset='/%s/Run%s-v1/RAW'%(ds, era)
            runlist=[]
            if True:
                runlist=runlists[era]

            master.write('[Winter53%s%sPrio%d]\n'%(era, ds, prio))
            master.write('campaign=Run%s\n'%(era))
            master.write('priority=%d\n'%( 70000 - 1000* prio ))
            master.write('dset_run_dict={"%s" : %s}\n'%(dataset, runlist))
            
            if (cfg != ''):
                master.write('cfg_path=%s\n'%(cfg))
            if skim_file!='':
                master.write('skim_cfg=%s\n'%(skim_file))
                master.write('skim_name=%s\n'%(skim_file.replace('.py','')))
            if mini_file!='':
                if cfg != '':
                    master.write('step2_cfg=%s'%(mini_file))
                else:
                    master.write('cfg_path=%s'%(mini_file))

            master.write('\n\n')

        master.close()
        return file('master.conf','r').read()

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("--in", dest="input")
    options,args=parser.parse_args()
    conf_maker = MasterConfMaker(options.input, 'http://moni.cern.ch:5984/campaigns/')
    conf_maker.makeMaster()