import streamlit as st

from to_consume.streamlit.plot_episode_ratings import plot_episode_ratings


def display_title(selected_imdb_id):
    if selected_imdb_id:
        selected_title = st.session_state.watchlist.watchlist[selected_imdb_id]
        title = selected_title["title"]
        plot_episode_ratings(title)
        st.title(title.title)
        st.subheader(title.type)
        col1, col2 = st.columns(2)
        with col1:
            if title.image_url:
                st.image(title.image_url, width=400)
        with col2:
            safe_write(title, "overview")
            safe_write(title, "tagline")
            st.markdown("""---""")
            for platform, link in title.streaming_links.items():
                st.write(f"[{platform}]({link})")
            st.markdown("""---""")
            st.write(f"[IMDb]({title.imdb_url})")
            st.write(f"[Just Watch]({title.just_watch_url})")
            st.write(f"[UNOGS]({title.unogs_url})")
            st.markdown("""---""")
            st.write(f"Average IMDb rating: {title.avg_imdb_rating}⭐ ({title.imdb_ratings_count} ratings)")
            st.markdown("""---""")
            watched = st.checkbox("Watched", value=selected_title["watched"])
            rating = st.slider(
                "Rating", value=selected_title["rating"], min_value=1, max_value=100, disabled=not watched
            )
            st.button(label="Update status", args=[selected_imdb_id, watched, rating], on_click=st_update_watchlist)
            st.markdown("""---""")
            st.button("Remove from list", args=[selected_imdb_id], on_click=st_delete_from_list)
        try:
            st.video(title.trailer_url)
        except:
            pass


def safe_write(obj, attr):
    value = getattr(obj, attr, "")
    st.write(value)


def st_update_watchlist(imdb_id: str, watched: bool, rating: int) -> None:
    st.session_state.watchlist.update_watchlist(imdb_id, watched, rating)
    st.success(f"Updated title {imdb_id}")


def st_delete_from_list(imdb_id: str) -> None:
    st.session_state.watchlist.delete_from_watchlist(imdb_id)
    st.success(f"Deleted title {imdb_id}")
