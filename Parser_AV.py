from bs4 import BeautifulSoup
import asyncio
import aiohttp
import pandas as pd

pars_list = []


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def parser(html):
    soup = BeautifulSoup(html, 'lxml')

    links_ = soup.find_all('a', class_='listing-item__link')
    link_list = [('https://cars.av.by' + link.get('href')) for link in links_]

    bs_prices_byn = soup.find_all('div', class_='listing-item__price')
    price_byn_list = [price_byn.text for price_byn in bs_prices_byn]

    bs_prices_usd = soup.find_all('div', class_='listing-item__priceusd')
    price_usd_list = [price_usd.text.replace("≈", "").replace(" ", "").replace("$", "") for price_usd in bs_prices_usd]

    options_ = soup.find_all('div', class_='listing-item__params')
    options_list = [param.text for param in options_]

    pars_list.append([{'Ссылка': link_list[num],
                       'Цена в BYN': price_byn_list[num],
                       'Характеристики': options_list[num],
                       'Цена в USD': price_usd_list[num]
                       } for num in range(0, len(price_usd_list))])
    print(pars_list)


async def download(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        await parser(html)


urls = [f'https://cars.av.by/filter?brands[0][brand]=545&brands[0][model]=1980&brands[0][generation]=3808&brands[1]' \
        f'[brand]=545&brands[1][model]=1980&brands[1][generation]=3809&page={i}' for i in range(1, 3)]

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(download(url)) for url in urls]
tasks = asyncio.gather(*tasks)
loop.run_until_complete(tasks)

df = pd.DataFrame(pars_list)
df.to_csv('AV.csv', index=False)
df.to_json('AV.json')
