# Data management application
```json
{
  "/": "\n    Opening function that directs to index.html\n    ", 
  "/api/help": "Print available functions.", 
  "/get_alca_matrix_value": "\n    Downloads the autoAlca matrix from the Git repo and passes it to Angular controller which\n    updates the text field\n    ", 
  "/get_all_docs": "\n    Used in saveDocs() function to get all docs and later for the \n    object to be pushed in to the data list\n    ", 
  "/get_skim_matrix_value": "\n    Downloads the autoSkim matrix from the Git repo and passes it to Angular controller which\n    updates the text field\n    ", 
  "/load_data": "\n    Communicates with the CouchDB and returns the object\n    according to it's _id as a JSON\n    ", 
  "/save_doc": "\n    Puts a newly created object to the CouchDB\n    ", 
  "/submit_campaign": "\n    Executes the submit button by updating the current campaign, creating/executing the script in get_submit_bash()\n    Logs of the process can be found in the WORK_DIR variable location and a log is also uploaded to the CouchDB\n    together with the object\n    ", 
  "/test_campaign": "\n    Creates a bash script that will proceed with the config file generation and\n    will run the cmsRun command without injecting it to request manager.\n    Runs tests with all the datasets of the campaign and return jsons\n    should be processed by the dataset name in controllers.js\n    ", 
  "/update_file": "\n    Gets the object from the browser and updates it in the CouchDB\n    "
}
```
