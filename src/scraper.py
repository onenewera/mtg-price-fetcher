import requests
from bs4 import BeautifulSoup
from rapidfuzz import process
from html import unescape
import urllib
import logging

logger = logging.getLogger(__name__)

def _get_dom_from_url(url: str, timeout: int = 20) -> BeautifulSoup:
    logger.info("Fetching URL: %s", url)
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

MTGSTOCKS_BASE_URL = 'http://www.mtgstocks.com'
QUERY_STRING = '/cards/search?utf8=%E2%9C%93&print%5Bcard%5D={}&button='
SETS_PATH = MTGSTOCKS_BASE_URL + '/sets'

def generate_search_url(name):
    formatted_name = urllib.parse.quote('+'.join(name.split(' ')), '/+')
    return MTGSTOCKS_BASE_URL + QUERY_STRING.format(formatted_name)

# searches all items on the given page matching the given selector
# and returns the one closes
def get_matching_item_on_page(url, text, selector):
    dom = _get_dom_from_url(url)
    elems = dom.select(selector)

    possible_matches = [elem.get_text(strip=True) for elem in elems]
    best_match = process.extractOne(text, possible_matches)

    match_index = possible_matches.index(best_match[0])
    return elems[match_index]

def get_card_url_from_search_results(search_url, name):
    card_link = get_matching_item_on_page(search_url, name, '.table > tbody > tr > td > a')

    return MTGSTOCKS_BASE_URL + (card_link.get('href') if card_link else '')

def card_url_from_name(name):
    query_url = generate_search_url(name)
    response = requests.get(query_url, allow_redirects=False)

    if (response.status_code in range(301, 307)):
        return response.headers['Location']
    elif (response.status_code == requests.codes.ok):
        return get_card_url_from_search_results(query_url, name)

    return None

def card_url_from_set(name, card_set):
    set_link = get_matching_item_on_page(SETS_PATH, card_set, '.list > a')

    card_link = get_matching_item_on_page(
        MTGSTOCKS_BASE_URL + (set_link.get('href') if set_link else ''),
        name,
        '.table tr > td > a'
    )

    return MTGSTOCKS_BASE_URL + (card_link.get('href') if card_link else '')

def scrape_price(card_url):
    dom = _get_dom_from_url(card_url)
    name_el = dom.select_one('h2 > a')
    set_el = dom.select_one('h5 > a')
    price_els = dom.select('.priceheader')
    card_name = name_el.get_text(strip=True) if name_el else None
    card_set = set_el.get_text(strip=True) if set_el else None
    price_values = [elem.get_text(strip=True) for elem in price_els]
    price_keys = ['avg']

    if len(price_values) > 1:
        price_keys.insert(0, 'low')
        price_keys.append('high')

    return {
        'name': unescape(card_name) if card_name else None,
        'set': unescape(card_set) if card_set else None,
        'link': card_url,
        'promo': len(price_keys) == 1,
        'prices' : dict(zip(price_keys, price_values))
    }



def get_card_price(name, card_set=None):
    if card_set is not None:
        card_url = card_url_from_set(name, card_set)
    else:
        card_url = card_url_from_name(name)

    return scrape_price(card_url)


