from pandas import DataFrame
from to_consume.content import Episode, Title
import plotly.express as px
import streamlit as st


def get_episode_plot_data(episode: Episode) -> dict:
    return {
        "season_number": episode.season_number,
        "episode_number": episode.episode_number,
        "title": episode.title,
        "overview": episode.overview,
        "date_released": str(episode.date_released),
        "imdb_rating": episode.avg_imdb_rating,
        "imdb_rating_count": episode.imdb_ratings_count,
    }


def plot_episode_ratings(title: Title):
    episode_data = [get_episode_plot_data(episode) for episode in title.episodes]
    if not episode_data:
        return None
    df = DataFrame.from_records(episode_data).sort_values(["season_number", "episode_number"]).reset_index(drop=True)
    df.loc[df["imdb_rating"] == 0, "imdb_rating"] = None
    if not df.empty:
        fig = px.line(
            df,
            x=df.index,
            y="imdb_rating",
            color="season_number",
            title="Episode ratings",
            hover_data=[
                "season_number",
                "episode_number",
                "title",
                "date_released",
                "imdb_rating",
                "imdb_rating_count",
                "overview",
            ],
            markers=True,
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)
