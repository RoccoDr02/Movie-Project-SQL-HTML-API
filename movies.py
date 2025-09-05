import random
import movie_storage_sql as storage

def list_movies():
    """ lists all movies with total rating, year and poster """
    movies = storage.list_movies()
    if not movies:
        print("No movies in your database.")
    else:
        print(f"{len(movies)} movies in total")
        for title, info in movies.items():
            print(f"{title} (Rating: {info['rating']}, Year: {info['year']}, Poster: {info['poster_url']})")


def add_movie():
    """ adds a movie by title using OMDb API """
    title = input("Which movie you want to add?: ").strip()
    try:
        storage.add_movie(title)
        print(f"Movie '{title}' added successfully from OMDb API.")
    except Exception as e:
        print("Error:", e)


def delete_movie():
    """ deletes a movie of your choice """
    title = input("Which movie you want to delete?: ")
    movies = storage.list_movies()
    if title in movies:
        storage.delete_movie(title)
        print(f"Movie '{title}' got deleted.")
    else:
        print("Movie isn't in database.")


def update_movie():
    """ updates the rating of a movie manually """
    title = input("Which movie you want to update: ")
    movies = storage.list_movies()
    if title not in movies:
        print("Movie not in database.")
        return

    try:
        rating = float(input("New rating (0-10): "))
        if 0 <= rating <= 10:
            storage.update_movie(title, rating)
            print(f"Movie '{title}' updated with new rating of {rating}.")
        else:
            print("Please give a rating from 0-10.")
    except ValueError:
        print("Invalid rating.")


def show_stats():
    """ shows best and worst movie and the average rating """
    movies = storage.list_movies()
    if not movies:
        print("No movies in your database.")
        return
    ratings = [info["rating"] for info in movies.values()]
    avg = sum(ratings) / len(ratings)
    highest = max(movies.items(), key=lambda item: item[1]["rating"])
    lowest = min(movies.items(), key=lambda item: item[1]["rating"])
    print(f"Average rating: {avg:.2f}")
    print(f"Best movie: {highest[0]} ({highest[1]['rating']})")
    print(f"Worst movie: {lowest[0]} ({lowest[1]['rating']})")


def random_movie():
    """ suggests you a random movie from movies """
    movies = storage.list_movies()
    if not movies:
        print("No movies in database.")
    else:
        title, info = random.choice(list(movies.items()))
        print(f"Random movie: {title} (Rating: {info['rating']}, Year: {info['year']}, Poster: {info['poster_url']})")


def search_movie():
    """ search for a movie in movies"""
    term = input("Enter part of movie name: ").lower()
    movies = storage.list_movies()
    found = False
    for title, info in movies.items():
        if term in title.lower():
            print(f"{title} (Rating: {info['rating']}, Year: {info['year']}, Poster: {info['poster_url']})")
            found = True
    if not found:
        print("No movie found.")


def sort_by_rating():
    """ sorting from highest to lowest and showing movies """
    movies = storage.list_movies()
    if not movies:
        print("No movies in database.")
        return
    sorted_list = sorted(movies.items(), key=lambda item: item[1]["rating"], reverse=True)
    print("Movies sorted by rating:")
    for title, info in sorted_list:
        print(f"{title} (Rating: {info['rating']}, Year: {info['year']})")


def sort_by_year():
    """ sort by year and ask how to sort (oldest or youngest first) """
    movies = storage.list_movies()
    if not movies:
        print("No movies in database.")
        return
    answer = input("Do you want the latest movies first? (Y/N): ").strip().lower()
    reverse = True if answer == "y" else False
    sorted_list = sorted(movies.items(), key=lambda item: item[1]["year"], reverse=reverse)
    print("Movies sorted by year:")
    for title, info in sorted_list:
        print(f"{title} (Year: {info['year']}, Rating: {info['rating']})")


def filter_movies():
    """ filter movies by minimum rating and/or year range """
    movies = storage.list_movies()
    print("Filter movies:")
    min_rating_str = input("Enter minimum rating (leave blank for no minimum rating): ").strip()
    start_year_str = input("Enter start year (leave blank for no start year): ").strip()
    end_year_str = input("Enter end year (leave blank for no end year): ").strip()

    try:
        min_rating = float(min_rating_str) if min_rating_str else None
    except ValueError:
        print("Invalid minimum rating. Ignoring this filter.")
        min_rating = None

    try:
        start_year = int(start_year_str) if start_year_str else None
    except ValueError:
        print("Invalid start year. Ignoring this filter.")
        start_year = None

    try:
        end_year = int(end_year_str) if end_year_str else None
    except ValueError:
        print("Invalid end year. Ignoring this filter.")
        end_year = None

    filtered = []
    for title, info in movies.items():
        if min_rating is not None and info["rating"] < min_rating:
            continue
        if start_year is not None and (info["year"] is None or info["year"] < start_year):
            continue
        if end_year is not None and (info["year"] is None or info["year"] > end_year):
            continue
        filtered.append((title, info))

    if not filtered:
        print("No movies matched the filter.")
    else:
        print(f"{len(filtered)} movies matched the filter:")
        for title, info in filtered:
            print(f"{title} (Rating: {info['rating']}, Year: {info['year']}, Poster: {info['poster_url']})")


def main():
    while True:
        print("""
********** My Movies Database **********

Menu:
0. Exit
1. List Movies
2. Add movie
3. Delete movie
4. Update movie
5. Stats
6. Random movie
7. Search movie
8. Movies sorted by rating
9. Movies sorted by year
10. Filter movies
11. Generate movies HTML page
        """)
        choice = input("Enter your option (0-11): ")
        print()
        if choice == "0":
            print("Bye!")
            break
        elif choice == "1":
            list_movies()
        elif choice == "2":
            add_movie()
        elif choice == "3":
            delete_movie()
        elif choice == "4":
            update_movie()
        elif choice == "5":
            show_stats()
        elif choice == "6":
            random_movie()
        elif choice == "7":
            search_movie()
        elif choice == "8":
            sort_by_rating()
        elif choice == "9":
            sort_by_year()
        elif choice == "10":
            filter_movies()
        elif choice == "11":
            storage.generate_movies_html()
        else:
            print("Invalid choice. Please choose from 0-11.")


if __name__ == "__main__":
    main()
