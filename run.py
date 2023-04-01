from pandas import DataFrame, read_csv
import streamlit as st
from to_consume.imdb import IMDBSearch
from annotated_text import annotated_text

st.set_page_config(layout="wide")
df = read_csv("to_watch.csv").sort_values(["watched", "title"])

with st.sidebar:
    search_title = st.text_input("Search title")
    if search_title:
        scraped_title = IMDBSearch(search_title)
        for result in scraped_title.search_results:
            link = result.get("href")
            st.write(f"[🔗]({link})")
            texts = [(text,) for text in result.get("texts")]
            annotated_text(*texts)
            st.button("Add to list", key=link)

st.experimental_data_editor(
    df.set_index("title"),
    use_container_width=True,
    num_rows="static",
)


def round_pandas(s, n):
    return (s / n).round() * n


st.bar_chart(round_pandas(df.rating, 5).value_counts())
st.bar_chart(
    df[["watched", "where"]]
    .value_counts()
    .to_frame("n")
    .reset_index()
    .pivot(index="where", columns="watched", values="n")
    .fillna(0)
    .astype(int),
)
