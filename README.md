## README 

__How to Run__
Initialize:
* pull down git repo
* create venv and install packages using requirements.txt
* add the correct username and password in `IncidentsPipeline.py`

Run background scheduled job:
* in a background process run the python file named `scheduler.py`

Run and query API (local only):
* open code editor to project home folder
* run command `python .\app\app.py` to run API (requires python 3)
* go to `http://0.0.0.0:9000` and then use the endpoint `\incidents`


__Approach__
With this take-home assignment, I took a very simple approach consisting of three separate scripts:
1. `IncidentsPipeline`: this is the core class that extracts the data for each incident type, processes the raw data, and ultimately saves a file title `historical incidents.json` which contains all incident data up until this point
2. `app.py`: a FastAPI endpoint, which reads in `historical incidents.json` and returns results to the end user
3. `scheduler.py`: a basic background job that runs `IncidentsPipeline` every 15 minutes and updates `historical incidents.json`

The high-level flow is that scheduler.py runs in the background and calls the incidents pipeline every 15 minutes. The incidents pipeline then pulls the raw data for each incident type, at which point, it loops through all raw incidents individually, processes the incident, and stores it.  The final result is then saved within the `\data` folder. The local API then leverages the saved data and provides data back to the user immediately 

__Improvements for production__
There are a number of changes I would make as this was done in ~2-3 hours.  Some high-level ideas would be the following:
* Each incident type appears to have a different schema, instead of handling these using if statements, I would pre-define these schemas and make the processing dynamic dependent on schema
* I recreate all of the data from scratch every run, however, in a real world situation, I would incrementally add only new data 
* For this very basic approach, I use a cron job, which saves a JSON file that is used by API. In reality, I would do something like the following (assumes batch data processing and not streaming, which would require a wholly different architecture).  The key goal is decoupling every stage as we might be pulling in raw data from dozens of different sources for a single client, 
  * Various Lambdas that pull the raw data and push directly to a database / data warehouse. 
    * Lambdas could be triggered every 15 minutes using AWS events scheduler (dependent on data source)
  * Once raw data is available in data warehouse, this kicks off a processing pipeline either using DBT or custom python code. 
    * Pipeline can be orchestrated utilizing Airflow
    * Pipeline takes raw data processes it and saves it in a set of processed tables in the data warehouse 
  * API would then pull directly from these processed tables
* Other smaller changes
  * Create a `models.py` file to define response structure for the API 
  * Improve exception handling
  * This uses an all or nothing approach with zero retries. If the pipeline fails then no data is captured.  In a real-world setting, this would made to be more fault-tolerant
  * Utilize a proper secrets manager and `config.py` to handle credentials and settings, respectively
  * Define inpute parameter and output types for functions
