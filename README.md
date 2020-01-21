# gee_extractor
Connect your DHIS2 instance to real live data from Google Earth Engine.

This python script enables custom or periodic extraction of data from Google Earth Engine into a DHIS2 instance.

## Context

[Google Earth Engine](https://earthengine.google.com/) is a computing platform that allows users to run geospatial analysis on Google's infrastructure. This script uses the Python library API which allows for automating batch processing tasks, piping Earth Engine processed data to Python run-time. More information in Earth Engine Python API environemnts and setup can be found on [this link](https://developers.google.com/earth-engine/python_install)

### Earth Engine Data Structures

The two most fundamental geographic data structures in Earth Engine are **Image** and **Feature** corresponding to raster and vector data types, respectively. Images contain bands and a dictionary of properties while features are mainly geometries with a dictionary of properties. Usually Earth Engine refers to **ImageCollection** as a set of images on a time-series basis. The consequent features are also stored in a **FeatureCollection** object.

## Basic installation
Git clone or download
~~~~~~
git clone git@github.com:EyeSeeTea/gee_extractor.git
cd gee_extractor/
~~~~~~
Python requirements
~~~~~~
pip install -r requirements.txt
~~~~~~

Get Google Earth Engine credentials: Whiting your python environment run the following command and follow the resulting printed isntructions. A URL will be provided that generates an authorization code upon agreement.
~~~~~~
earthengine authenticate
~~~~~~

Upon entering the authorization code, an authorization token gets saved to a credentials file which can be found below. Subsequent use of the API's ee.Initialize() command and the earthengine command line tool will look to this file to authenticate. If you want to revoke authorization, simply delete the credentials file.
~~~~~~
$HOME/.config/earthengine/credentials
~~~~~~


## Configuration

The scripts contains the following customized parameters:

* ``instance_url``: DHIS2 instance root URL.
* ``user``: DHIS2 user username to connect to the DHIS2 instance.
* ``pwd``: DHIS2 user password to connect to the DHIS2 instance.
* ``ouroot``: Organisation unit id referencing the root of the subtree target for the data import.
* ``fromperiod``: Lowest limit from the time interval desired for the data import.
* ``toperiod``: Highest limit from the time interval desired for the data import.

## Usage
```bash
Usage: run.py [OPTIONS] [CONFIGURATIONFILE]
  Run gee_extractor
  CONFIGURATIONFILE contains all the parameters if -c flag is activated
Options:
  -c, --conf
  --instance_url TEXT      DHIS2 instance root URL
  --user TEXT              DHIS2 user username to connect to the DHIS2
                           instance
  --pwd TEXT               DHIS2 user password to connect to the DHIS2
                           instance
  --gee TEXT               Google Earth Engine image collection
  --ouroot TEXT            Organisation unit id referencing the root of the
                           subtree target for the data import
  --fromPeriod [%Y-%m-%d]  Lowest limit from the time interval desired for the
                           data import
  --toPeriod [%Y-%m-%d]    Highest limit from the time interval desired for
                           the data import
  --help                   Show this message and exit.
```


To provide all the parameters by command line, this script just needs to be invoked as follows
~~~~~~
python run.py --instance_url instance --user user --pwd pwd --gee ERA5_DAILY --outroot ou --fromPeriod fromP --toPeriod toPeriod
~~~~~~

Alternatively a configuration file can be specified as a positional argument like follows:
~~~~~~
python run.py -c CONFIGURATIONFILE
~~~~~~

An example of configuration is included in [conf.json](./conf.json)

## Data extraction

Data is extracted from Google Earth Engine by filtering by Geometry and Period.
Periods are extracted from the interval introduced in the configuration and Geometries from the DHIS2 instance organisation units.

The script reduces the geometry information available for a certain period to single float number and import it to the corresponding DHIS2 data entry point.

The script enables full flexibility into which API resource from the Earth Engine connect. Datasets must be added to the [dataset management file](./logic/datasets.py) and correctly introduced in the parameters.

Each dataset containes the following structure:

```json
"ERA5_DAILY": {
        "pointer": "ECMWF/ERA5/DAILY",
        "mappings": {
            "total_precipitation": "uWYGA1xiwuZ",
            "mean_2m_air_temperature": "RSJpUZqMoxC"
        },
        "doc": "https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_DAILY",
    },
```

* ``pointer``: Image collection resource name in the Earth Engine API.
* ``doc``: Additional link with dataset references.
* ``mappings``: Set of mappings from Earth Engine feature bands and DHIS2 data element ids.
