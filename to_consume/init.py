from to_consume.watchlist import add_to_list
from to_consume.imdb import IMDBListing, IMDBSearch
from to_consume.movies_database import Listing

titles = [
    "alice in borderland",
    "all quiet on the western front",
    "Angry Boys",
    "Atlanta",
    "brave new world",
    "Clarkson's farm",
    "daredevil",
    "decoding Watson",
    "enemy villeneuve",
    "Epstein documentary",
    "euphoria ",
    "Gattaca",
    "Green Brook",
    "hurt locker",
    "i came by",
    "irobot",
    "Jessica jones",
    "le mans 66",
    "Margin Call",
    "Monsters vs. Aliens",
    "punisher",
    "Rising phoenix",
    "room",
    "smile",
    "spirited away",
    "ted lasso",
    "the clone wars",
    "the last of us",
    "the Martian",
    "the peripheral",
    "The playlist (spotify)",
    "the unbearable weight of massive talent",
    "the whale",
    "Wednesday",
    "when we left earth",
    "Andor",
    "Another earth",
    "Avatar: The Way of Water",
    "bullet train",
    "Dune",
    "everything everywhere all at once",
    "Fifa documentary",
    "glass onion",
    "Good Time",
    "In Bruges",
    "lost in translation",
    "peaky blinders",
    "severence",
    "storror rooftop culture",
    "tenet",
    "The bit player 2018",
    "the white lotus",
    "zero dark thirty",
    "Zodiac",
]

if __name__ == "__main__":
    for title in titles:
        try:
            search_res = IMDBSearch(title)
            if search_res.hrefs:
                first_res = IMDBListing(search_res.hrefs[0])
                listing = Listing(first_res.imdb_id)
                add_to_list(listing)
                print(f"Added {title}")
            else:
                print(f"Could not find {title}")
        except:
            print(f"Could not find {title}")
