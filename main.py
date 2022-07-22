import csv
import time
import simplekml
from polycircles import polycircles

import googlemaps

FILE_PATH = 'enderecos.csv'
GOOGLE_MAPS_API_TOKEN = 'AIzaSyD7pgtiBTMfeT6co1xV8YR8QUiaxKcfS4I'


def readfile(path):
    rows = []
    with open(path, 'r', encoding='CP1252') as file:
        csvreader = csv.reader(file, delimiter=';')
        header = next(csvreader)
        for row in csvreader:
            rows.append(row)
    return rows


class Location:
    def __init__(self, row, google_result):
        self.row = row
        self.google_result = google_result


def search(gmaps, rows):
    locations = []
    for row in rows:
        search_address = row[1] + ' ' + row[2] + ' ' + row[3] + ' ' + row[4]
        location = gmaps.geocode(search_address)

        if type(location) == list:
            if location:
                locations.append(Location(row, location[0]))
            else:
                print("No results for {}".format(search_address))
        else:
            locations.append(Location(row, location["results"][0]))
        time.sleep(2)

    return locations


def convert_to_geojson(locations):
    geo_locations = []
    for loc in locations:
        lng = loc.google_result['geometry']['location']['lng']
        lat = loc.google_result['geometry']['location']['lat']
        formatted_address = loc.google_result['formatted_address']
        geolocation = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lng, lat]
            },
            'properties': {
                'name': loc.row[1],
                'address': formatted_address,
                'radius': loc.row[8],
            }
        }
        geo_locations.append(geolocation)
    return geo_locations


def main():
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_TOKEN)
    rows = readfile(FILE_PATH)

    locations = search(gmaps, rows)

    kml = simplekml.Kml()

    for loc in locations:
        lng = loc.google_result['geometry']['location']['lng']
        lat = loc.google_result['geometry']['location']['lat']

        circle = polycircles.Polycircle(latitude=lat,
                                        longitude=lng,
                                        radius=int(int(loc.row[8]) * 1000),
                                        number_of_vertices=50)
        pol = kml.newpolygon(name=loc.row[1], outerboundaryis=circle.to_kml())
        pol.style.polystyle.color = simplekml.Color.changealphaint(50, simplekml.Color.red)

    kml.save('google.kml')


if __name__ == '__main__':
    main()
