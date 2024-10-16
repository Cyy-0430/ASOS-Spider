import requests
import asyncio
from bs4 import BeautifulSoup
from requests import ReadTimeout, Response
from soupsieve import SelectorSyntaxError
from urllib3.exceptions import ReadTimeoutError

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

session = requests.session()

async def get(url):
    try:
        resp =  await asyncio.to_thread(session.get, url, headers=headers)
    except ReadTimeout and ReadTimeoutError:
        resp = Response()
        resp.status_code = 000
    return resp

async def parse_page(page):
    print(f"正在同时解析第{page}页，请稍后")
    url = f"https://www.asos.com/women/sale/cat/?cid=7046&ctaref=hp%7Cww%7Cpromo%7Cbanner%7C1%7Cedit%7Csale&page={page}"
    # resp = requests.get(url, headers=headers)
    resp = await get(url)

    if resp.status_code != 200:
        print(f"第{page}页解析失败, 状态码{resp.status_code}")
        return

    soup = BeautifulSoup(resp.text, "lxml")
    articles = soup.find_all("article")

    article_tasks = [None] * len(articles)
    for i, article in enumerate(articles):
        article_page = article.a["href"]
        article_tasks[i] = asyncio.create_task(parse_article(article_page))

    await asyncio.gather(*article_tasks)
    print(f"第{page}页解析完成")


async def parse_article(article_page):
    # resp = requests.get(article_page, headers=headers)
    resp = await get(article_page)

    if resp.status_code != 200:
        print(f"解析失败，状态码{resp.status_code} {article_page}")
        return
    print(f"article_page解析成功 {article_page}")
    soup = BeautifulSoup(resp.text, "lxml")
    title = soup.h1.text
    title = str(title)
    if "/" in title:
        return
    try:
        image_urls = soup.select(f'img[alt^="{title}"][src$=constrain]')
    except SelectorSyntaxError:
        return
    image_tasks = [None] * len(image_urls)
    image_urls = [x["src"] for x in image_urls]
    for i, image_url in enumerate(image_urls):
        # image = requests.get(image_url, headers=headers).content
        image_tasks[i] = get(image_url)

    images = await asyncio.gather(*image_tasks)

    for i, image in enumerate(images):
        if image.status_code != 200:
            continue
        image = image.content

        with open(f"data/{title} - {i}.png", "wb") as f:
            f.write(image)

        print(f"成功下载 {title} - {image_urls[i]}")


async def main():
    n = 100
    page_tasks = [None] * n
    for i in range(1, n + 1):
        page_tasks[i - 1] = asyncio.create_task(parse_page(i))
        await page_tasks[i - 1]

    # await asyncio.gather(*page_tasks)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("程序退出")
        quit()
