import streamlit as st
from to_consume.exceptions import ItemAlreadyInListError

from to_consume.imdb import IMDBListing, IMDBSearch
from to_consume.movies_database import MoviesDatabaseTitle


def searched_title_add(searched_title: str):
    scraped_title = IMDBSearch(searched_title)
    for href in scraped_title.hrefs:
        listing = IMDBListing(href)
        if listing.imdb_type == "title":
            st.write(f"[🔗]({listing.url})")
            listing_info = MoviesDatabaseTitle(listing.imdb_id)
            st.json(listing_info.title_info, expanded=False)
            if listing_info.image_url:
                st.image(listing_info.image_url, width=200)
            st.button("Add to list", key=listing.imdb_id, args=[listing.imdb_id], on_click=st_add_to_list)
            st.markdown("""---""")


def add_imdb_ids(imdb_ids: str) -> None:
    for imdb_id in imdb_ids.split(","):
        st_add_to_list(imdb_id)


def st_add_to_list(imdb_id: str) -> None:
    try:
        st.session_state.watchlist.add_to_watchlist(imdb_id)
    except ItemAlreadyInListError:
        st.warning(f"{imdb_id} already in the list")
        return None
    st.success(f"Added {imdb_id} to the watchlist")


def search_titles():
    imdb_ids = st.text_input("Add titles by their IMDb ID", help="Separate multiple IDs with commas")
    if imdb_ids:
        add_imdb_ids(imdb_ids)
    imdb_ids = ""
    searched_title = st.text_input("Search title", key="search_title", value="")
    if searched_title:
        searched_title_add(searched_title)
    searched_title = ""
