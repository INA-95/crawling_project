import os.path
import time
import json
import logging
import argparse
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("--keywords", type=str, default="안철수")
parser.add_argument("--count", type=int, default=40, help="The number of articles(default,max=4000).")
parser.add_argument("--save_path", type=str, default="articles.json")


def write_json(path, content):
    with open(path, 'w', encoding='utf-8') as w:
        json.dump(content, w)


def main():
    args = parser.parse_args()
    url = "https://search.naver.com/search.naver?where=news&ie=utf8&query={keyword}&start={start}"
    for keyword in args.keywords.split(","):
        logging.info(f"**Keyword:{keyword}")
        news = []
        for i in range(0, args.count, 10):
            query = url.format(keyword=keyword, start=i+1)
            with requests.get(query) as req:
                soup = BeautifulSoup(req.text, "lxml")
            news_list = soup.select_one('ul[class="list_news"]')
            news_sections = news_list.select('li[class="bx"]')
            for section in news_sections:
                news += [article.get('href') for article in section.select('a[class="info"]')]
                news += [article.get('href') for article in section.select('a[class="sub_txt"]')]

            if len(news) > args.count:
                break

        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        }
        results = []
        for article in news[:args.count]:
            logging.info(f"crawling on ... {article}")
            with requests.get(article, headers=header) as req:
                soup = BeautifulSoup(req.text, "lxml")
            headline = soup.select_one('div[class="article_info"] > h3').text
            contents = soup.select_one('div[id="articleBodyContents"]').text
            results.append({'headline': headline, 'contents': contents})
        path = os.path.join(os.path.dirname(args.save_path),keyword, os.path.basename(args.save_path))
        if not os.path.isdir(os.path.dirname(path)):
            os.mkdir(os.path.dirname(path))
        write_json(path, results)
        logging.info(f"{len(results)} articles saved successfully")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()