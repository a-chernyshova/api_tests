import requests
from api_tests import most_popular_api_tests


# call each endpoints loaded from file, check if it returns not 200 and not empty json


def check_status_code_and_response(domain, endpoints):
    for endpoint in endpoints:
        try:
            r = requests.head(domain + endpoint)
            if r.status_code != 200:
                print(domain + endpoint, ' returns ', r.status_code)
            elif not requests.get(domain + endpoint).json():
                print('Error: empty response ' + endpoint)
        except requests.ConnectionError:
            print(domain + endpoint, ": failed to connect")


def load_test_data(filename):
    test_data = most_popular_api_tests.load_config(filename)
    domain, end_points, search = test_data['DOMAIN'], test_data['END_POINTS'], test_data['API_SEARCH']
    end_points = end_points[1:-1].split(', ')

    return domain, end_points, search


def article_env_endpoints(domain, search):
    response = requests.get(domain + search).json()['articles']
    slug = 'v1/' + response[0]['canonical_slug']  # grab the first 2 results
    slugs = [slug, slug + '/images', slug + '/related']
    check_status_code_and_response(domain, slugs)
    # /related response can be empty


if __name__ == '__main__':
    DOMAIN, END_POINTS, SEARCH = load_test_data('api_endpoints_test_data.txt')
    check_status_code_and_response(DOMAIN, END_POINTS)
    article_env_endpoints(DOMAIN, SEARCH)
