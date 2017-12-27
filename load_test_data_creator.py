import requests
import datetime
from api_tests import most_popular_api_tests


def get_list_of_most_recent_articles(endpoint, article_type):
    response = requests.get(endpoint+article_type)
    content = response.json()
    articles = content['articles']
    slugs = []
    for article in articles:
        if article:
            slugs.append(article['slug'])

    return slugs


def put_list_in_file(article_list, cheat_list):
    file = open('load_test_data_creator/template_test_data_load.csv', 'r+')
    file.readline()
    test_data = []
    i = 0
    for line in file:
        data = '"' + line[1:-2] + article_list[i] + ',' + cheat_list[i] + ',' + '"'
        test_data.append(data)
        i += 1
    file.close()

    return test_data


def create_test_data_file(data_list):
    timestamp = str(datetime.datetime.now())[:10]
    new_file_name = 'loadtest' + timestamp + '.csv'
    file = open('load_test_data_creator/' + new_file_name, 'a')
    for line in data_list:
        file.write(line + '\n')

    file.close()


def get_tags_from_db():
    pass


def run_test_creator(search_endpoint):
    if requests.head(search_endpoint).status_code == 200:
        article_list = get_list_of_most_recent_articles(search_endpoint, 'article')
        cheat_list = get_list_of_most_recent_articles(search_endpoint, 'cheat')
        test_data = put_list_in_file(article_list, cheat_list)
        create_test_data_file(test_data)
    else:
        print('API responds with', requests.head(API_SEARCH_PROD).status_code)


if __name__ == '__main__':
    TEST_DATA = most_popular_api_tests.load_config('api_tests/api_config.txt')
    API_SEARCH_STAGE = TEST_DATA['API_SEARCH_STAGE']
    API_SEARCH_PROD = TEST_DATA['API_SEARCH_PROD']
    run_test_creator(API_SEARCH_PROD)


# TODO: connect to db and retrieve tags select slug from tag where id in (select tag_id, count(*)
# from article_tag group by tag_id having count(article_id) > 10 limit 6;);
