import asyncio

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

options = webdriver.EdgeOptions()

async def get_article_url(page):
    driver = webdriver.Edge(options=options)
    driver.get(page)
    articles = driver.find_elements(By.CSS_SELECTOR, "article a")
    article_tasks = [None] * len(articles)
    for i, article in enumerate(articles):
        article = article.get_attribute("href")
        article_tasks[i - 1] = asyncio.create_task(parse_article(article))
        await article_tasks[i - 1]

    # await asyncio.gather(*article_tasks)
    driver.close()

async def parse_article(article):
    driver = webdriver.Edge(options=options)
    driver.get(article)
    title = driver.find_element(By.CSS_SELECTOR, "h1")
    price = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="current-price"]')
    print(f"{title.text} - {price.text}")
    imgs = driver.find_elements(By.CSS_SELECTOR, f'img[alt^="{title.text}"][src$=constrain]')

    img_set = set()
    for img in imgs:
        img_url = img.get_attribute("src")
        img_set.add(img_url)

    img_tasks = [None] * len(img_set)
    for i, img in enumerate(img_set):
        img_tasks[i - 1] = asyncio.create_task(download_img(img, f"{title.text} - {i}"))
        await img_tasks[i - 1]

    # await asyncio.gather(*img_tasks)
    driver.close()


async def download_img(img, title):
    response = requests.get(img)
    if response.status_code != 200:
        print(f"{img}下载失败，状态码为{response.status_code}")
        return

    with open(f"data\\{title}.png", "wb") as f:
        f.write(response.content)
    print(f"下载成功{img}")

async def main():
    n = 1
    page_tasks = [None] * n * 2
    for i in range(1, n + 1):
        women_url = f"https://www.asos.com/women/new-in/cat/?cid=27108&ctaref=15offnewcustomer%7Cglobalbanner%7Cww&page={i}"
        page_tasks[i - 1] = asyncio.create_task(get_article_url(women_url))
        men_url = f"https://www.asos.com/men/new-in/cat/?cid=27110&ctaref=15offnewcustomer%7Cglobalbanner%7Cmw&ew6325sf1=fail&page={i}"
        page_tasks[n + i - 1] = asyncio.create_task(get_article_url(men_url))

    await asyncio.gather(*page_tasks)

if __name__ == '__main__':
    asyncio.run(main())