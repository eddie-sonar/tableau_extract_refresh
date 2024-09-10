import requests
import xml.etree.ElementTree as ET
import os
import json
import math
from datetime import date, timedelta
import time

class ApiCallError(Exception):
    pass

def _check_status(server_response, success_code):
    """
    Checks the server response for possible errors.
    'server_response'       the response received from the server
    'success_code'          the expected success code for the response
    Throws an ApiCallError exception if the API call fails.
    """
    if server_response.status_code != success_code:
        parsed_response = ET.fromstring(server_response.text)

        # Obtain the 3 xml tags from the response: error, summary, and detail tags
        error_element = parsed_response.find('t:error', namespaces=xmlns)
        summary_element = parsed_response.find('.//t:summary', namespaces=xmlns)
        detail_element = parsed_response.find('.//t:detail', namespaces=xmlns)

        # Retrieve the error code, summary, and detail if the response contains them
        code = error_element.get('code', 'unknown') if error_element is not None else 'unknown code'
        summary = summary_element.text if summary_element is not None else 'unknown summary'
        detail = detail_element.text if detail_element is not None else 'unknown detail'
        error_message = '{0}: {1} - {2}'.format(code, summary, detail)
        raise ApiCallError(error_message)

def _encode_for_display(text):
    """
    Encodes strings so they can display as ASCII in a Windows terminal window.
    This function also encodes strings for processing by xml.etree.ElementTree functions.
    Returns an ASCII-encoded version of the text.
    Unicode characters are converted to ASCII placeholders (for example, "?").
    """
    return text.encode('ascii', errors="backslashreplace").decode('utf-8')

def sign_in(server, personalAccessTokenName, personalAccessTokenSecret, site=""):
    """
    Signs in to the server specified with the given credentials
    'server'   specified server address
    'personalAccessTokenName' is the name (not ID) of the user to sign in as.
               Note that most of the functions in this example require that the user
               have server administrator permissions.
    'personalAccessTokenSecret' is the personalAccessTokenSecret for the user.
    'site'     is the ID (as a string) of the site on the server to sign in to. The
               default is "", which signs in to the default site.
    Returns the authentication token and the site ID.
    """
    url = "https://" + server + "/api/{0}/auth/signin".format(VERSION)

    # Builds the request
    xml_request = ET.Element('tsRequest')
    credentials_element = ET.SubElement(xml_request, 'credentials', personalAccessTokenName=personalAccessTokenName, personalAccessTokenSecret=personalAccessTokenSecret)
    ET.SubElement(credentials_element, 'site', contentUrl=site)
    xml_request = ET.tostring(xml_request)

    # Make the request to server
    server_response = requests.post(url, data=xml_request, verify=False)
    _check_status(server_response, 200)

    # ASCII encode server response to enable displaying to console
    server_response = _encode_for_display(server_response.text)

    # Reads and parses the response
    parsed_response = ET.fromstring(server_response)

    # Gets the auth token and site ID
    token = parsed_response.find('t:credentials', namespaces=xmlns).get('token')
    site_id = parsed_response.find('.//t:site', namespaces=xmlns).get('id')
    user_id = parsed_response.find('.//t:user', namespaces=xmlns).get('id')
    return token, site_id, user_id


def sign_out(server, auth_token):
    """
    Destroys the active session and invalidates authentication token.
    'server'        specified server address
    'auth_token'    authentication token that grants user access to API calls
    """
    url = "https://" + server + "/api/{0}/auth/signout".format(VERSION)
    server_response = requests.post(url, headers={'x-tableau-auth': auth_token}, verify=False)
    _check_status(server_response, 204)
    print("hi") 

