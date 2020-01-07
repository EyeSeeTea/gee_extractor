import os
from simple_rest_client.api import API

print(os.environ.get('WE_INSTANCE', 'localhost:8080'))

api = API(
    api_root_url=os.environ.get('WE_INSTANCE', 'http://localhost:8080') + '/api/',
    params={},
    headers={
        'Authorization': 'Bearer ' + os.environ.get('WE_AUTH_TOKEN')
    },
    timeout=5,
    append_slash=False,
    json_encode_body=True
)

api.add_resource(resource_name='organisationUnits')
api.add_resource(resource_name='dataValueSets')

def get_organisation_units_with_id(id_list,params={}):
    params['filter'] = 'id:in:[' + ','.join(id_list) + ']'
    response = api.organisationUnits.list(
        body=None,
        params=params
    ).body

    return response['organisationUnits']

def post_dataValueSets(content):
    response = api.dataValueSets.create(body=content)
    print("{} > {}. ({})".format(
        response.body['status'],
        response.body['description'],
        response.body['importCount']
    ))

if __name__ == '__main__':
    print(get_organisation_units_with_id(['E4h5WBOg71F'], params={
                'fields': 'id,name,coordinates,featureType,children'
            }))
