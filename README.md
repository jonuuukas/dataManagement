# Data management application
```json
{
  "/": "\n    Opening function that directs to index.html\n    ", 
  "/api/help": "Print available functions.", 
  "/get_all_docs": "\n    Used in saveDocs() function to get all docs and later for the \n    object to be pushed in to the data list\n    ", 
  "/load_data": "\n    Communicates with the CouchDB and returns the object\n    according to it's _id as a JSON\n    ", 
  "/save_doc": "\n    Puts a newly created object to the CouchDB\n    ", 
  "/submit_campaign": "\n    Executes the submit button by updating the current campaign, creating/executing the script in get_bash()\n    Logs of the process can be found in the WORK_DIR variable location and a log is also uploaded to the CouchDB\n    together with the object\n    ", 
  "/update_file": "\n    Gets the object from the browser and updates it in the CouchDB\n    "
}
```
