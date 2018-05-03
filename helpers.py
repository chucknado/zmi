import os
import json
import time
import configparser
from urllib.parse import urlparse

import requests
from auth import get_auth


# ----- Functions ----- #

def get_settings():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    default = config['DEFAULT']
    settings = {'src_root': 'https://{}.zendesk.com/api/v2/help_center'.format(default['src_kb']),
                'dst_root': 'https://{}.zendesk.com/api/v2/help_center'.format(default['dst_kb']),
                'locale': default['locale'],
                'src_archive': default['src_archive'],
                'team_user': default['team_user']}
    return settings


def read_data(file_name):
    """
    Reads a .json file and converts it to a Python data structure
    :param file_name: File in the data folder. Omit the .json extension. One of "articles", "sections",
     "comments", "subscriptions", "votes"
    :return: Python data structure
    """
    file_path = os.path.join('data', f'{file_name}.json')
    if os.path.isfile(file_path) is False:
        print(f'File does not exist: {file_name}')
        exit()
    with open(file_path, mode='r') as f:
        data = json.load(f)
    return data


def write_data(data, resources):
    """
    Writes a Python data structure to a .json file
    :param data: A Python data structure
    :param resources: One of "articles", "sections", "comments", "subs", etc
    :return: None
    """
    file_path = os.path.join('data', f'{resources}.json')
    with open(file_path, mode='w') as f:
        json.dump(data, f, sort_keys=True, indent=2)


def package_article(article, put=False):
    """
    Creates the payload for a PUT or POST article request.
    :param article: Complete article dict from API
    :param put: Whether the payload is for a PUT request. Defaults to POST request
    :return: Abridged article dict
    """
    if put:
        package = {
            'title': article['title'],
            'body': article['body'],
            'draft': article['draft'],
        }
        return {'translation': package}
    else:
        package = {
            'title': article['title'],
            'author_id': article['author_id'],
            'body': article['body'],
            'comments_disabled': article['comments_disabled'],
            'label_names': article['label_names'],
            'draft': article['draft'],
            'promoted': article['promoted'],
            'position': article['position']
        }
        return {'article': package}


def package_comment(comment, put=False):
    """
    Creates the payload for a PUT or POST comment request.
    :param comment: Complete comment dict from API
    :param put: Whether the payload is for a PUT request. Defaults to POST request
    :return: Abridged comment dict
    """
    if put:
        package = {
            'body': comment['body']
        }
    else:
        package = {
            'author_id': comment['author_id'],
            'body': comment['body'],
            'locale': comment['locale'],
            'created_at': comment['created_at']
        }
    return {'comment': package, 'notify_subscribers': False}


def verify_author(author_id, team_author_id):
    """
    Checks to see if article's author is an end user, who can't publish to HC. If yes, replace with the generic
    Zendesk team user set in settings.ini.
    :param author_id: The author's id
    :param team_author_id: The user id of a generic agent in Zendesk
    :return: The id of an author who is not an end user
    """
    url = 'https://support.zendesk.com/api/v2/users/{}.json'.format(author_id)
    user = get_resource(url)
    role = user['role']
    if role == 'end-user':
        return int(team_author_id)
    else:
        return author_id


def write_js_redirects(article_map):
    """
    The js_redirects.txt file is used in the script.js file for article redirects after migrating
    :param article_map: Dict of old:new article ids
    :return: None
    """
    file_path = os.path.join('data', 'js_redirects.txt')
    counter = 1
    with open(file_path, mode='w') as f:
        for article in article_map:
            if counter == len(article_map):
                f.write('    {}:{}\n'.format(article, article_map[article]))
            else:
                f.write('    {}:{},\n'.format(article, article_map[article]))

    return None


def get_resource_list(url):
    """
    Returns a list of HC resources specified by the url basename (such as .../articles.json)
    :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles.json'
    :return: List of resources
    """
    session = requests.Session()
    session.auth = get_auth()

    o = urlparse(url)
    resource = os.path.splitext(os.path.basename(o.path))[0]    # e.g., 'articles'
    record_list = {resource: []}
    while url:
        response = session.get(url)
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            response = session.get(url)
        if response.status_code != 200:
            print('Error with status code {}'.format(response.status_code))
            exit()
        data = response.json()
        if data[resource]:  # guard against empty record list
            record_list[resource].extend(data[resource])
        url = data['next_page']
    return record_list[resource]


def get_resource(url):
    """
    Returns a single HC resource
    :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles/2342572.json'
    :return: Dict of a resource
    """
    resource = None
    response = requests.get(url, auth=get_auth())
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.get(url, auth=get_auth())
    if response.status_code != 200:
        print('Failed to get record with error {}:'.format(response.status_code))
        print(response.text)
        exit()
    for k, v in response.json().items():
        resource = v
    if type(resource) is dict:
        return resource
    return None


def post_resource(url, data, status=201):
    """
    :param url:
    :param data:
    :param status: HTTP status. Normally 201 but some POST requests return 200
    :return:
    """
    resource = None
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.post(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code != status:
        print('Failed to create record with error {}:'.format(response.status_code))
        print(response.text)
        exit()
    for k, v in response.json().items():
        resource = v
    if type(resource) is dict:
        return resource
    return None


def put_resource(url, data):
    """
    :param url:
    :param data:
    :return:
    """
    resource = None
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.post(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code != 200:
        print('Failed to update record with error {}:'.format(response.status_code))
        print(response.text)
        exit()
    for k, v in response.json().items():
        resource = v
    if type(resource) is dict:
        return resource
    return None


def delete_resource(url):
    """
    Runs a DELETE request on any Delete endpoint in the Zendesk API
    :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles/2342572.json'
    :return: If successful, a 204 status code. If not, None
    """
    response = requests.delete(url, auth=get_auth())
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.delete(url, auth=get_auth())
    if response.status_code != 204:
        print('Failed to delete record with error {}'.format(response.status_code))
        print(response.text)
        exit()
    return None
