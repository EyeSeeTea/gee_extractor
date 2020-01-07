import ee
import json

from datetime import datetime, timedelta

def initializeGoogleEarth():
    try:
        ee.Initialize()
        return True
    except Exception as e:
        print('Failed to initialize Google Earth Engine')
        print(str(e))
        return False

def read_parameters_from_file(file_path):
    with open(file_path) as f:
        conf_file = json.load(f)
        return conf_file["ouroot"], datetime.strptime(conf_file["fromperiod"], "%Y-%m-%d"), datetime.strptime(conf_file["toperiod"], "%Y-%m-%d")

def print_check_arguments(conf, ouroot, fromperiod, toperiod, configurationfile):
    print('Received the following arguments:')
    print('--conf flag: ', conf)
    if conf:
        print('CONFIGURATIONFILE path: ', configurationfile)
        if not all([configurationfile]):
            print('Error: With conf flag activated, configuration file path cannot be None')
            return False
    print('--ouroot option: ', ouroot)
    print('--fromPeriod option: ', fromperiod)
    print('--toPeriod option: ', toperiod)
    if not all([ouroot, fromperiod, toperiod]):
        print('Error: With conf flag disactivated, all options must be specified')
        return False
    return True

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def add_data_values(bulk, org_unit_id, period, de_mappings, gee_data):
    header = gee_data[0]
    values = gee_data[1:]
    for value in values:
        for band, dataElement in de_mappings.items():
            new_data_value = {}
            new_data_value["dataElement"] = dataElement
            new_data_value["period"] = period.strftime("%Y%m%d")
            new_data_value["orgUnit"] = org_unit_id
            new_data_value["value"] = value[header.index(band)]
            bulk["dataValues"].append(new_data_value)
