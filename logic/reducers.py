import ee
import json

def featureExtractorByGeom(image,featureType, coordinates):
    try:
        if featureType == 'POINT':
            reducerGeom = ee.Geometry.Point(json.loads(coordinates))
        elif featureType in ['POLYGON', 'MULTI_POLYGON']:
            reducerGeom = ee.Geometry.MultiPolygon(json.loads(coordinates))

        precipitation = image.getRegion(reducerGeom, scale=30).getInfo()
        return True, precipitation
    except Exception as e:
        print('Failed to extract G.E.E data:')
        print(str(e))
        return False, []