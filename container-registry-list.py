import requests
import pprint
import re
import sys

#TODO:  Handle bearer and simple auth
#TODO:  Handle pagination details embedded in header['link'] to get full list
#   - described here:  https://docs.docker.com/registry/spec/api/
#   - example URL:  https://registry.suse.com/v2/_catalog?last=cap-beta%2Fscf-cc-clock&n=100

pp = pprint.PrettyPrinter(indent=4)

def get_token(base_url, scope):
    r = requests.get(base_url)

    auth_headers = r.headers.get(
        'www-authenticate', 'www-authenticate does not exist in header!')

    # print(re.match('bearerr', auth_headers, re.IGNORECASE))
    bearerauth_match = re.search('bearer', auth_headers, re.IGNORECASE)
    # basicauth_match = re.search('basic', auth_headers, re.IGNORECASE)
    # print(auth_headers)

    auth_type =''
    if bearerauth_match:
        # print('Found: ', bearerauth_match.group())
        auth_type = 'bearer'
    else:
        print('Did not find bearer auth path')
        # sys.exit(1)
        return

    split_auth_header = auth_headers.split(",")
    realm = split_auth_header[0].split(' ')[1].split(
        '=')[1].replace('\"', '').replace('\'', '').strip()
    service = split_auth_header[1].split('=')[1].replace(
        '\"', '').replace('\'', '').strip()
    # scope = "registry:catalog:*"
    # print(realm)

    params = {"service": service, "scope": scope}
    r2 = requests.get(realm, params=params)
    token = r2.json().get('token', None)
    # print(token)
    return token

def get_v2catalog(base_url, **kwargs):
    if ('n' in kwargs):
         params = {'n': kwargs['n']}
    else:
        params = {'n': 100}

    if base_url[-1] != "/":
        base_url += "/"
    catalog_url = base_url + "v2/_catalog"
    scope = 'registry:catalog:*'

    token = get_token(catalog_url, scope)
    if token:
        headers = {"Authorization": "Bearer " + token}
    else:
        headers = {}

    r1 = requests.get(catalog_url, params=params,headers=headers)
    header_link = r1.headers.get('link', None)
    if r1.ok:
        # pp.pprint(r.json())
        return dict(r1.json()).get('repositories')
    else:
        # print("Failed to access registry catalog")
        return None

def get_repo_tags(base_url, repo):
    if base_url[-1] != "/":
        base_url += "/"
    tags_list_url = base_url + "v2/" + repo + "/tags/list"
    # print("tags_list_url: " + tags_list_url)
    scope = 'repository:' + repo + ':pull'
    token = get_token(tags_list_url, scope)
    headers = {"Authorization": "Bearer " + token}
    r = requests.get(tags_list_url, headers=headers)
    if r.ok:
        # pp.pprint(r.json())
        return r.json()
    else:
        # print("Failed to access tag list for repo: " + repo)
        return None



base_url = 'https://registry.suse.com/'
# base_url = 'https://hub.docker.com/'
# catalog = get_v2catalog(base_url, n=10).get('repositories')
catalog = get_v2catalog(base_url, n=100)
pp.pprint(catalog)
# catalog_dict = dict.fromkeys(catalog, '')

# for entry in catalog:
#     print('.', end='')
#     temp = get_repo_tags(base_url, entry)
#     if temp:
#         catalog_dict[entry] = temp.get('tags', '')
# print()
# pp.pprint(catalog_dict)




# current_endpoint = ['https://registry.suse.com/v2/_catalog', 'registry:catalog:*']
# current_endpoint = ['https://registry.suse.com/v2/caasp/v4/velum/tags/list', 'repository:caasp/v4/velum:pull']
# current_endpoint = ['https://registry.suse.com/v2/caasp/v4/caasp-dex/tags/list', 'repository:caasp/v4/caasp-dex:pull']

# token1 = get_token(current_endpoint[0], current_endpoint[1])

# headers = {"Authorization": "Bearer " + token1}
# r3 = requests.get(current_endpoint[0], headers=headers)
# if r3.ok:
#     pp.pprint(r3.json())
# else:
#     print("Failed to access registry catalog")