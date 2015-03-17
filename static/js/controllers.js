var myApp = angular.module('myApp', ['ui.bootstrap']);
myApp.controller('myAppCtrl', function ($scope, $http, $location) {
  $scope.data = {"CMSSW":"CMSSW_7_4_0_pre6", "GT": "GT_FAKE", "era":"2012A", "prio": 7, "req":{}};
  $scope.check = {};
  $scope.alca = {};
  $scope.skim = {};
  $scope.drive = {};
  $scope.checkAll = {reco : false, skim : false, mini :false};
  $scope.actionDict = {"reco":"reco", "skim":"skim", "mini":"mini"};
  $scope.allOpt = {"Default" : {}};
  $scope.defCon = {};
  $scope.recoOpt = {
                    "steps" : "steps",
                    "conditions": "conditions", 
                  };
  $scope.skimOpt = {
                  "steps" : "steps",
                  "conditions": "conditions", 
                  "skimoption": "skimoption"
                  };

  $scope.miniOpt = {
                  "steps": "steps", 
                  "conditions": "conditions"
                  };

  $scope.defOpt = {"reco" : $scope.recoOpt, "skim" : $scope.skimOpt, "mini" : $scope.miniOpt};

  $scope.addReq = function(name)
  {
    console.log("addReq: " + name);   
    if (!(name in $scope.data['req'])){
      name = name || "NewDataSet";
      $scope.data['req'][name] = {"id": name, "filter": true, "action": {}};

      $scope.check[name] = {reco : false, skim : false, mini :false};
      
      if ($scope.drive[name] == undefined){
        $scope.drive[name] = {};
      }
      if ($scope.allOpt[name] == undefined){
              $scope.allOpt[name] = {};
      }

      for (key in $scope.check[name]){
        
        if ($scope.drive[name][key] == undefined){
          $scope.drive[name][key] = {};
        }

        if ($scope.checkAll[key]){
          $scope.check[name][key] = true;
          $scope.allOpt[name][action] = JSON.parse(JSON.stringify($scope.defOpt[action]));
          $scope.allOpt[name][key] = JSON.parse(JSON.stringify($scope.allOpt['Default'][key]));
          $scope.data['req'][name]['action'][key] = {};
          if ($scope.defCon[key] != undefined){
            $scope.data['req'][name]['action'][key] = JSON.parse(JSON.stringify($scope.defCon[key]));
          }
        }

        $scope.checkAlca(name);
        $scope.checkSkim(name);
      }
    }else{
      alert("Dataset name already exists");
    }
  };

  $scope.addExtra = function(ds, action, name, miniOpt)
  {   
    if (name == undefined){
      alert("No extra name");
    } else{
      $scope.allOpt[ds][action][name] = name;
    }
  };

  $scope.addDefExtra = function(ds, action, name)
  {   
    if (name == undefined){
      alert("No extra name");
    } else{
      for (dataset in $scope.allOpt){
        $scope.allOpt[dataset][action][name] = name;
      }
    }
  };

  $scope.removeReq = function(name)
  {   
    if ((name in $scope.data['req'])){
      delete $scope.data['req'][name];
    }  
  };

  $scope.removeExtra = function(ds, action, name)
  {
    console.log("removeExtra: " + ds + "; " + action + "; " + name + "; " + miniOpt);  
    if ($scope.data['req'][ds]['action'][action] != undefined && (name in $scope.data['req'][ds]['action'][action])){
      delete $scope.data['req'][ds]['action'][action][name];
    }
    if ($scope.allOpt[ds][action][name] != undefined && (name in $scope.allOpt[ds][action])){
      delete $scope.allOpt[ds][action][name];
    } 
  };

  $scope.removeDefExtra = function(ds, action, name)
  {        
    for (dataset in $scope.allOpt){
      if (dataset != 'Default'){
        if ($scope.data['req'][dataset]['action'][action] != undefined && (name in $scope.data['req'][dataset]['action'][action])){
          delete $scope.data['req'][dataset]['action'][action][name];
        }
      }else{
        if ($scope.defCon[action] != undefined && (name in $scope.defCon[action])){
          delete $scope.defCon[action][name];
        }
      }
      if ($scope.allOpt[dataset][action][name] != undefined && (name in $scope.allOpt[dataset][action])){
        delete $scope.allOpt[dataset][action][name];
      }
    }
  };

  $scope.makeInput = function()
  {
    $http({method: 'POST', url:'get_data', data: {'campaign1': $scope.data, 'drive' : $scope.drive}}).success(function(data, status){
      console.log(data, "success" + status);
    }).error(function(status){
      console.log("error:" + status);
    }); 
  };


  $scope.fillDefault = function()
  {
    $scope.alca = {
                  "ExpressCosmics" : "SiStripCalZeroBias+TkAlCosmics0T",
                    "StreamExpress"  : "SiStripCalZeroBias+TkAlMinBias+MuAlCalIsolatedMu+DtCalib",
                    "MinimumBias"    : "SiStripCalMinBias+TkAlMinBias",
                    "Commissioning"  : "HcalCalIsoTrk",
                    "SingleMu"       : "MuAlCalIsolatedMu+MuAlOverlaps+TkAlMuonIsolated+DtCalib",
                    "DoubleMu"       : "MuAlCalIsolatedMu+MuAlOverlaps+DtCalib+TkAlZMuMu",
                    "MuOnia"         : "TkAlJpsiMuMu+TkAlUpsilonMuMu",
                    "SingleElectron" : "EcalCalElectron",
                    "DoubleElectron" : "EcalCalElectron",
                    "AlCaLumiPixels" : "LumiPixels",
                    "DoubleMuParked" : "MuAlCalIsolatedMu+MuAlOverlaps+DtCalib+TkAlZMuMu",
                    "MuOniaParked"   : "TkAlJpsiMuMu+TkAlUpsilonMuMu",
                    "Cosmics"        : "TkAlCosmics0T+MuAlGlobalCosmics+HcalCalHOCosmics+DtCalibCosmics",
                    "AlCaP0"         : "",
                    "HcalNZS"        : "HcalCalMinBias"
                  }

    $scope.skim = {
                  "MinBias":"MuonTrack+BeamBkg+ValSkim+LogError+HSCPSD",
                  "ZeroBias":"LogError",
                  "Commissioning":"DT+LogError",
                  "Cosmics":"CosmicSP+CosmicTP+LogError",
                  "Mu" : "WMu+ZMu+HighMET+LogError",    
                  "EG":"WElectron+ZElectron+HighMET+LogError",
                  "Electron":"WElectron+ZElectron+HighMET+LogError",
                  "Photon":"WElectron+ZElectron+HighMET+LogError+DiPhoton+EXOHPTE",
                  "JetMETTau":"LogError+Tau",
                  "JetMET":"HighMET+LogError",
                  "BTau":"LogError+Tau",
                  "Jet":"HighMET+LogError",
                  "METFwd":"HighMET+LogError",
                  "SingleMu" : "WMu+ZMu+HighMET+LogError+HWW+HZZ+DiTau+EXOHSCP",
                  "DoubleMu" : "WMu+ZMu+HighMET+LogError+HWW+HZZ+EXOHSCP",
                  "SingleElectron" : "WElectron+HighMET+LogError+HWW+HZZ+Tau",
                  "DoubleElectron" : "ZElectron+LogError+HWW+HZZ",
                  "MuEG" : "LogError+HWW+HZZ",
                  "METBTag": "HighMET+LogError+EXOHSCP",
                  "BTag": "LogError+EXOHSCP",
                  "MET": "HighMET+LogError+EXOHSCP",

                  "HT": "HighMET+LogError",

                  "Tau": "LogError",
                  "PhotonHad": "LogError",
                  "MuHad": "LogError",
                  "MultiJet": "LogError",
                  "MuOnia": "LogError",
                  "ElectronHad": "LogError",
                  "TauPlusX": "LogError"
              }

    for (action in $scope.checkAll){
      $scope.checkAll[action] = true;
      if (action == 'reco'){
        $scope.allOpt['Default'][action] = JSON.parse(JSON.stringify($scope.defOpt[action]));
        $scope.defCon[action] = {};
        $scope.defCon[action]['steps'] = "RAW2DIGI,L1Reco,RECO,ALCA:,USER:EventFilter/HcalRawToDigi/hcallaserhbhehffilter2012_cff.hcallLaser2012Filter";
        $scope.defCon[action]['conditions'] = $scope.data['GT'];
        $scope.addDefExtra('Default', 'reco', 'data');
        $scope.defCon[action]['data'] = 'true';
        $scope.addDefExtra('Default', 'reco', 'eventcontent');
        $scope.defCon[action]['eventcontent'] = 'RECO';
        $scope.addDefExtra('Default', 'reco', 'datatier');
        $scope.defCon[action]['datatier'] = 'RECO';
        $scope.addDefExtra('Default', 'reco', 'customise');
        $scope.defCon[action]['customise'] = 'Configuration/DataProcessing/RecoTLR.customisePrompt';
      }

      if (action == 'skim'){
        $scope.allOpt['Default'][action] = JSON.parse(JSON.stringify($scope.defOpt[action]));
        $scope.defCon[action] = {};
        $scope.defCon[action]['steps'] = "SKIM:";
        $scope.defCon[action]['conditions'] = $scope.data['GT'];
        $scope.removeDefExtra('Default', 'skim', 'skimoption');
      }

      if (action == 'mini'){
        $scope.allOpt['Default'][action] = JSON.parse(JSON.stringify($scope.defOpt[action]));
        $scope.defCon[action] = {};
        $scope.defCon[action]['steps'] = "PAT";
        $scope.defCon[action]['conditions'] = "auto:run1_data_Fake";
        $scope.addDefExtra('Default', 'mini', 'n');
        $scope.defCon[action]['n'] = "2";
        $scope.addDefExtra('Default', 'mini', 'data');
        $scope.defCon[action]['data'] = "true";
        $scope.addDefExtra('Default', 'mini', 'eventcontent');
        $scope.defCon[action]['eventcontent'] = "MINIAOD";
        $scope.addDefExtra('Default', 'mini', 'runUnscheduled');
        $scope.defCon[action]['runUnscheduled'] = "true";
        $scope.addDefExtra('Default', 'mini', 'filein');
        $scope.defCon[action]['filein'] = "file:reco.root";
        $scope.addDefExtra('Default', 'mini', 'datatier');
        $scope.defCon[action]['datatier'] = "MINIAOD";
      }

    }



  };

  $scope.checkSkim = function(ds)
  {
      if ($scope.skim[ds.split("/")[1]] == undefined && $scope.check[ds].skim == true){
        $scope.check[ds].skim = false;
        if ('skim' in $scope.data['req'][ds]['action']){
          delete $scope.data['req'][ds]['action']['skim'];
        }
      }

      console.log($scope.checkAll['skim'] == true);
      console.log($scope.skim[ds.split("/")[1]] != undefined);

      if ($scope.checkAll['skim'] == true && $scope.skim[ds.split("/")[1]] != undefined){
        $scope.check[ds].skim = true;
      }    
  };

  $scope.checkAlca = function(ds)
  {
    if ($scope.defCon['reco'] != undefined){
      var test = "";
      for (name in $scope.alca){
        test += "(" + name + ")" + "|";
      }
      test = new RegExp(test);

      if (/ALCA:/.test($scope.defCon['reco']['steps']) && $scope.alca[ds.split("/")[1]] == undefined){
        str = $scope.data['req'][ds]['action']['reco']['steps'].split('ALCA:');
        $scope.data['req'][ds]['action']['reco']['steps'] = "";
        if(str[0] != undefined){
          $scope.data['req'][ds]['action']['reco']['steps'] += str[0];
        }
        if (str[1] != undefined){
          $scope.data['req'][ds]['action']['reco']['steps'] += str[1];
        }
      }
    }
  };

  $scope.formDriver = function(ds, action)
  {
    var isDefault = ((ds == 'Default') ? true : false);
    console.log("formDriver: " + ds + "; " + action + "; ");
    console.log($scope.alca);

    if (isDefault && $scope.drive[ds] == undefined){
        $scope.drive[ds] = {};
    }

    if (!isDefault){
      if ($scope.data['req'][ds]['action'][action] != undefined) {
        var temp = JSON.parse(JSON.stringify($scope.data['req'][ds]['action'][action]));
      } else {
        var temp = {};
      }
    } else{
      if ($scope.defCon[action] != undefined){
        var temp = JSON.parse(JSON.stringify($scope.defCon[action]));
      }else {
        var temp = {};
      }
    }

    if (action == 'reco'){
        $scope.drive[ds][action] = "";
        $scope.drive[ds][action] = "cmsDriver.py reco";
        
      if (!isDefault){
        var test = "";
        for (name in $scope.alca){
          test += "(" + name + ")" + "|";
        }
        test = new RegExp(test);
        if (/ALCA:/.test($scope.defCon['reco']['steps']) && $scope.alca[ds.split("/")[1]] != undefined){
          str = $scope.data['req'][ds]['action'][action]['steps'].split('ALCA:');
          $scope.data['req'][ds]['action'][action]['steps'] = "";
          temp['steps'] = "";

          if (str[0] != undefined){
            $scope.data['req'][ds]['action'][action]['steps'] += str[0];
            temp['steps'] += str[0];
          }

          $scope.data['req'][ds]['action'][action]['steps'] += "ALCA:";
          temp['steps'] += "ALCA:";
          temp['steps'] += $scope.alca[ds.split("/")[1]];

          if (str[1] != undefined){
            $scope.data['req'][ds]['action'][action]['steps'] += str[1];
            temp['steps'] += str[1];
          }
        }
      }
        $scope.drive[ds][action] += temp['steps'] ? " -s " + (temp['steps'] || "") : "";
        delete temp['steps'];
        //$scope.drive[ds][action] += temp['data'] ? " --data " + (temp['data'] || "") : "";
        //delete temp['data'];
        $scope.drive[ds][action] += temp['conditions'] ? " --conditions " + (temp['conditions'] || "") : "";
        delete temp['conditions'];
        $scope.drive[ds][action] += temp['eventcontent'] ? " --eventcontent " + (temp['eventcontent'] || "") : "";
        delete temp['eventcontent'];        
        $scope.drive[ds][action] += temp['datatier'] ? " --datatier " + (temp['datatier'] || "") : "";
        delete temp['datatier'];
        $scope.drive[ds][action] += temp['customise'] ? " --customise " + (temp['customise'] || "") : "";
        delete temp['customise'];
        $scope.drive[ds][action] += temp['scenario'] ? " --scenario " + (temp['scenario'] || "") : "";
        delete temp['scenario'];
        $scope.drive[ds][action] += " --no_exec";
        $scope.drive[ds][action] += " --python";
        $scope.drive[ds][action] += " reco_" + $scope.data['era'] + "_" + ds.split("/")[1] + ".py";
        $scope.drive[ds][action] += " --fileout";
        $scope.drive[ds][action] += " reco_" + $scope.data['era'] + "_" + ds.split("/")[1] + ".root";
    }

    if (action == 'skim'){

      if (!isDefault){
        var test = "";
        for (name in $scope.skim){
          test += "(" + name + ")" + "|";
        }
        test = new RegExp(test);
        if (/SKIM:/.test($scope.defCon['skim']['steps']) && $scope.skim[ds.split("/")[1]] != undefined){
          str = $scope.data['req'][ds]['action'][action]['steps'].split('SKIM:');
          $scope.data['req'][ds]['action'][action]['steps'] = "";
          temp['steps'] = "";

          if (str[0] != undefined){
            $scope.data['req'][ds]['action'][action]['steps'] += str[0];
            temp['steps'] += str[0];
          }

          $scope.data['req'][ds]['action'][action]['steps'] += "SKIM:";
          temp['steps'] += "SKIM:";
          temp['steps'] += $scope.skim[ds.split("/")[1]];

          if (str[1] != undefined){
            $scope.data['req'][ds]['action'][action]['steps'] += str[1];
            temp['steps'] += str[1];
          }
        }
      }

        $scope.drive[ds][action] = "";
        $scope.drive[ds][action] = "cmsDriver.py skim";
        $scope.drive[ds][action] += temp['steps'] ? " -s " + (temp['steps'] || "") : "";
        delete temp['steps'];     
        $scope.drive[ds][action] += temp['conditions'] ? " --conditions " + (temp['conditions'] || " ") : "";
        delete temp['conditions'];
        $scope.drive[ds][action] += temp['skimoption'] ? " --skimoption " + (temp['skimoption'] || " ") : "";
        delete temp['skimoption'];
        $scope.drive[ds][action] += " --no_exec";
        $scope.drive[ds][action] += " --python_filename";
        $scope.drive[ds][action] += " skim_" + $scope.data['era'] + "_" + ds.split("/")[1] + ".py";
     }     

    if (action == 'mini'){
        $scope.drive[ds][action]= "cmsDriver.py mini ";
        $scope.drive[ds][action] += temp['steps'] ? "-s " + (temp['steps'] || " ") : "";
        delete temp['steps'];
        $scope.drive[ds][action] += temp['n'] ? " -n " + (temp['n'] || " ") : "";
        delete temp['n'];
        $scope.drive[ds][action] += " --no_exec";
        $scope.drive[ds][action] += " --python_filename";
        $scope.drive[ds][action] += " mini_" + $scope.data['era'] + "_" + ds.split("/")[1] + ".py";
        $scope.drive[ds][action] += " --filein";
        $scope.drive[ds][action] += " reco_" + $scope.data['era'] + "_" + ds.split("/")[1] + ".root";   
    }

   
    for (key in temp){
      $scope.drive[ds][action] += " --" + key + " ";
      if (temp[key] == 'true'){
        $scope.drive[ds][action] += "";
      } else {
        $scope.drive[ds][action] += temp[key];
      }
    }
     
  };

  $scope.$watch('checkAll', function(newValue, oldValue) {

    for (action in newValue){

      //true to false
      if (oldValue[action] == true && newValue[action] == false){
        for (dataset in $scope.data['req']){
          delete $scope.data['req'][dataset]['action'][action];
          $scope.allOpt[dataset][action] = false;
          $scope.check[dataset][action] = false;
        }
        delete $scope.defCon[action];
      }

      //false to true
      if (oldValue[action] == false && newValue[action] == true){

        if ($scope.allOpt['Default'][action] == undefined){
          $scope.allOpt['Default'][action] = JSON.parse(JSON.stringify($scope.defOpt[action]));
        }        

        for (dataset in $scope.data['req']){
          $scope.data['req'][dataset]['action'][action] = {};
          $scope.allOpt[dataset][action] = JSON.parse(JSON.stringify($scope.defOpt[action]));
          $scope.check[dataset][action] = true;

          if ($scope.drive[dataset] == undefined){
            $scope.drive[dataset] = {};
          }
          if ($scope.drive[dataset][action] == undefined){
            $scope.drive[dataset][action]= {};
          }
          if (action == 'skim'){
            $scope.checkSkim(dataset);
          }
        }
        $scope.formDriver('Default', action);
        
      }
      
    }
   },true);

  $scope.$watch('check', function(newValue, oldValue) {

    console.log("watch check");
    //delete if false
    for (var key in newValue){
      if (oldValue[key] == undefined){
        break;
      }

      //for (action in $scope.actionDict){
      for (action in $scope.checkAll){
        //if action turns to false
        if (oldValue[key][action] == true && newValue[key][action] == false){
          delete $scope.data['req'][key]['action'][action];
        }
        //if action turns true
        if (oldValue[key][action] == false && newValue[key][action] == true){
          if ($scope.data['req'][key]['action'][action] == undefined){
            $scope.data['req'][key]['action'][action] = {};
          }
          $scope.data['req'][key]['action'][action] = $scope.defCon[action];

          if ($scope.allOpt[key][action] == undefined){
            $scope.allOpt[key][action] = JSON.parse(JSON.stringify($scope.defOpt[action]));
          }
          if ($scope.drive[key] == undefined){
            $scope.drive[key] = {};
          }
          if ($scope.drive[key][action] == undefined){
            $scope.drive[key][action] = {};
          }
          $scope.formDriver(ds, action);
        }
      }
    }
   },true);

  $scope.$watch("data['req']", function(newValue, oldValue) {

    for (ds in newValue){
      if (oldValue[ds] == undefined || newValue[ds] != oldValue[ds]){
        for (action in newValue[ds]['action']){
          if (oldValue[ds] == undefined || oldValue[ds]['action'][action] == undefined || newValue[ds]['action'][action]!=oldValue[ds]['action'][action]){
           
            $scope.formDriver(ds, action);
          }
        }
      }
    }
   },true);

  $scope.$watch("skim", function(newValue, oldValue) {
    console.log("watch skim");
    //$scope.checkSkim();
    for (ds in $scope.data['req']){
      //for (action in $scope.data['req'][ds]['action']){
      $scope.checkSkim(ds);
      $scope.formDriver(ds, 'skim');
      //}
    }
  },true);

  $scope.$watch("alca", function(newValue, oldValue) {
    for (ds in $scope.data['req']){
      for (action in $scope.data['req'][ds]['action']){
        console.log("alca" + ds + " " + action);
        $scope.checkAlca(ds);
        $scope.formDriver(ds, action);
      }
    }
  },true);

  $scope.$watch("defCon", function(newValue, oldValue) {
    for (action in newValue){
      if (oldValue[action] == undefined || newValue[action] != oldValue[action]){

        for (field in newValue[action]){
          if (oldValue[action] == undefined || oldValue[action][field] == undefined || newValue[action][field]!=oldValue[action][field]){
            for (ds in $scope.allOpt){
              if (ds != 'Default'){
                if ($scope.data['req'][ds]['action'][action] == undefined){
                  $scope.data['req'][ds]['action'][action] = {};
                }
                if ($scope.allOpt[ds][action][field] != undefined){
                  $scope.data['req'][ds]['action'][action][field] = newValue[action][field];
                }
                
                if (action == 'reco'){
                  $scope.checkAlca(ds);
                }
              }
      
            }            
          }
        }         
      }
      $scope.formDriver('Default', action);
    }
   },true);

});


myApp.directive("inlineEditable", function () {
    return {
        require: 'ngModel',
        scope: {},
        templateUrl: "static/temp.textarea.html",
        link: function (scope, element, attr, ctrl) {
            ctrl.$render = function () {
                scope.json_value = JSON.stringify(ctrl.$viewValue, null, 4);
            };
            scope.update = function () {
                var object = null;
                try {
                    object = JSON.parse(scope.json_value);
                    ctrl.$setViewValue(object);
                    ctrl.$setValidity("bad_json", true);
                } catch (err) {
                    ctrl.$setValidity("bad_json", false);
                }
            };
        }
    }
});




