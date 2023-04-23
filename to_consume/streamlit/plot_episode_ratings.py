from to_consume.content import Title
import plotly.express as px
import streamlit as st


def plot_episode_ratings(title: Title):
    df = title.get_seasons_df()
    df.loc[df["imdb_rating"] == 0, "imdb_rating"] = None
    if not df.empty:
        fig = px.line(
            df,
            x=df.index,
            y="imdb_rating",
            color="season",
            title="Episode ratings",
            hover_data=["season", "episode", "imdb_rating", "imdb_ratings_count", "overview"],
            markers=True,
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)
