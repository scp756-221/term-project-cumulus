"""
SFU CMPT 756
Loader for sample database
"""

# Standard library modules
import csv
import os
import time

# Installed packages
import requests

# The application

loader_token = os.getenv('SVC_LOADER_TOKEN')

# Enough time for Envoy proxy to initialize
# This is only needed if the loader is run with
# Istio injection.  `cluster/loader-tpl.yaml`
# sets that value.
INITIAL_WAIT_SEC = 1

db = {
    "name": "http://cmpt756db:30002/api/v1/datastore",
}


def build_auth():
    """Return a loader Authorization header in Basic format"""
    global loader_token
    return requests.auth.HTTPBasicAuth('svc-loader', loader_token)


def create_user(name, email, mobile, uuid):
    """
    Create a user.
    If a record already exists with the same fname, lname, and email,
    the old UUID is replaced with this one.
    """
    url = db['name'] + '/load'
    response = requests.post(
        url,
        auth=build_auth(),
        json={"objtype": "user",
              "name": name,
              "email": email,
              "mobile": mobile,
              "uuid": uuid})
    return (response.json())


def create_booklist(author, title, uuid):
    """
    Create a song.
    If a record already exists with the same author and title,
    the old UUID is replaced with this one.
    """
    url = db['name'] + '/load'
    response = requests.post(
        url,
        auth=build_auth(),
        json={"objtype": "Book",
              "Author": author,
              "BookTitle": title,
              "uuid": uuid})
    return (response.json())


def check_resp(resp, key):
    if 'http_status_code' in resp:
        return None
    else:
        return resp[key]


if __name__ == '__main__':
    # Give Istio proxy time to initialize
    time.sleep(INITIAL_WAIT_SEC)

    resource_dir = '/data'

    with open('{}/users/users.csv'.format(resource_dir), 'r') as inp:
        rdr = csv.reader(inp)
        next(rdr)  # Skip header
        for name, email, mobile, uuid in rdr:
            resp = create_user(name.strip(),
                               email.strip(),
                               mobile.strip(),
							   uuid.strip())
            resp = check_resp(resp, 'user_id')
            if resp is None or resp != uuid:
                print('Error creating user {} {} ({}), {}'.format(name,
                                                                  email,
                                                                  mobile,
                                                                  uuid))

    with open('{}/books/books.csv'.format(resource_dir), 'r') as inp:
        rdr = csv.reader(inp)
        next(rdr)  # Skip header
        for author, title, uuid in rdr:
            resp = create_booklist(author.strip(),
                               title.strip(),
                               uuid.strip())
            resp = check_resp(resp, 'book_id')
            if resp is None or resp != uuid:
                print('Error creating booklist {} {}, {}'.format(author,
                                                             title,
                                                             uuid))
