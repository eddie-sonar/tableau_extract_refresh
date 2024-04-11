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
