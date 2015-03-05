import json
import os
import optparse

class MasterConfMaker:

    

    def __init__(self, data):
        self.cmsD=True
        self.data = json.loads(data)
        print self.data 
        print "****************************"   

    

    #make reco config
    def makeRecoCfg(self, name,era, GT, par):
        cfg='reco_%s_%s.py'%(era,name)

        hcal=',USER:EventFilter/HcalRawToDigi/hcallaserhbhehffilter2012_cff.hcallLaser2012Filter'
        from Configuration.AlCa.autoAlca import autoAlca
        alca=''
        if name in autoAlca:
            alca=',ALCA:@%s'%(name)

        reco=''
        if 'reco' in par:
            reco = par['reco']

        scenario=''
        if 'scenario' in par:
            scenario=par['scenario']

        dqm=''
        if 'dqm' in par:
            dqm = par['dqm']

        out='RECO' #out='AOD,DQM'
        if 'out' in par:
            out = par['out']

        fcn='--customise Configuration/DataProcessing/RecoTLR.customisePrompt'
        if 'fcn' in par:
            fcn = par['fcn']

        if 'conditions' in par:
            GT=par['conditions']

        com='cmsDriver.py reco -s RAW2DIGI,L1Reco,RECO%s%s%s,DQM%s --data --conditions %s --eventcontent %s --datatier %s %s %s --no_exec --python %s'%(
            reco,
            alca,
            hcal,
            dqm,
            GT,
            out,out,
            fcn,
            scenario,
            cfg)

        
        if self.cmsD:
            os.system(com)
        return cfg

    #make miniAOD config
    def makeMiniAODCfg(self, cfg, era, name, GT, par):
        
        step=''

        if cfg == '':
            cfg = 'reco_%s_%s.py'%(era,name)


        com1_steps='RAW2DIGI,L1Reco,RECO,EI,ALCA:SiStripCalZeroBias+SiStripCalMinBias+TkAlMinBias,DQM'
        
        com2_steps='PAT'

        com1 = 'cmsDriver.py step3  --conditions auto:run1_data_Fake --scenario pp --process reRECO --data  --eventcontent RECO,DQM --hltProcess reHLT -s %s --datatier RECO,DQMIO -n 2 --no_exec'% (com1_steps)
        com2 = 'cmsDriver.py step5  --conditions auto:run1_data_Fake -n 2 --data  --eventcontent MINIAOD --runUnscheduled  --filein file:step3.root -s %s --datatier MINIAOD --no_exec'%(com2_steps)

        if self.cmsD:
            os.system(com1)
            print com1
            os.system(com2)
            print com2

        return {"com1": com1_steps, "com2" : com2_steps}

    #make skim config
    skimoption=''
    def makeSkimCfg(self, name, era, GT, skim, par):
        from Configuration.Skimming.autoSkim import autoSkim
        skimoption=''
        fskim = ""
        
        for exp in autoSkim:
            if (exp == name):
                fskim = autoSkim[exp]
            elif (skim != "-"):
                fskim = skim
       
        if 'conditions' in par:
            GT=par['conditions']

        if 'skimoption' in par:
            skimoption=par['skimoption']    

        print "Found skim: %s , %s"%(name, fskim)    
        com='cmsDriver.py skim -s SKIM:%s --data --conditions %s --python_filenam skim_%s_%s.py --no_exec %s'%(fskim,GT,era,name,skimoption)
        if 'cosmic' in exp.lower():
            com+=' --scenario cosmics'
        if self.cmsD:
            os.system(com)
        return "skim_%s_%s.py"% (era, name)


    def makeMaster(self):

        GT = self.data['campaign1']['GT']
        cfg = ''

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

        #requests in campaign
        requests = self.data['campaign1']['req']
        GT = self.data['campaign1']['GT']

        runlists = {}
        for era in ['A','B','C','D']:
            runlists['2012%s'%era]=eval(os.popen('curl -s http://cms-pdmv.web.cern.ch/cms-pdmv/doc/DCS-json-2012eras/DCSjson-2012%s.txt'%era).read())
        era = self.data['campaign1']['era']

        for key, value in requests.iteritems():
            cfg = ''
            skim_file = ''
            mini_files = {}
            if 'RECO' in value['action']:
                print "RECO %s"%key
                cfg = self.makeRecoCfg(key, era, GT, value['action']['RECO'])

            if 'Skim' in value['action']:
                print "Skim %s"%key
                skim_file = self.makeSkimCfg(key, era, GT, value['skim'], value['action']['Skim'])

            if 'MiniAOD' in value['action']:
                print "Mini %s"%key
                mini_files = self.makeMiniAODCfg(cfg, era, key, GT, value['action']['MiniAOD'])

            site=''
            prio=int(self.data['campaign1']['prio'])
            dataset='/%s/Run%s-v1/RAW'%(key, era)
            runlist=[]
            if value['filter']:
                runlist=runlists[era]

            master.write('[Winter53%s%sPrio%d]\n'%(era, key, prio))
            master.write('campaign=Run%s\n'%(era))
            master.write('priority=%d\n'%( 70000 - 1000* prio ))
            master.write('dset_run_dict={"%s" : %s}\n'%(dataset, runlist))

            
            if (cfg != ''):
                master.write('cfg_path=%s\n'%(cfg))
            

            #if request['keep']=='TMP':
            #    master.write('transient_output = ["RECOoutput"]\n')
                
            if skim_file!='':
                master.write('skim_cfg=%s\n'%(skim_file))
                master.write('skim_name=%s\n'%(skim_file.replace('.py','')))

            if mini_files!={}:
                master.write('miniAOD_reco_cfg=%s\n'%(mini_files['com1']))
                master.write('miniAOD_cfg=%s'%(mini_files['com2']))

                #if not request['keep']:
                #    master.write('skim_input=AODoutput\n')

            master.write('\n\n')
        master.close()

        return file('master.conf','r').read()

if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option("--in",
                       dest="input"
                      )
    options,args=parser.parse_args()
    conf_maker = MasterConfMaker(options.input)

    conf_maker.makeMaster()



