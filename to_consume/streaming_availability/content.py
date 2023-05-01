from collections import defaultdict
from to_consume.base_content import BaseContent, BaseEpisode, BaseTitle
from to_consume.streaming_availability.api import get_streaming_availability_gb


class StreamingInfoContent(BaseContent):
    def __init__(self, imdb_id: str, responses: dict) -> None:
        super().__init__(imdb_id, responses)
        self.set_attr_from_dict_if_exists(responses, "title", ["sa_basic", "title"])
        self.set_attr_from_dict_if_exists(responses, "type", ["sa_basic", "type"])
        self.set_attr_from_dict_if_exists(responses, "overview", ["sa_basic", "overview"])
        self.set_attr_from_dict_if_exists(responses, "tagline", ["sa_basic", "tagline"])
        self.set_attr_from_dict_if_exists(responses, "image_url", ["sa_basic", "posterURLs", "original"])
        self.set_attr_from_dict_if_exists(responses, "avg_imdb_rating", ["sa_basic", "imdbRating"])
        self.set_attr_from_dict_if_exists(responses, "imdb_ratings_count", ["sa_basic", "imdbVoteCount"])
        self.set_attr_from_dict_if_exists(responses, "trailer_url", ["sa_basic", "youtubeTrailerVideoLink"])
        self.set_attr_from_dict_if_exists(
            responses, "streaming_links", ["sa_basic", "streamingInfo", "gb"], get_streaming_platform_link
        )


class StreamingInfoTitle(BaseTitle, StreamingInfoContent):
    def __init__(self, imdb_id: str, responses: dict) -> None:
        responses.update({"sa_basic": get_streaming_availability_gb(imdb_id)})
        super().__init__(imdb_id, responses)

    def append_episode_responses(self, episode_responses: defaultdict[dict]) -> None:
        super().append_episode_responses(episode_responses)
        responses = self.get_episode_responses_sa()
        for episode_imdb_id, response in responses.items():
            episode_responses[episode_imdb_id].update(response)

    def get_episode_responses_sa(self) -> defaultdict[dict]:
        response = get_streaming_availability_gb(self.imdb_id)
        episode_responses = defaultdict(dict)
        seasons = response.get("seasons", [])
        seasons = [] if seasons is None else seasons
        for season_number, season in enumerate(seasons, start=1):
            episodes = season.get("episodes", [])
            episodes = [] if episodes is None else episodes
            for episode_number, episode in enumerate(episodes, start=1):
                if episode.get("imdbId"):
                    episode_responses[episode["imdbId"]].update(
                        sa_basic=episode,
                        sa_season_ep_number={"season_number": season_number, "episode_number": episode_number},
                    )
        return episode_responses


class StreamingInfoEpisode(BaseEpisode, StreamingInfoContent):
    def __init__(self, imdb_id: str, responses: dict) -> None:
        super().__init__(imdb_id, responses)
        self.set_attr_from_dict_if_exists(responses, "sa_season_ep_number", ["sa_season_ep_number", "season_number"])
        self.set_attr_from_dict_if_exists(responses, "sa_season_ep_number", ["sa_season_ep_number", "episode_number"])


def get_streaming_platform_link(streaming_dict: dict) -> dict[str, str]:
    platform_links = {}
    for platform, info in streaming_dict.items():
        platform_links[platform] = info[0]["link"]
    return platform_links
