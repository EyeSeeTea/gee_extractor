import ee
import click
import json
import time

from datetime import date, timedelta

from logic import reducers, datasets, helpers, dhis2_api

@click.command()
@click.option('--conf', '-c', is_flag=True, default=False)
@click.option('--ouroot', type=str)
@click.option('--fromPeriod', type=click.DateTime(formats=["%Y-%m-%d"]), default=(date.today() - timedelta(days=500)).strftime("%Y-%m-%d"))
@click.option('--toPeriod', type=click.DateTime(formats=["%Y-%m-%d"]), default=(date.today() - timedelta(days=490)).strftime("%Y-%m-%d"))
@click.argument('configurationfile', required=False, type=click.Path(exists=True))
def run(conf, ouroot, fromperiod, toperiod, configurationfile):
    start_time = time.time()
    click.echo('Starting extractor')
    if conf:
        ouroot, fromperiod, toperiod = helpers.read_parameters_from_file(configurationfile)

    if not helpers.print_check_arguments(conf, ouroot, fromperiod, toperiod, configurationfile):
        click.echo('Exiting with errors')
        return
    if not helpers.initializeGoogleEarth():
        click.echo('Exiting with errors')
        return

    next_ous = [ouroot]
    dataset = ee.ImageCollection(datasets.ERA5_DAILY["pointer"]).filterDate(fromperiod, toperiod)
    while len(next_ous) != 0:
        ou_list = dhis2_api.get_organisation_units_with_id(
            next_ous,
            params={
                'fields': 'id,name,coordinates,featureType,children'
            }
        )
        next_ous[:] = []
        for json_ou in ou_list:
            bulk_data_values = {}
            bulk_data_values["dataValues"] = []
            if 'coordinates' in json_ou and json_ou['coordinates'] != 'NONE':
                print(json_ou['name'])
                if json_ou['featureType'] == 'POINT':
                    for day in helpers.daterange(fromperiod, toperiod):
                        day_dataset = dataset.select(
                            tuple(datasets.ERA5_DAILY['mappings'].keys())
                        ).filterDate(day)

                        correct, gee_data = reducers.featureExtractorByGeom(
                            day_dataset,
                            featureType=json_ou['featureType'], coordinates=json_ou['coordinates']
                        )
                        if correct:
                            helpers.add_data_values(bulk_data_values, json_ou['id'], day, datasets.ERA5_DAILY['mappings'], gee_data)
                    dhis2_api.post_dataValueSets(bulk_data_values)
            else:
                print("Organisation unit with name : <{}> and id: <{}> does not have coordinates in the DHIS2 instance".format(json_ou['name'], json_ou['id']))
            next_ous += [c['id'] for c in json_ou['children']]
        print("Import finished in {} seconds".format(time.time() -  start_time))

if __name__ == '__main__':
    run()
