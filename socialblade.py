from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import csv
import re

# Logger
logging.basicConfig(level=logging.DEBUG)

def get_pagesource(url:str):
    """Get html page
    """
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector('body > div:nth-child(12) > div:nth-child(2)', timeout=10000)
            html = page.content()
            browser.close()
    except Exception as err:
        logging.error(str(err))
        html = None
    return html

def parse(html:str):
    """Parse html page
    """
    page = BeautifulSoup(html, 'html.parser')
    filtered_by = page.find('span', {'id':'sort-by-current-title'}).text.replace('Sorted by:', '').strip()
    items = page.select('body > div:nth-child(12) > div:nth-child(2) > div')
    data = []
    for item in items[4:]:
        col = item.find_all('div')
        row = [
            re.sub(r'^([0-9]{1,3})[snrdth]{2}$', '\\1', col[0].text.strip()), # rank
            filtered_by.lower(), # filter
            col[1].text.strip(), # grade
            col[2].find('a').text.strip(), # name
            col[2].find('sup').find('i')['title'].replace('Category:','').strip(), # category
            col[3].text.replace(',','').strip(), # uploads
            col[4].text.strip(), # subscribers
            col[5].text.replace(',','').strip(), # views
            'https://socialblade.com' + col[2].find('a')['href'], # stats_url
            datetime.utcnow().isoformat(timespec='seconds') + '+00Z', # date_scraped
            'socialblade', # source
        ]
        data.append(row)
    return data

if __name__ == '__main__':
    filename = 'socialblade_youtube_' + datetime.utcnow().strftime('%Y-%m-%d') + '.csv'
    urls = [
        'https://socialblade.com/youtube/top/country/id/mostsubscribed',
        'https://socialblade.com/youtube/top/country/id/mostviewed'
    ]
    data = []
    field = ['rank','filter','grade','name','category','uploads','subscribers','views','stats_url','date_scraped','source']
    data.append(field)
    for url in urls:
        res = get_pagesource(url)
        data += parse(res)
    with open('result/' + filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)
