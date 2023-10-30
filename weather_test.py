import unittest
from unittest.mock import patch
from main import City, Weather, CityNotFoundError, WeatherError


class CityTests(unittest.TestCase):
    def test_city_request(self):
        with patch('main.make_request') as mock_make_request:
            mock_make_request.return_value = '{"results": [{"name": "New York", "latitude": 40.7128, "longitude": -74.0060, "country": "US"}]}'
            city = City(name='Berlin')
            city.request()

            self.assertEqual(city.name, 'Berlin')
            self.assertEqual(city.latitude, 52.52437)
            self.assertEqual(city.longitude, 13.404954)
            self.assertEqual(city.country, 'Germany')

    def test_city_request_not_found(self):
        with patch('main.make_request') as mock_make_request:
            mock_make_request.return_value = '{"results": []}'
            city = City(name='Invalid City')

            with self.assertRaises(CityNotFoundError):
                city.request()


class WeatherTests(unittest.TestCase):
    def test_weather_request(self):
        with patch('main.make_request') as mock_make_request:
            mock_make_request.return_value = '{"current_weather": {"temperature": 25, "time": "2023-06-01T12:00:00"}, "elevation": 100, "hourly": {"relativehumidity_2m": [60, 55, 62], "time": ["2023-06-01T12:00:00", "2023-06-01T13:00:00", "2023-06-01T14:00:00"]}}'
            weather = Weather(city='Berlin')
            weather.request()

            self.assertEqual(weather.temperature, 25)
            self.assertEqual(weather.timeofreq, "2023-06-01T12:00:00")
            self.assertEqual(weather.elevation, 100)
            self.assertEqual(weather.humidity, 60)

    def test_weather_request_no_data(self):
        with patch('main.make_request') as mock_make_request:
            mock_make_request.return_value = '{}'

            with self.assertRaises(WeatherError):
                weather = Weather(city='New York')
                weather.request()


if __name__ == '__main__':
    unittest.main()