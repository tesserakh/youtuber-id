from datetime import datetime
import requests
import json
import csv


def get_data(session):
    sort = ['total_subscribers', 'total_video_views']
    user_input = []
    for item in sort:
        for page in range(0, 100, 25):
            params = {
                'sort_by': item, # total_subscribers, total_video_views
                'country': 'id',
                'platform': 'youtube',
                'limit': '25',
                'offset': str(page), # 0, 25, 50, 75
            }
            user_input.append(params)
    json_data = []
    for params in user_input:
        res = session.get('https://graphyrepo.com/api/v1/creators/leaderboard', params=params)
        results = json.loads(res.text)['results']
        count = int(params['offset'])
        for talent in results:
            count += 1
            talent.update({
                'ranking':count,
                'sort_by':params['sort_by'],
            })
            json_data.append(talent)
    return json_data

def parse(json_data):
    data = []
    for col in json_data:
        row = [
            col['ranking'], # rank
            col['sort_by'].replace('_',' ').replace('total','').strip(), # filter
            col['repometer_score'], # grade
            col['name'], # name
            col['quality_score'], # quality
            col['virality_score'], # virality
            col['frequency_score'], # frequency
            col['youtube_details']['total_subscribers'], # subscribers
            col['youtube_details']['total_video_views'], # views
            'https://graphyrepo.com/p/' + col['username'], # stats_url
            datetime.utcnow().isoformat(timespec='seconds') + '+00Z', # date_scraped
            'graphyrepo', # source
        ]
        data.append(row)
    return data

def build_data():
    """Build data and save to a CSV file"""
    http = requests.Session()
    http.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://graphyrepo.com/top/id/categories/youtube',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
    })

    field = ['rank','filter','grade','name','quality','virality','frequency','subscribers','views','stats_url','date_scraped','source']
    result = get_data(session=http)
    data = parse(json_data=result)

    filename = 'graphyrepo_youtube_' + datetime.utcnow().strftime('%Y-%m-%d') + '.csv'
    with open('result/' + filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(field)
        writer.writerows(data)

if __name__ == '__main__':
    build_data()
