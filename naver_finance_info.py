
import requests
from bs4 import BeautifulSoup
import argparse
import pandas as pd
from collections import defaultdict
parser = argparse.ArgumentParser()
parser.add_argument("--item", type=str, default="035420", help="")
parser.add_argument("--date", type=str, default="2022.01.03", help="")
parser.add_argument("--outfile", type=str, default="result.csv", help="")


def main():
    items = ['날짜', "종가", "전일비", "시가", "고가", "저가", "거래량"]
    url = "https://finance.naver.com/item/sise_day.naver?code={code}&page={page}"
    by_target = False
    total, p = [], 1
    while not by_target:
        with requests.get(url.format(code=args.item, page=p), headers = {'User-Agent': 'Mozilla/5.0'}) as req:
            soup = BeautifulSoup(req.text, 'lxml')
        for item in soup.select('tr[onmouseover="mouseOver(this)"]'):
            data = [t.text for t in item.select("span")]
            # ['2022.02.15', None, '\n\t\t\t\t3,500\n\t\t\t\t', '325,000', '325,500', '316,000', '333,846']
            data = [t.strip().replace(",", "") if t else "" for t in data]
            total.append(data)
            if data[0] == args.date:
                by_target = True
                break
        p += 1
    # a = [['2022.02.15', '318500', '3500', '325000', '325500', '316000', '333846'], ['2022.02.14', '322000', '5500', '326000', '327000', '318000', '424845']]
    # zip(*a) >> [(1,'a'),(2,'b'), (3,'c')]
    '''
    date,last = list(zip(*total))
    total = {'날짜':date, "종가":last}
    '''
    total = {k: v for k, v in zip(items, zip(*total))}
    df = pd.DataFrame(total)
    df.to_csv(args.outfile, index=False, encoding='utf-8')


if __name__ == "__main__":
    args = parser.parse_args()
    main()