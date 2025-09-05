import os
from sqlalchemy import create_engine, text
import requests

API_KEY = "a8e97f74"
BASE_URL = "http://www.omdbapi.com/"
POSTER_URL = "http://img.omdbapi.com/"


DB_URL = "sqlite:///movies.db"

engine = create_engine(DB_URL)

with engine.begin() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT
        )
    """))


def fetch_movie_from_omdb(title):
    params = {"apikey": API_KEY, "t": title}
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception("OMDb API error")

    data = response.json()
    if data.get("Response") == "False":
        raise Exception(f"Movie not found: {title}")

    imdb_id = data.get("imdbID")

    return {
        "title": data["Title"],
        "year": int(data["Year"]),
        "rating": float(data["imdbRating"]) if data["imdbRating"] != "N/A" else 0.0,
        "poster_url": f"{POSTER_URL}?apikey={API_KEY}&i={imdb_id}" if imdb_id else ""
    }


def list_movies():
    """
    Returns a dictionary of movies in the format:
    {
        "Movie Title": {
            "year": 1999,
            "rating": 9.0
        },
        ...
    }
    """
    with engine.connect() as conn:
        result = conn.execute(text("SELECT title, year, rating, poster_url FROM movies"))
        movies = {}
        for row in result:
            movies[row.title] = {"year": row.year,
                                 "rating": row.rating,
                                 "poster_url": row.poster_url if row.poster_url else "No poster available."
                                 }
        return movies


def add_movie(title):
    try:
        movie_data = fetch_movie_from_omdb(title)

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT OR REPLACE INTO movies (title, year, rating, poster_url)
                    VALUES (:title, :year, :rating, :poster_url)
                """),
                movie_data
            )
        print(f"✅ '{movie_data['title']}' hinzugefügt.")
    except Exception as e:
        print("❌ Fehler beim Hinzufügen:", e)


def delete_movie(title):
    """
    Deletes a movie from the database by title.
    """
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM movies WHERE title = :title"),
            {"title": title}
        )
    print(f"Movie '{title}' deleted successfully.")


def update_movie(title, rating):
    """
    Updates the rating of a movie by title.
    """
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE movies SET rating = :rating WHERE title = :title"),
            {"title": title, "rating": rating}
        )
    print(f"Movie '{title}' updated successfully.")


def get_movie(title):
    """
    Fetch a single movie by title.
    Returns a dictionary with keys 'year' and 'rating', or None if not found.
    """
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT title, year, rating, poster_url FROM movies WHERE title = :title"),
            {"title": title}
        ).fetchone()
        if result:
            return {
                "year": result.year,
                "rating": result.rating,
                "poster_url":result.poster_url if result.poster_url else "No poster available."
            }
        return None


def generate_movies_html():
    """Erstellt eine index_template.html im _static-Ordner mit allen Filmen aus der Datenbank"""
    static_folder = "_static"
    os.makedirs(static_folder, exist_ok=True)  # Ordner erstellen falls nicht vorhanden

    html_file_path = os.path.join(static_folder, "index_template.html")

    # Template direkt als String
    template = """
    <html>
    <head>
        <title>__TEMPLATE_TITLE__</title>
        <link rel="stylesheet" href="style.css"/>
    </head>
    <body>
    <div class="list-movies-title">
        <h1>__TEMPLATE_TITLE__</h1>
    </div>
    <div>
        <ol class="movie-grid">
            __TEMPLATE_MOVIE_GRID__
        </ol>
    </div>
    </body>
    </html>
    """

    # Filme aus DB holen
    with engine.connect() as conn:
        result = conn.execute(text("SELECT title, year, rating, poster_url FROM movies"))
        movies = result.fetchall()

    # Movie Grid bauen
    movie_grid_html = ""
    for row in movies:
        movie_grid_html += f"""
        <li>
            <div class="movie">
                <img class="movie-poster" src="{row.poster_url}" alt="{row.title} poster"/>
                <div class="movie-title">{row.title}</div>
                <div class="movie-year">{row.year}</div>
                <div class="movie-rating">Rating: {row.rating}</div>
            </div>
        </li>
        """

    # Template ersetzen
    html = template.replace("__TEMPLATE_TITLE__", "My Movie App")
    html = html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)

    # Datei schreiben
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Website was generated successfully at {html_file_path}")