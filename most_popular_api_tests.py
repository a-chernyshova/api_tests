import requests
from selenium import webdriver
import json
import logging

logging.basicConfig(filename="log.txt", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.INFO)


def load_config(filename):
    logging.info('Open config')
    file = open(filename, 'r+')
    file.readline()
    test_data = {}
    for line in file:
        key, value = line.split(' = ')
        logging.debug('Read lines from file and build dict' + key + ':' + value)
        test_data[key] = value[:-1]
    file.close()
    return test_data


def update_most_popular(domain, link_list):
    logging.info('Call articles to update MP list')
    for link in link_list:
        for i in range(1, 10):
            try:
                r = requests.head(domain + link)
                logging.info('Calling' + link)
                if r.status_code != 200:
                    logging.debug(link + ' responds with ' + r.status_code)
            except requests.ConnectionError:
                logging.critical(link + ' unreachable ' + r.status_code)
    print('INFO: most popular - is updated')


def put_new_article_in_mp(domain, url):
    for i in range(1, 50):
        try:
            r = requests.head(domain + url)
            logging.info('Call ' + url)
            if r.status_code != 200:
                logging.debug(url + ' returns ' + r.status_code)
        except requests.ConnectionError:
            logging.critical(url + ' unreachable')
    print('INFO: added new article in mp')


# find tb1 slug via selenium
def find_top_box_story1():
    browser = webdriver.Chrome()
    browser.get(DOMAIN)
    top_story = browser.find_element_by_class_name('TopBox__image-link')
    top_story_slug = top_story.get_attribute('href')
    top_story_slug = top_story_slug.split('/')[3]
    browser.close()
    return top_story_slug


def retrieve_top_story_from_api(api_domain):
    logging.info('Start retrieving top stories')
    response = requests.get(api_domain + 'homepage').json()
    topstories = []
    for n in range(4):
        topstories.append(response['articles'][n]['slug'])
        logging.info('Added ' + str(n) + ' as top story')
    return topstories


def find_sponsored(api_domain):
    logging.info('Start sorting out of sponsored article')
    for i in range(1, 20):
        params = {'page': i, 'sort': 'date', 'per_page': 12, 'type': 'article'}
        response = requests.get(api_domain + 'search', params=params).json()['articles']

        for article in response:
            if article['Metadata']['sponsored']:
                logging.debug('Sponsored article is found ' + article['slug'] )
                return article['slug']


def check_mp_list_len(mp_list):
    if len(mp_list) < 5:
        logging.critical('Incorrect MP list lenght ' + len(mp_list) + '. Expect: 5')
    print('INFO: checked mp list length')


def get_mp_list(api_mp):
    response = requests.get(api_mp).json()
    mp_list = []
    for article in response:
        logging.debug('Add article ' + article['slug'] + ' in MP list')
        mp_list.append(article['slug'])
    print('INFO: most popular list is retrieved')
    return mp_list


def check_update_of_mp(list1, list2):
    if len(set(list1)&set(list2)) > 6:
        print("Error: most popular list isn't changed")


# check if list contains cheats, sponsored, branded articles, duplicates or top story1, and len < 5
def filter_out_mp(api_url, api_domain):
    response = requests.get(api_url).json()
    incorrect_list = []  # contains sponsored, branded, duplicates and top story1 articles
    mp_list = []
    for article in response:
        if article['type'] != 'article':
            incorrect_list.append(article['slug' + ' - not article'])
            logging.critical('List contains not article type story')
        elif article['Metadata']['sponsored'] == True or article['Metadata']['branded'] == True:
            incorrect_list.append(article['slug'] + ' - sponsored')
            logging.critical('List contains sponsored story')
        # check if top story 1 is in mp list
        elif article['canonical_slug'] == retrieve_top_story_from_api(api_domain)[0]:
            incorrect_list.append(article['canonical_slug'] + ' - is top story')
            logging.critical('List contains top story')
        elif article['canonical_slug'] in mp_list:
            incorrect_list.append(article['canonical_slug'] + ' - duplicated')
            logging.critical('List contains duplicated stories')
        else:
            mp_list.append(article['canonical_slug'])
            logging.debug('Added story to MP list')

    if not incorrect_list and len(mp_list) > 5:
        logging.debug('Correct MP list')
        
    else:
        if len(mp_list) < 5:
            print('MP list is not correct. Only ', len(mp_list), ' articles in list.')
            logging.warning('Incorrect lenght of MP list')
        else:
            print('Incorrect slugs: ', incorrect_list)


def get_list_of_most_recent_stories(api_domain, story_type, header_key):
    params = {'page': 1, 'sort': 'date', 'per_page': 12, 'type': story_type}
    headers = {'x-api-key': header_key}
    response = requests.get(api_domain + 'search', params=params, headers=headers)
    content = response.json()
    articles = content['articles']
    article_slugs = []
    for article in articles:
        logging.debug('Added one of most recent stories in MP list')
        article_slugs.append(article['slug'])

    return article_slugs


def get_list_of_sponsored(endpoint):
    response = requests.get(endpoint)   #.json()
    content = response.json()
    articles = content['articles']
    article_slugs = []
    for article in articles:
        if article['Metadata']['sponsored'] == 'true' or article['Metadata']['branded'] == 'true':
            article_slugs.append(article['slug'])
    if len(article_slugs) == 0:
        print('need create loop')
    return article_slugs


if __name__ == '__main__':
    TEST_DATA = load_config('api_config.txt')
    API_STATUS = TEST_DATA['API_STATUS']
    API_MP = TEST_DATA['API_MP']
    API_DOMAIN = TEST_DATA['API_DOMAIN']
    DOMAIN = TEST_DATA['DOMAIN']
    HEADER_KEY = TEST_DATA['X_API_KEY']

    if requests.head(API_STATUS).status_code == 200:

        update_most_popular(DOMAIN, get_list_of_most_recent_stories(API_DOMAIN, 'article', HEADER_KEY))
        update_most_popular(DOMAIN, get_list_of_most_recent_stories(API_DOMAIN, 'cheat', HEADER_KEY))

    # TODO: rework put_new_article_in_mp with arg* to put 1-N articles in one time
        put_new_article_in_mp(DOMAIN, retrieve_top_story_from_api(API_DOMAIN)[0])
        put_new_article_in_mp(DOMAIN, retrieve_top_story_from_api(API_DOMAIN)[1])
        put_new_article_in_mp(DOMAIN, find_sponsored(API_DOMAIN))
        filter_out_mp(API_MP, API_DOMAIN)

    # TODO: rework next 2 methods
        # most_popular_list_updated = get_mp_list(API_MP)
        # check_update_of_mp(most_popular_list, most_popular_list_updated)
    else:
        print('API responds with', requests.head(API_STATUS).status_code)
