from unittest import result
import pandas as pd
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

BASE_URL = "https://www.imdb.com/"


def get_soup(url: str):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    webpage = urlopen(req, timeout=5).read()
    soup = BeautifulSoup(webpage, "html.parser")
    return soup


class IMDBSearch:
    def __init__(self, search_term: str) -> None:
        self.search_term = search_term
        self.search_soup = self.get_search_soup()
        self.hrefs = self.get_search_result_hrefs()

    def get_search_soup(self) -> BeautifulSoup:
        return get_soup(BASE_URL + "find/?q=" + self.search_term.replace(" ", "%20"))

    def get_search_result_hrefs(self) -> list[str]:
        return [result.get("href") for result in self.search_soup.findAll(class_="ipc-metadata-list-summary-item__t")]

    def get_search_results(self) -> None:
        self.search_results = []
        for result in self.search_soup.find_all(class_="ipc-metadata-list-summary-item__tc"):
            result_dict = {}
            result_dict["texts"] = []
            for element in result():
                if element.get("href"):
                    result_dict["href"] = BASE_URL + element.get("href")
                if element.text and element.text not in result_dict["texts"]:
                    result_dict["texts"].append(element.text)
            self.search_results.append(result_dict)

    def _get_listing_info(self, href_inx: int = 0) -> None:
        self.listing_soup = get_soup(self.hrefs[href_inx])
        self.get_title()
        self.get_type()
        self.get_rating()
        self.get_categories()

    def get_rating(self) -> None:
        self.rating = self.listing_soup.find(attrs={"data-testid": "hero-rating-bar__aggregate-rating__score"}).text

    def get_type(self) -> None:
        self.type = self.listing_soup.find(attrs={"data-testid": "hero-title-block__metadata"}).find("li").text

    def get_title(self) -> None:
        title = self.listing_soup.find(attrs={"data-testid": "hero-title-block__title"}).text
        if not title:
            title = self.listing_soup.find(attrs={"data-testid": "hero__pageTitle"}).text
        self.title = title

    def get_categories(self) -> None:
        self.categories = [element.text for element in self.listing_soup.findAll(attrs={"class": "ipc-chip__text"})]
        if "Back to top" in self.categories:
            self.categories.remove("Back to top")


class IMDBListing:
    def __init__(self, href: str) -> None:
        self.href = href
        self.url = BASE_URL + href
        components = self.href.split("/")
        self.imdb_id = components[2]
        self.imdb_type = components[1]
