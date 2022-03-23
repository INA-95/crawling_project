import abc
import random
import logging
import argparse
import requests
import os
import json
from typing import Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

parser = argparse.ArgumentParser()
parser.add_argument("--queries", type=str, default="안철수", help="The queries for searching news articles.")
parser.add_argument("--crawler", type=str, default="beautifulsoup", help="")
parser.add_argument("--count", type=int, default=40, help="The number of articles(default,max=4000).")
parser.add_argument("--save_path", type=str, default="articles.json")

def write_json(path, content):
    with open(path, 'w', encoding='utf-8') as w:
        json.dump(content, w)

def get_header():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }


class Bs4BaseCrawler(object):
    def get_soup_from_url(self, url:str) -> BeautifulSoup:
        with requests.get(url) as req:
            return BeautifulSoup(req.text, "lxml")

    @abc.abstractmethod
    def get_crawling_data(self, url:str, *args, **kwargs) -> str:
        raise NotImplementedError("Please implement your own code for parsing certain website here!")

class Bs4NewsCrawler(Bs4BaseCrawler):
    def get_crawling_data(self, url:str, count:int, keyword:str, headers:Optional[dict]=None):
        news = []
        for i in range(0, count, 10):
            query = url.format(query=keyword, start=i+1)
            soup = self.get_soup_from_url(query)
            news_list = soup.select_one('ul[class="list_news"]')
            news_sections = news_list.select('li[class="bx"]')
            for section in news_sections:
                news += [article.get('href') for article in section.select('a[class="info"]')]
                news += [article.get('href') for article in section.select('a[class="sub_txt"]')]
            if len(news) > count:
                break
        results = []
        for article in news[:count]:
            logging.info(f"crawling on ... {article}")
            with requests.get(article, headers=headers) as req:
                soup = BeautifulSoup(req.text, "lxml")
            headline = soup.select_one('div[class="article_info"] > h3').text
            contents = soup.select_one('div[id="articleBodyContents"]').text
            results.append({'headline': headline, 'contents': contents})
        return results

def main():
    args = parser.parse_args()
    base_url = "https://search.naver.com/search.naver?where=news&ie=utf8&query={query}&start={start}"
    crawler = Bs4NewsCrawler() if args.crawler == "beautifulsoup" else SeleniumNewsCrawler(chrome_driver=args.chrome_path, headless=False)
    headers = get_header()
    for query in args.queries.split(","):
        logging.info(f"**[KEYWORD] {query}")
        crawling_results = crawler.get_crawling_data(base_url,args.count, query,headers)
        path = os.path.join(os.path.dirname(args.save_path), query, os.path.basename(args.save_path))
        if not os.path.isdir(os.path.dirname(path)):
            os.mkdir(os.path.dirname(path))
        write_json(path, crawling_results)
        logging.info(f"{len(crawling_results)} articles saved successfully")


if __name__=='__main__':
    main()