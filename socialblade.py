from playwright.sync_api import sync_playwright
from playwright.sync_api import Page
from datetime import datetime
import logging
import csv
import re

# Logger
logging.basicConfig(level=logging.DEBUG)

def get_data(urls:list):
    """ Get data from pages """
    try:
        with sync_playwright() as p:
            # open browser
            browser = p.firefox.launch()
            page = browser.new_page()
            data = []
            for url in urls:                
                # access page
                page.goto(url, timeout=150000)
                page.wait_for_load_state()
                logging.info(f"Get {url}")
                page.wait_for_selector('body > div:nth-child(12) > div:nth-child(2) > div:nth-child(5)', timeout=150000)
                #page.wait_for_selector('body > div:nth-child(13) > div:nth-child(2) > div:nth-child(5)', timeout=90000)
                # parse content
                data += parse(page)
            # close browser
            browser.close()
    except Exception as err:
        logging.error(str(err))
        data = None
    return data

def parse(page:Page):
    """ Parse content """
    filtered_by = page.query_selector('#sort-by-current-title').inner_text().replace('Sorted by:', '').strip()
    #items = page.query_selector_all('body > div:nth-child(12) > div:nth-child(2) > div')
    items = page.query_selector_all('body > div:nth-child(13) > div:nth-child(2) > div')
    data = []
    for item in items[4:]:
        col = item.query_selector_all('div')
        row = [
            re.sub(r'^([0-9]{1,3})[snrdth]{2}$', '\\1', col[0].inner_text().strip()), # rank
            filtered_by.lower(), # filter
            col[1].inner_text().strip(), # grade
            col[2].query_selector('a').inner_text().strip(), # name
            col[2].query_selector('sup > i').get_attribute('title').replace('Category:','').strip(), # category
            col[3].inner_text().replace(',','').strip(), # uploads
            col[4].inner_text().strip(), # subscribers
            col[5].inner_text().replace(',','').strip(), # views
            'https://socialblade.com' + col[2].query_selector('a').get_attribute('href').strip(), # stats_url
            datetime.utcnow().isoformat(timespec='seconds') + '+00Z', # date_scraped
            'socialblade', # source
        ]
        data.append(row)
    return data

if __name__ == '__main__':
    urls = [
        'https://socialblade.com/youtube/top/country/id/mostsubscribed',
        'https://socialblade.com/youtube/top/country/id/mostviewed'
    ]
    data = []
    field = ['rank','filter','grade','name','category','uploads','subscribers','views','stats_url','date_scraped','source']
    data.append(field)
    data += get_data(urls)
    filename = 'socialblade_youtube_' + datetime.utcnow().strftime('%Y-%m-%d') + '.csv'
    path = 'result/' + filename
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    logging.info(f"Data saved to {path}")
