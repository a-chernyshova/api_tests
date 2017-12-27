import requests
import unittest
from api_tests import most_popular_api_tests
from api_tests.feed_params import story_types, vertical, API_KEYS, KEY_QUERY


# story_types - list, vertical - list, API_KEYS - dictionary, KEY_QUERY - string
options = ['rss', 'atom']


class Feeds(unittest.TestCase):

    # @unittest.skip
    # Check that have no access without header x-api-key
    def test_access_denied(self):
        for option in options:
            for story_type in story_types:
                feed_url = API_FEED + option + '/' + story_type
                self.assertEqual(requests.get(feed_url).status_code, 403)

    # @unittest.skip
    # Check access to summary feeds without authorization
    def test_access_to_summary(self):
        for option in options:
            for story_type in story_types:
                feed_url = API_FEED + 'summary/' + option + '/' + story_type
                self.assertEqual(requests.get(feed_url).status_code, 200)

    # Check list of API keys for full feeds
    # @unittest.skip
    def test_access_to_full_feeds_common(self):
        for option in options:
            for story_type in story_types:
                feed_url = API_FEED + option + '/' + story_type
                for key in API_KEYS:
                    header_value = {'x-api-key': API_KEYS[key]}
                    self.assertEqual(requests.get(feed_url, headers=header_value).status_code, 200)

    # Check list of API keys for full feeds vertical
    # @unittest.skip
    def test_access_to_full_feeds_vertical(self):
        for category in vertical:
            for feed_format in options:
                for key in API_KEYS:
                    header_value = {'x-api-key': API_KEYS[key]}
                    feed_url = API_FEED + feed_format + '/' + category
                    # self._baseAssertEqual(requests.get(feed_url, headers=header_value).status_code, 200,
                    #                       msg='Failed here ' + feed_format + '/' + category)
                    self.assertEqual(requests.get(feed_url, headers=header_value).status_code, 200,
                                     msg='Failed here ' + feed_format + '/' + category)

    # check if response is empty
    @unittest.skip
    def test_feed_payload(self):
        print(requests.get(API_SUMMARY).content)
        pass

    # @unittest.skip
    def test_key_query_positive(self):
        for category in vertical:
            for feed_format in options:
                feed_url = API_FEED + feed_format + '/' + category + '?key=' + KEY_QUERY
                self._baseAssertEqual(requests.get(feed_url).status_code, 200,
                                      msg='Failed here ' + feed_format + '/' + category + KEY_QUERY)

    # @unittest.skip
    def test_key_query_negative(self):
        for category in vertical:
            for feed_format in options:
                feed_url = API + feed_format + '/' + category + '?key=blblabla'
                self._baseAssertEqual(requests.get(feed_url).status_code, 403,
                                      msg='Failed here ' + feed_format + '/' + category)

    def test_correct_x_api_incorrect_key(self):
        url = API_FEED + 'atom/articles?key=blabla'
        api_key = {'x-api-key': API_KEYS['Sailthru']}
        self._baseAssertEqual(requests.get(url, headers=api_key).status_code, 200,
                              msg='Failed here ' + url + ' ' + api_key['x-api-key'])

    def test_incorrect_x_api_correct_key(self):
        url = API_FEED + 'atom/articles?key=' + KEY_QUERY
        api_key = {'x-api-key': API_KEYS['Sailthru'] + '11'}
        self._baseAssertEqual(requests.get(url, headers=api_key).status_code, 403,
                              msg='Failed here ' + url + ' ' + api_key['x-api-key'])

if __name__ == '__main__':
    TEST_DATA = most_popular_api_tests.load_config('api_tests/api_config.txt')
    API_FEED = TEST_DATA['API_FEED']
    API_SUMMARY = TEST_DATA['API_SUMMARY']
    unittest.main()

# TODO: build test suite, add skipIf