def get_jobs(server, auth_token, site_id, date=None):
    """
    Returns the json of all the jobs that have happend since date
    'server'        specified server address
    'auth_token'    authentication token that grants user access to API calls
    'site_id'       ID of the site that the user is signed into
    'date'          Will pull all jobs if left None, otherwise pulls jobs that are >= the date
    """
    page_num, page_size = 1, 100   # Default paginating values

    # Builds the request
    url = "https://" + server + "/api/{0}/sites/{1}/jobs?filter=jobType:eq:refresh_extracts".format(VERSION, site_id)
    if date is not None:
        url = url + ",createdAt:gte:{0}T00:00:00z".format(date)
    paged_url = url + "&pageSize={0}&pageNumber={1}".format(page_size, page_num)
    print(paged_url)
    server_response = requests.get(paged_url, headers={'x-tableau-auth': auth_token}, verify=False)
    _check_status(server_response, 200)
    xml_response = ET.fromstring(_encode_for_display(server_response.text))

    # Used to determine if more requests are required to find all jobs on server
    total_jobs = int(xml_response.find('t:pagination', namespaces=xmlns).get('totalAvailable'))
    max_page = int(math.ceil(total_jobs / page_size))

    print("Total Jobs:", total_jobs)
    print("Max Pages:", max_page)

    jobs = xml_response.findall('.//t:backgroundJob', namespaces=xmlns)

    # Continue querying if more jobs exist on the server
    for page in range(2, max_page + 1):
        print("Page:", page)
        paged_url = url + "&pageSize={0}&pageNumber={1}".format(page_size, page)
        server_response = requests.get(paged_url, headers={'x-tableau-auth': auth_token}, verify=False)
        _check_status(server_response, 200)
        xml_response = ET.fromstring(_encode_for_display(server_response.text))
        jobs.extend(xml_response.findall('.//t:backgroundJob', namespaces=xmlns))

    # Look through all jobs to find the 'default' one
    jobs_json = []
    for job in jobs:
        job_json = {}
        job_id = job.get('id')
        datasource_id, workbook_id, notes = get_datasource_by_job_id(server, auth_token, site_id, job_id)

        job_json['job_rest_id'] = job_id
        job_json['status'] = job.get('status')
        job_json['created_at'] = job.get('createdAt')
        job_json['started_at'] = job.get('startedAt')
        job_json['ended_at'] = job.get('endedAt')
        job_json['priority'] = job.get('priority')
        job_json['job_type'] = job.get('jobType')
        job_json['datasource_rest_id'] = datasource_id
        job_json['workbook_rest_id'] = workbook_id
        job_json['notes'] = notes

        jobs_json.append(job_json)
    return jobs_json


def get_datasource_by_job_id(server, auth_token, site_id, job_id):
    """
    Gets the datasource/workbook/notes assosiated with the job_id.
    'server'        specified server address
    'auth_token'    authentication token that grants user access to API calls
    'user_id'       ID of user with access to job
    'site_id'       ID of the site that the user is signed into
    'job_id' name of job to get ID of
    Returns the datasource_id, workbook_id, notes for Job id.
    """
    url = "https://" + server + "/api/{0}/sites/{1}/jobs/{2}".format(VERSION, site_id, job_id)
    server_response = requests.get(url, headers={'x-tableau-auth': auth_token}, verify=False)
    _check_status(server_response, 200)
    xml_response = ET.fromstring(_encode_for_display(server_response.text))

    job = xml_response.find('.//t:job', namespaces=xmlns)
    datasource_id = None
    workbook_id = None
    notes = None
    if job is not None:
        refresh_job = job.find('.//t:extractRefreshJob', namespaces=xmlns)
        if refresh_job is not None:
            notes_job = job.find('.//t:notes', namespaces=xmlns)
            if notes_job is not None:
                notes = notes_job.text
            datasource = refresh_job.find('.//t:datasource', namespaces=xmlns)
            if datasource is not None:
                datasource_id = datasource.get('id')
            workbook = refresh_job.find('.//t:workbook', namespaces=xmlns)
            if workbook is not None:
                workbook_id = workbook.get('id')
            return datasource_id, workbook_id, notes
    error = "Datasource ID not found for Job ID '{0}'.".format(job_id)
    raise LookupError(error)

if __name__ == "__main__":

    # start timer
    tic = time.perf_counter()

    # setup variables
    today = date.today()
    days_ago = today - timedelta(days=2)
    print("Today's date:", today)

    xmlns = {'t': 'http://tableau.com/api'}
    VERSION = '3.8'
    server_url = os.environ.get("SERVER_URL")
    site_name = os.environ.get("SITENAME")
    personalAccessTokenName = os.environ.get('TOKEN_NAME')
    personalAccessTokenSecret = os.environ.get('TOKEN_VALUE')

    # sign into tableau rest api
    auth_token, site_id, user_id = sign_in(server_url, personalAccessTokenName, personalAccessTokenSecret, site_name)

    # get json file and format
    jobs_json = get_jobs(server_url, auth_token, site_id, days_ago)
    with open('data.json', 'w') as f:
        json.dump(jobs_json, f, indent=4)

    # sign out tableau rest api
    sign_out(server_url, auth_token)

    # job time print
    toc = time.perf_counter()
    print(f"Finished in {toc - tic:0.4f} seconds")