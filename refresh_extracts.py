import json
import tableauserverclient as TSC
import os

token_name = os.environ.get("TOKEN_NAME")
token_value = os.environ.get("TOKEN_VALUE")
site_name = os.environ.get("SITENAME")
server_url = "https://" + os.environ.get("SERVER_URL")

tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_name)
server = TSC.Server(server_url)
server.version = '2.8'
server.add_http_options({'verify': False})
server.auth.sign_in(tableau_auth)

data_source_ids = set()
with open('jobs_data.json', 'r') as f:
    data = json.load(f)
    for job in data:
        if job['datasource_rest_id']:
            data_source_ids.add(job['datasource_rest_id'])

new_job_ids = []
for id in data_source_ids:
    try:
        ds = server.datasources.get_by_id(id)
        print(f"Refreshing {ds.name} in project {ds.project_name}")
        job = server.datasources.refresh(ds)
        new_job_ids.append(job.id)
    except:
        print(id, 'failed')
    
print(new_job_ids)