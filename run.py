import ee
import click
import json
import time
import itertools
from datetime import date, timedelta

from logic import reducers, datasets, helpers, dhis2api


@click.command()
@click.option('--conf', '-c', is_flag=True, default=False)
@click.option('--instance_url', type=str, help="DHIS2 instance root URL")
@click.option('--user', type=str, help="DHIS2 user username to connect to the DHIS2 instance")
@click.option('--pwd', type=str, help="DHIS2 user password to connect to the DHIS2 instance")
@click.option('--gee', type=str, help="Google Earth Engine image collection")
@click.option('--ouroot', type=str, help="Organisation unit id referencing the root of the subtree target for the data import")
@click.option('--fromPeriod', type=click.DateTime(formats=["%Y-%m-%d"]), default=(date.today() - timedelta(days=500)).strftime("%Y-%m-%d"), help="Lowest limit from the time interval desired for the data import")
@click.option('--toPeriod', type=click.DateTime(formats=["%Y-%m-%d"]), default=(date.today() - timedelta(days=490)).strftime("%Y-%m-%d"), help="Highest limit from the time interval desired for the data import")
@click.argument('configurationfile', required=False, type=click.Path(exists=True))
def run(conf, instance_url, user, pwd, gee, ouroot, fromperiod, toperiod, configurationfile):
    """Run gee_extractor

    CONFIGURATIONFILE contains all the parameters if -c flag is activated
    """
    start_time = time.time()
    click.echo('Starting extractor')
    if conf:
        instance_url, user, pwd, gee, ouroot, fromperiod, toperiod = helpers.read_parameters_from_file(configurationfile)

    if not helpers.print_check_arguments(conf, instance_url, user, pwd, gee, ouroot, fromperiod, toperiod, configurationfile):
        click.echo('Exiting with errors')
        return
    if not helpers.initializeGoogleEarth():
        click.echo('Exiting with errors')
        return

    d2 = dhis2api.Dhis2Api(url=instance_url, username=user, password=pwd)

    next_ous = [ouroot]
    dataset = ee.ImageCollection(datasets.data[gee]["pointer"]).filterDate(fromperiod, toperiod)
    while len(next_ous) != 0:
        params = {
            'fields': 'id,name,coordinates,featureType,children',
            'paging': 'false'
        }

        ou_list = []
        for group in itertools.zip_longest(*(iter(next_ous),) * 500):
            params['filter'] = 'id:in:[' + ','.join(filter(None, group)) + ']'
            ou_list += d2.get(path='/organisationUnits', params=params)['organisationUnits']

        next_ous[:] = []
        for json_ou in ou_list:
            bulk_data_values = {}
            bulk_data_values["dataValues"] = []
            if 'coordinates' in json_ou and json_ou['coordinates'] != 'NONE':
                if json_ou['featureType'] == 'POINT':
                    for day in helpers.daterange(fromperiod, toperiod):
                        day_dataset = dataset.select(
                            tuple(datasets.data[gee]['mappings'].keys())
                        ).filterDate(day)

                        correct, gee_data = reducers.featureExtractorByGeom(
                            day_dataset,
                            featureType=json_ou['featureType'], coordinates=json_ou['coordinates']
                        )
                        if correct:
                            helpers.add_data_values(bulk_data_values, json_ou['id'], day, datasets.data[gee]['mappings'], gee_data)
                    d2.post('/dataValueSets', payload=bulk_data_values)
                    print(">> Import done for organisation unit with name: <{}> and id: <{}> for period <{}>".format(
                        json_ou['name'],
                        json_ou['id'],
                        day.strftime("%Y%m%d")
                        ))
                else:
                    print("Organisation unit with name: <{}> and id: <{}> skipped do to geometry size".format(json_ou['name'], json_ou['id']))
            else:
                print("Organisation unit with name : <{}> and id: <{}> does not have coordinates in the DHIS2 instance".format(json_ou['name'], json_ou['id']))
            next_ous += [c['id'] for c in json_ou['children']]
        print("Import finished in {} seconds".format(time.time() -  start_time))

if __name__ == '__main__':
    run()
