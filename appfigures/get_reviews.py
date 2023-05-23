"""This module provides functions to query and download app reviews
from the Appfigures API. Please set your API key in config/config.py"""
import os
import math
import json
import argparse
import requests
from requests.auth import HTTPBasicAuth
from tqdm import trange

from config.config import KEY, PRODUCT_IDS


HOST = 'https://api.appfigures.com/v2'
REVIEW_ENDPOINT = 'reviews'
COUNTS_ENDPOINT = 'reviews/count'
QUERY = '?products={products}&count={count}&lang={lang}&start={start}'
COUNT = 250


def build_query(product_ids, language, start_date, count):
    return QUERY.format(products=','.join(map(str, product_ids)),
                        count=count,
                        lang=language,
                        start=start_date)


def add_page(url, page):
    return url + '&page=' + str(page)


def get(url, username, password, key):
    r = requests.get(url,
                     auth=HTTPBasicAuth(username, password),
                     headers={'X-Client-Key': key})
    assert r.status_code == 200
    return r


def get_total_count(url, username, password, key):
    r = get(url, username, password, key)
    return sum(r.json()['products'].values())


def get_review_page(url, username, password, key, page):
    return get(add_page(url, page), username, password, key).json()['reviews']


def get_reviews(username, password, key, product_ids, language, start_date, count):
    reviews = []
    query = build_query(product_ids, language, start_date, count)
    review_url = os.path.join(HOST, REVIEW_ENDPOINT + query)
    counts_url = os.path.join(HOST, COUNTS_ENDPOINT + query)
    total_counts = get_total_count(counts_url, username, password, key)
    for page in trange(1, math.ceil(total_counts / float(count)) + 1):
        reviews += get_review_page(review_url, username, password, key, page)
    return reviews


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', required=True, type=str,
                        help='path to output file')
    parser.add_argument('--user', '-u', required=True, type=str,
                        help='username')
    parser.add_argument('--passw', '-pw', required=True, type=str,
                        help='password')
    parser.add_argument('--start', '-s', required=True, type=str,
                        help='start date in format yyyy-mm-dd')
    parser.add_argument('--language', '-l', required=False, type=str,
                        default='en',
                        help='language of translations')
    args = parser.parse_args()
    username = args.user
    password = args.passw
    language = args.language
    start_date = args.start
    reviews = get_reviews(username, password, KEY, PRODUCT_IDS, language, start_date, COUNT)
    json.dump(reviews, open(args.file, 'w'))
