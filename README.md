# Tableau Refresh Extracts

A script to refresh all extracts programatically.

## Prereqs

Run

`pip install tableauserverclient`

Make a [Personal Access Token on Tableau](https://help.tableau.com/current/server/en-us/security_personal_access_tokens.htm#create-personal-access-tokens) and create a `.env` file, with the following configurations:

```
TOKEN_NAME="<token_name>"
TOKEN_VALUE="<token_value>"
SITENAME="sonarsource"
SERVER_URL="dub01.online.tableau.com"
```

## How to run

Run

`bash refresh_all_extracts.sh`

This will run two different python scripts in order: 1. `get_jobs.py` 2. `refresh_all_extracts.py`.

`get_jobs.py` will get a list of all the jobs run in the last 2 days and save it to `data.json`. From there `refresh_all_extracts.py` will get all the data sources that have extracts from `data.json` and run their respective extract job.