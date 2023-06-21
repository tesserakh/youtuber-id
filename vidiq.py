from selectolax.parser import HTMLParser
from datetime import datetime
import requests
import csv


ROWS_SELECTOR = "tr[class*=cursor-pointer]"
COLS_SELECTOR = "td"


def scrape(url: str):
    client = requests.Session()
    response = client.get(url)
    if response.status_code == 200:
        data = parse(response.text)
        fields = ["Rank", "Channel", "Videos", "Subscribers", "Views"]
        data = [fields] + data
        return data
    else:
        print("ERROR: status code {}".format(response.status_code))
        return


def parse(txt: str) -> list:
    html = HTMLParser(txt)
    content_table = []
    for row in html.css(ROWS_SELECTOR):
        cols = row.css(COLS_SELECTOR)
        content_rows = []
        if len(cols) == 5:
            for col in cols:
                content_cell = col.text(strip=True)
                content_rows.append(content_cell)
            content_rows[0] = int(content_rows[0].replace("#", ""))
        content_table.append(content_rows)
    return content_table


def save(data: list, filepath: str) -> None:
    with open(filepath, "w") as fout:
        writer = csv.writer(fout)
        writer.writerows(data)


if __name__ == "__main__":
    filename = "result/vidiq_youtube_{}.csv".format(datetime.now().strftime("%Y-%m-%d"))
    url = "https://vidiq.com/youtube-stats/top/country/id/"
    data = scrape(url)
    if data is not None:
        save(data, filename)
        print("INFO: data saved from {}".format(url))
    else:
        print("WARNING: no data being saved")
