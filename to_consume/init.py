import sys

sys.path.append("/home/neil/repos/to_consume")
from to_consume.watchlist import add_to_list
from to_consume.imdb import IMDBListing, IMDBSearch
from to_consume.movies_database import MoviesDatabaseBaseTitle

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

imdb_ids = [
    "tt0443706",
    "tt10795658",
    "tt0020629",
    "tt1596589",
    "tt4288182",
    "tt9814116",
    "tt10541088",
    "tt3322312",
    "tt9562568",
    "tt10814062",
    "tt8772296",
    "tt0119177",
    "tt0887912",
    "tt15083184",
    "tt0343818",
    "tt2357547",
    "tt1950186",
    "tt1615147",
    "tt0892782",
    "tt5675620",
    "tt17036612",
    "tt3170832",
    "tt15474916",
    "tt0245429",
    "tt10986410",
    "tt0458290",
    "tt3581920",
    "tt3659388",
    "tt8291284",
    "tt11291274",
    "tt13833688",
    "tt13443470",
    "tt1233514",
    "tt9253284",
    "tt1549572",
    "tt1630029",
    "tt12593682",
    "tt1160419",
    "tt6710474",
    "tt11564570",
    "tt4846232",
    "tt0780536",
    "tt0335266",
    "tt2442560",
    "tt6723592",
    "tt5015534",
    "tt13406094",
    "tt1790885",
    "tt6966692",
    "tt11280740",
]


def get_titles():
    for title in titles:
        try:
            search_res = IMDBSearch(title)
            if search_res.hrefs:
                first_res = IMDBListing(search_res.hrefs[0])
                listing = MoviesDatabaseBaseTitle(first_res.imdb_id)
                add_to_list(listing)
                print(f"Added {title}")
            else:
                print(f"Could not find {title}")
        except:
            print(f"Could not find {title}")


def get_imdb_ids():
    for imdb_id in imdb_ids:
        try:
            listing = MoviesDatabaseBaseTitle(imdb_id)
            add_to_list(listing.imdb_id)
            print(f"Added {imdb_id}")
        except Exception as e:
            print(f"falied to add {imdb_id}", e)


if __name__ == "__main__":
    get_imdb_ids()
