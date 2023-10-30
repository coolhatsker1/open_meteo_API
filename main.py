#!/usr/bin/env python3

import json
import requests
import datetime
from geopy.geocoders import Nominatim

# TODO: try using Requests package
#       (https://requests.readthedocs.io)


def make_request(url):
    """Issue GET request to URL returning text."""
    # TODO: try parsing response headers, content-type
    # to get encoding from there
    # (content-type: text/html; charset=UTF-8)
    # TODO: try parsing it with regexp
    respfile = requests.get(url)

    hdr = respfile.headers
    ct = hdr.get('content-type', '; charset=UTF-8')
    enc = ct.split(';')[-1].split('=')[-1]
    enc = enc.lower()

    # bindata = respfile.read()
    data = respfile.content.decode(encoding=enc)
    return data


class WeatherError(Exception):
    pass


class CityNotFoundError(WeatherError, LookupError):
    """Raised when city not found."""
    pass


class RequestData:
    URL_TEMPLATE = ''

    def request(self, **kwargs):
        """Make request to remote URL parsing json result."""
        # Create url for further GET request to OpenMeteo
        url = self.URL_TEMPLATE.format(**kwargs)

        text = make_request(url=url)
        data = json.loads(text)
        return data


class City(RequestData):
    URL_TEMPLATE = (
        'https://geocoding-api.open-meteo.com/v1/search?name={name}')

    def __init__(self, name=None, latitude=None, longitude=None):
        if name is not None:
            name = name.title()
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        #self.country = country

    def request(self):
        cities = self.find_cities()

        if self.name not in cities:
            raise CityNotFoundError(self.name)

        # code below executes only if we didn't raise an exception
        for k, v in cities[self.name].items():
            setattr(self, k, v)

    def find_cities(self):
        data = super().request(name=self.name)
        data = data.get('results', {})
        res = {}
        for entry in data:
            name = entry['name']
            res[name] = {
                'latitude': entry['latitude'],
                'longitude': entry['longitude'],
                'country': entry['country']
            }

        return res


class Weather(RequestData):
    URL_TEMPLATE = ('https://api.open-meteo.com/v1/forecast?'
                    'latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m')

    def __init__(self, city=None, latitude=None, longitude=None):
        # TODO: try getting latitute and longitude from city name
        #       if not provided directly
        # i.e. Weather(city='kyiv') or Weather(latitude=30, longitude=40)
        if isinstance(city, str):
            # Create a City object from the city name
            city = City(name=city)
            city.request()

        if (city is None) and (latitude is None or longitude is None):
            msg = ('Either city or a pair of latitude, '
                   'longitude must be provided')
            raise WeatherError(msg)

        self.city = city
        self.lat = latitude or city.latitude
        self.lon = longitude or city.longitude
        self.data = None


    def __repr__(self):
        n = type(self).__name__
        return f'{n}(latitude={self.lat}, longitude={self.lon})'

    def request(self):
        data = super().request(lat=self.lat, lon=self.lon)
        self.data = data

    def get_city(self):
        '''makes possible to output city name if it is parsed via name as an attribute or a pair of coordinates'''
        if isinstance(city, str):
            if self.city:
                return self.city.name if self.city else None
        else:
            geolocator = Nominatim(user_agent="my-app")
            location = geolocator.reverse((self.lat, self.lon))
            return location.raw["address"]["city"]
    @property
    def temperature(self):
        """Retreive temperature from OpenMeteo response."""
        if self.data is None:
            self.request()
        return self.data['current_weather']['temperature']

    @property
    def timeofreq(self):
        """Retreive time of an OpenMeteo response."""
        if self.data is None:
            self.request()
        return self.data['current_weather']['time']

    @property
    def elevation(self):
        """Retreive elevation from OpenMeteo response."""
        if self.data is None:
            self.request()
        return self.data['elevation']

    @property
    def windspeed(self):
        """Retreive windspeed from OpenMeteo response."""
        if self.data is None:
            self.request()
        return self.data['current_weather']['windspeed']

    @property
    def humidity(self):
        '''Retrieve relative humidity in %
           Works only for the cities where weather forecast is provided hourly such as lat=52.52 lon=13.419998
        '''
        if self.data is None:
            self.request()

        dateTimeObj = datetime.datetime.now()
        curr_date = dateTimeObj.strftime("%Y-%m-%dT%H")
        index_el = 0
        for k, v in self.data.items():
            if k == 'hourly':
                for i, el in enumerate(v['time']):
                    if el[:-3] == curr_date:
                        index_el = i
                        break

        rh_data = v['relativehumidity_2m'][index_el]
        return rh_data

# TODO: add argument parsing
# TODO: try setting city as: Ukraine/Kyiv or simply Kyiv

if __name__ == '__main__':
    from pprint import pprint


    import sys
    name = sys.argv[1] if len(sys.argv) == 2 else 'lviv'

    city = City(name)
    city.request()

    print('Parsing city object as a pair of coordinates')
    wth = Weather(latitude=52.52, longitude=13.419998)
    print(f'Temperature in {wth.get_city()} is {wth.temperature} by {wth.timeofreq}')
    print(f'Elevation in {wth.get_city()} is {wth.elevation} by {wth.timeofreq}')
    print(f'Windspeed in {wth.get_city()} is {wth.windspeed} by {wth.timeofreq}')
    print(f'Relative humidity in {wth.get_city()} is {wth.humidity} by {wth.timeofreq}\n')

    print('Parsing city object as an object')
    wth = Weather(city=city)
    print(f'Temperature in {city.name} is {wth.temperature} by {wth.timeofreq}')
    print(f'Elevation in {city.name} is {wth.elevation} by {wth.timeofreq}')
    print(f'Windspeed in {city.name} is {wth.windspeed} by {wth.timeofreq}')
    print(f'Relative humidity in {city.name} is {wth.humidity} by {wth.timeofreq}\n')

    print('Parsing city object as a name')
    wth = Weather(city='kyiv')
    print(f'Temperature in {wth.get_city()} is {wth.temperature} by {wth.timeofreq}')
    print(f'Elevation in {wth.get_city()} is {wth.elevation} by {wth.timeofreq}')
    print(f'Windspeed in {wth.get_city()} is {wth.windspeed} by {wth.timeofreq}')
    print(f'Relative humidity in {wth.get_city()} is {wth.humidity} by {wth.timeofreq}\n')

