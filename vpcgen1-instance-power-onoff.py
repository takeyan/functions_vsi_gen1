import http.client
import gzip
import json
import sys

def get_token(APIKEY):
    # URL for token
    conn = http.client.HTTPSConnection("iam.cloud.ibm.com")

    # Payload for retrieving token. Note: An API key will need to be generated and replaced here
    payload = f'grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey={APIKEY}&response_type=cloud_iam'


    # Required headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
    }

    try:
        # Connect to endpoint for retrieving a token
        conn.request("POST", "/identity/token", payload, headers)

        # Get and read response data
        res = conn.getresponse().read()
        data = res.decode("utf-8")

        # Format response in JSON
        json_res = json.loads(data)

        # Concatenate token type and token value
        return json_res['token_type'] + ' ' + json_res['access_token']

    # If an error happens while retrieving token
    except Exception as error:
        print(f"Error getting token. {error}")
        raise

def print_json(data):
    print(json.dumps(json.loads(data), indent=2, sort_keys=True))


def fetch_instances(conn, version, headers, vpcname):

    payload = ""

    try:
        # Connect to rias endpoint for instances
        conn.request("GET", "/v1/instances?version=" + version + "&vpc.name=" + vpcname, payload, headers)

        # Get and read response data
        res = conn.getresponse()
        data = res.read()

        return data


    # If an error happens while fetching instances
    except Exception as error:
        print(f"Error fetching instances. {error}")
        raise


def create_action(conn, version, headers, instance_id, action):

    payload = f'{{ \"type\" : \"{action}\" }}'

    try:
        conn.request("POST", f"/v1/instances/{instance_id}/actions?version={version}&generation=1", payload, headers)


        # Get and read response data
        res = conn.getresponse()
        data = res.read()

#        print_json(data.decode("utf-8"))
        return json.loads(data)

    except Exception as error:
        print(f"Error fetching instances. {error}")
        raise


def main(dict):
    api = dict['api']
    reg = dict['region']
    ver = dict['version']
    vpc = dict['vpc']
    act = dict['action']
    vsi = dict['instance']

    con = http.client.HTTPSConnection(f"{reg}.iaas.cloud.ibm.com")
    hdr = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json',
        'Authorization': get_token(api),
        'cache-control': 'no-cache'
    }

    res = json.loads(fetch_instances(con, ver, hdr, vpc))
    instances = res['instances']

    res = "NOT FOUND"
    for instance in instances:
        if instance['name'] == vsi:
            id = instance['id']
            res = create_action(con, ver, hdr, id, act)

    return res



