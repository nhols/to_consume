import streamlit as st
from to_consume.exceptions import ItemAlreadyInListError

from to_consume.imdb import IMDBListing, IMDBSearch
from to_consume.movies_db.content import MoviesDbTitle


def search_add_titles():
    add_by_id()
    search_titles_to_add()


def add_by_id():
    with st.form("add_titles", clear_on_submit=True):
        imdb_ids = st.text_input(
            "Add titles", placeholder="Add multiple titles by their IMDb IDs", help="Separate multiple IDs with commas"
        )
        add_ids_clicked = st.form_submit_button("Add titles")
        if add_ids_clicked:
            add_imdb_ids(imdb_ids)


def search_titles_to_add():
    with st.form("search_titles", clear_on_submit=True):
        searched_title = st.text_input("Search title", placeholder="Search IMDb for a title")
        search_titles_clicked = st.form_submit_button("Search titles")
    if search_titles_clicked:
        searched_title_add(searched_title)


def searched_title_add(searched_title: str):
    scraped_title = IMDBSearch(searched_title)
    for href in scraped_title.hrefs:
        searched_title_card(href)


def searched_title_card(title_href: str):
    listing = IMDBListing(title_href)
    if listing.imdb_type == "title":
        mdb_title = MoviesDbTitle(listing.imdb_id)
        st.markdown(f"**Title: {mdb_title.title}**")
        st.markdown(f"type: {mdb_title.type}")
        st.markdown(f"IMDB link: [🔗]({listing.url})")
        if mdb_title.image_url:
            st.image(mdb_title.image_url, width=200)
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
