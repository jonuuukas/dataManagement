var myApp = angular.module('myApp', ['ui.bootstrap']);
myApp.controller('myAppCtrl', function ($scope, $http, $location) {
  $scope.data = {"CMSSW":"CMSSW_7_4_0_pre6", "GT": "GT_FAKE", "era":"2012A", "prio": 7, "req":{}};
  $scope.check = {};
  $scope.actionDict = {"reco":"RECO", "skim":"Skim", "mini":"MiniAOD"};
  $scope.allOpt = {};
  $scope.recoOpt = {
                    "recoReco": "reco", 
                    "recoAlca" : "alca", 
                    "recoDqm" : "dqm", 
                    "recoCond": "conditions", 
                    "recoOut": "out", 
                    "recoScen": "scenario"
                  };
  $scope.skimOpt = {
                  "skimCond": "conditions", 
                  "skimOpt": "skimoption"
                  };
  $scope.miniOpt = {
                  "miniRecoSteps": "stepsReco", 
                  "miniAODSteps": "stepsMini"
                  };

  $scope.defOpt = {"reco" : $scope.recoOpt, "skim" : $scope.skimOpt, "mini" : $scope.miniOpt};

  $scope.addReq = function(name)
  {   
    if (!(name in $scope.data['req'])){
      name = name || "NewDataSet";
      $scope.data['req'][name] = {"id": name, "skim": "", "filter": true, "action": {}};
    }else{
      alert("Dataset name already exists");
    }
  };

  $scope.addExtra = function(ds, action, name)
  {   
    if (name == undefined){
      alert("No extra name");
    } else{
        $scope.allOpt[ds][action][name] = name;
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
    if ($scope.data['req'][ds]['action'][action] != undefined && (name in $scope.data['req'][ds]['action'][$scope.actionDict[action]])){
      delete $scope.data['req'][ds]['action'][$scope.actionDict[action]][name];
    }
    if ($scope.allOpt[ds][action][name] != undefined && (name in $scope.allOpt[ds][action])){
      delete $scope.allOpt[ds][action][name];
    }
  };

  $scope.makeInput = function()
  {
    $http({method: 'POST', url:'get_data', data: {'campaign1': $scope.data}}).success(function(data, status){
      console.log(data, "success" + status);
    }).error(function(status){
      console.log("error:" + status);
    }); 
  };
  
  $scope.$watch('check', function(newValue, oldValue) {
    //delete if false
    for (var key in newValue){      
      for (action in $scope.actionDict){
        //if action turns to false
        if (oldValue[key] != undefined && oldValue[key][action] != undefined && newValue[key][action] == false){
          delete $scope.check[key][action];
          delete $scope.data['req'][key]['action'][$scope.actionDict[action]];
          delete $scope.allOpt[key][action];
        }
        //if action turns true
        if ((oldValue[key] == undefined || oldValue[key][action] == undefined) && newValue[key][action] == true){
          
          if ($scope.allOpt[key] == undefined){
            $scope.allOpt[key] = {};
          } 

          if ($scope.data['req'][key]['action'][$scope.actionDict[action]] == undefined){
            $scope.data['req'][key]['action'][$scope.actionDict[action]] = {};
          }
          
          if ($scope.allOpt[key][action] == undefined){
            $scope.allOpt[key][action] = JSON.parse(JSON.stringify($scope.defOpt[action]));
            console.log("allOpt: " + JSON.stringify($scope.allOpt));
          }
        }
      }
    }
   },true);

});


myApp.directive("inlineEditable", function () {
    return {
        require: 'ngModel',
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
                console.log(scope.json_value)
            };
        }
    }
});




