import os.path
import time
import json
import logging
import argparse
import requests
import re
import pandas as pd
from collections import defaultdict
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("--product_cnt", type=int, default=100)
parser.add_argument("--save_path", type=str, default="lush_korea_product_info.xlsx")


def main():
    args = parser.parse_args()
    url = 'https://www.lush.co.kr/goods/goods_list.php?page={page_num}&cateCd=001013'
    headers = {'User-Agent': 'Mozilla/5.0'}
    links, i = [], 1
    while len(links) < args.product_cnt:
        page_num = url.format(page_num=i)
        with requests.get(page_num) as req:
            soup = BeautifulSoup(req.text, 'lxml')
        product_lst = soup.select_one('ul[class="prdList"]')
        product_sections = product_lst.select('div[class="space"]')
        product_sections = product_sections[:(args.product_cnt - len(links))]
        hrefs = [product.select_one('div[class="txt"] > a') for product in product_sections]
        hrefs = [h.get("href").replace('../', 'https://www.lush.co.kr/') for h in hrefs if h]
        links += hrefs
        i+=1

    results = defaultdict(list)
    for link in links[:args.product_cnt]:
        with requests.get(link, headers=headers) as req:
            soup = BeautifulSoup(req.text, "lxml")

        product_name = soup.select_one('div[class="tit"] > h2')
        hash_tag = soup.select_one('div[class="hashtag"]')
        price = soup.select_one('li > div > strong')
        score = soup.select_one('div[class="average"] > div[class="score"]')

        product_name = product_name.text.strip() if product_name else ""
        hash_tag = hash_tag.text.strip() if hash_tag else ""
        price = price.text.strip() if price else ""
        score = score.text.strip() if score else ""

        price = int(price.replace("￦", "").replace(",", ""))
        hash_tag = ", ".join(["#"+tag.strip() for tag in hash_tag.split("#") if tag.strip()])
        score = float(score)

        results["product_name"].append(product_name)
        results["hash_tag"].append(hash_tag)
        results["price"].append(price)
        results["score"].append(score)

    pd.DataFrame(results).to_excel(args.save_path, index=False)
    logging.info(f"{len(results)} product info saved successfully")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
