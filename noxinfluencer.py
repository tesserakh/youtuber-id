from bs4 import BeautifulSoup
from datetime import datetime
import requests
import logging
import csv

logging.basicConfig(level=logging.DEBUG)

def get_pagesource(url:str):
    """Get html page
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.noxinfluencer.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
    })
    res = session.get(url)
    return res

def parse(res):
    """Parse html page
    """
    page = BeautifulSoup(res.text, 'html.parser')
    table = page.find('div', {'id':'table-body'})
    url = res.url
    data = []
    for item in table.find_all('div', {'class':'table-line'}):
        # calculate stars
        rank_icon = item.find('span', {'class':'rank-score'})
        rank = 0
        for icon in rank_icon.find_all('i'):
            star = icon['class'][-1].split('-')[-1]
            if star == 'full':
                rank += 1
            elif star == 'half':
                rank += 0.5
            else:
                continue
        # build row by row
        row = [
            item.find('span', {'class':'rank-number'}).find('span').text.strip(), # rank
            url.split('/')[-1].split('sorted-by-')[-1].replace('-',' '), # filter
            rank, # grade
            item.find('span', {'class':'rank-desc'}).find('span').text.strip(), # name
            item.find('span', {'class':'rank-category'}).text.strip(), # category
            item.find('span', {'class':'rank-subs'}).find('span', {'class':'number'}).text.strip(), # subscribers
            item.find('span', {'class':'rank-avg-view'}).find('span', {'class':'number'}).text.strip(), # views avg weekly
            'https://www.noxinfluencer.com' + item.find('span', {'class':'rank-desc'}).find('a')['href'], # stats_url
            datetime.utcnow().isoformat(timespec='seconds') + '+00Z', # date_scraped
            'noxinfluencer', # source
        ]
        data.append(row)
    return data


if __name__ == '__main__':
    urls = [
        'https://www.noxinfluencer.com/youtube-channel-rank/top-100-id-all-youtuber-sorted-by-subs-weekly',
        'https://www.noxinfluencer.com/youtube-channel-rank/top-100-id-all-youtuber-sorted-by-avgview-weekly',
        'https://www.noxinfluencer.com/youtube-channel-rank/top-100-id-all-youtuber-sorted-by-noxscore-weekly',
        'https://www.noxinfluencer.com/youtube-channel-rank/top-100-id-all-youtuber-sorted-by-growth-weekly',
        'https://www.noxinfluencer.com/youtube-channel-rank/top-100-id-all-youtuber-sorted-by-views-monthly',
    ]
    data = []
    field = ['rank','filter','grade','name','category','subscribers','views','stats_url','date_scraped','source']
    data.append(field)
    for url in urls:
        res = get_pagesource(url)
        data += parse(res)

    filename = 'noxinfluencer_youtube_' + datetime.utcnow().strftime('%Y-%m-%d') + '.csv'
    filepath = 'result/' + filename
    with open(filepath, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)
        logging.info(f'Data saved to {filepath}')
