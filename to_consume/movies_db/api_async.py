from typing import Any
import aiohttp
import asyncio
from to_consume.movies_db.api import HEADERS, BASE_URL

#TODO cache
def get_title_info_async(imdb_ids: list[str]):
    urls = [BASE_URL + f"titles/{imdb_id}" for imdb_id in imdb_ids]
    responses = asyncio.run(main(urls))
    return [response["results"] for response in responses]

def get_title_rating_async(imdb_ids: list[str]):
    urls = [BASE_URL + f"titles/{imdb_id}/ratings" for imdb_id in imdb_ids]
    responses = asyncio.run(main(urls))
    return [response["results"] for response in responses]

def get_movies_db_urls_async(urls:list[str]) -> list[Any]:
    responses = asyncio.run(main(urls))
    return [response["results"] for response in responses]

async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [get_movies_database_data_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

async def get_movies_database_data_async(session, url: str):
    async with session.get(url, headers=HEADERS) as response:
        return await response.json()