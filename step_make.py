import json
import os
import optparse
import urllib2

class MasterConfMaker:

    def __init__(self, doc_id, DB_url):
        print "doc_id: %s" %doc_id
        self.url_address = DB_url
        self.opener = urllib2.build_opener(urllib2.HTTPHandler)
        self.cmsD=True
        self.data = self.get_file(doc_id)
        print '****************************'
        print self.data
        print "****************************"   

    def get_file(self, fileID):
        request = urllib2.Request(self.url_address +'/campaigns/' + fileID)
        request.add_header('Content-Type', 'text/plain')
        request.get_method = lambda: 'GET'
        url = self.opener.open(request)
        return json.loads(url.read())
    
    def makeMaster(self):
        GT = self.data['campaign1']['GT']
        drive = self.data['drive']
        del drive['Default']
        
        #make master config header
        master = file('master.conf','w')
        header = '''\
        [DEFAULT]
        group=ppd
        user=mliutkut
        request_type=ReReco
        release=%s
        globaltag=%s
        ''' % (os.getenv('CMSSW_VERSION'),GT)
        master.write(header)
        
        runlists = {}
        for era in ['A','B','C','D']:
            runlists['2012%s'%era]=eval(os.popen('curl -s http://cms-pdmv.web.cern.ch/cms-pdmv/doc/DCS-json-2012eras/DCSjson-2012%s.txt'%era).read())
        era = self.data['campaign1']['era']

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
            prio=int(self.data['campaign1']['prio'])
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
                master.write('miniAOD_cfg=%s'%(mini_file))

            master.write('\n\n')

        master.close()
        return file('master.conf','r').read()

if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option("--in",
                       dest="input"
                      )
    options,args=parser.parse_args()
    print "Options: %s" %options
    conf_maker = MasterConfMaker(options.input, 'http://moni.cern.ch:5984/')
    conf_maker.makeMaster()




