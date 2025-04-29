import os
import re
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk

TMDB_API_KEY = "d5ea9071835d56e9b67dafea4152fa4b"

# Paths
desktop_path = Path.home() / "Desktop"
output_folder = desktop_path / "CineFetch_Movies"
output_folder.mkdir(exist_ok=True)
output_text_file = output_folder / "movie_details.txt"

language_map = {
    'en': 'English',
    'bn': 'Bengali',
    'hi': 'Hindi',
    'te': 'Telugu',
    'ta': 'Tamil',
    'ml': 'Malayalam',
    'kn': 'Kannada',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'pa': 'Punjabi',
    'ur': 'Urdu'
}

def extract_links(links):
    imdb_ids, tmdb_ids = [], []
    for line in links:
        line = line.strip()
        imdb_match = re.search(r'/title/(tt\d+)', line)
        tmdb_match = re.search(r'themoviedb\.org/movie/(\d+)', line)
        if imdb_match:
            imdb_ids.append(imdb_match.group(1))
        elif tmdb_match:
            tmdb_ids.append(tmdb_match.group(1))
    return imdb_ids, tmdb_ids

def get_movie_details_from_tmdb_id(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def format_duration(runtime):
    hours = runtime // 60
    minutes = runtime % 60
    return f"{hours}h {minutes}m" if runtime else "N/A"

def download_image(url, path):
    try:
        img = requests.get(url)
        with open(path, 'wb') as f:
            f.write(img.content)
    except:
        pass

def fetch_movies(imdb_ids, tmdb_ids):
    with open(output_text_file, 'w', encoding='utf-8') as text_file:
        all_ids = []

        # Handle IMDb
        for imdb_id in imdb_ids:
            find_url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"
            find_data = requests.get(find_url).json()
            movie_basic = find_data.get('movie_results', [])
            if not movie_basic:
                text_file.write(f"\n[❌] Movie not found for IMDb ID: {imdb_id}\n")
                continue
            tmdb_id = movie_basic[0]['id']
            all_ids.append(tmdb_id)

        # Add TMDB IDs directly
        all_ids += tmdb_ids

        # Fetch movie details
        for tmdb_id in all_ids:
            movie = get_movie_details_from_tmdb_id(tmdb_id)
            if not movie:
                text_file.write(f"\n[❌] Could not fetch full details for TMDB ID: {tmdb_id}\n")
                continue

            title = movie['title'].replace(" ", "_").replace("/", "_")
            year = movie.get('release_date', '')[:4]
            overview = movie.get('overview', 'No description.')
            rating = movie.get('vote_average', 'N/A')
            release_date = movie.get('release_date', 'N/A')
            content_rating = movie.get('adult', False)
            lang_code = movie.get('original_language', 'unknown').lower()
            language = language_map.get(lang_code, lang_code.upper())
            genres = ', '.join([g['name'] for g in movie.get('genres', [])]) or "N/A"
            runtime = format_duration(movie.get('runtime'))

            cast = movie.get('credits', {}).get('cast', [])
            actors = ', '.join([actor['name'] for actor in cast[:5]]) or "N/A"

            crew = movie.get('credits', {}).get('crew', [])
            directors = ', '.join([c['name'] for c in crew if c['job'] == 'Director']) or "N/A"

            poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None
            thumb_url = f"https://image.tmdb.org/t/p/w500{movie['backdrop_path']}" if movie.get('backdrop_path') else None

            poster_path = output_folder / f"{title}_poster.jpg"
            thumb_path = output_folder / f"{title}_thumb.jpg"

            if poster_url:
                download_image(poster_url, poster_path)
            if thumb_url:
                download_image(thumb_url, thumb_path)

            tmdb_link = f"https://www.themoviedb.org/movie/{tmdb_id}"

            text_file.write(
                f"""
=============================
🎬 Title: {movie['title']}
📆 Year: {year}
🔗 TMDB ID: {tmdb_id}
🔗 TMDB Link: {tmdb_link}
📅 Release Date: {release_date}
⏱️ Duration: {runtime}
👨‍💼 Directors: {directors}
🎭 Actors: {actors}
🈲 Content Rating: {'18+' if content_rating else 'PG'}
🌐 Language: {language}
🎬 Genres: {genres}
⭐ IMDb Rating: {rating}/10
📄 Description: {overview}
🖼️ Poster: {poster_path.name if poster_url else 'Not available'}
🖼️ Thumbnail: {thumb_path.name if thumb_url else 'Not available'}
=============================
""")

def on_fetch():
    raw_input = input_box.get("1.0", tk.END).strip().splitlines()
    imdb_ids, tmdb_ids = extract_links(raw_input)
    if not imdb_ids and not tmdb_ids:
        messagebox.showwarning("No Valid Links", "No valid IMDb or TMDB links found.")
        return
    fetch_movies(imdb_ids, tmdb_ids)
    messagebox.showinfo("Done", f"Movie data saved to:\n{output_text_file}")

def on_paste(event=None):
    try:
        clipboard = root.clipboard_get()
        for line in clipboard.splitlines():
            if line.strip():
                input_box.insert(tk.END, line.strip() + '\n')
        return "break"
    except:
        return

# GUI Setup
root = tk.Tk()
root.title("🎬 CineFetch - Movie Metadata Grabber")
root.geometry("760x660")
root.configure(bg="white")

style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook.Tab", background="#ddd", foreground="#111", padding=10)
style.configure("TFrame", background="white")
style.configure("TLabel", background="white", foreground="black")

notebook = ttk.Notebook(root)
main_tab = ttk.Frame(notebook)
credits_tab = ttk.Frame(notebook)
notebook.add(main_tab, text='📥 Fetch Movies')
notebook.add(credits_tab, text='📢 About & Credits')
notebook.pack(expand=1, fill='both')

tk.Label(main_tab, text="Paste IMDb or TMDB Links (one per line):", font=("Helvetica", 13, "bold"), fg="#2c3e50").pack(pady=10)
input_box = tk.Text(main_tab, height=18, width=85, bg="#f8f9fa", fg="black", insertbackground='black', font=("Consolas", 10), wrap="none")
input_box.pack(pady=10)
input_box.bind("<Control-v>", on_paste)
tk.Button(main_tab, text="🎯 Fetch & Save", command=on_fetch, bg="#2980b9", fg="white", font=("Helvetica", 12, "bold"), padx=20, pady=5).pack(pady=10)

# Credits Tab
tk.Label(credits_tab, text="CineFetch - Movie Metadata Grabber", font=("Helvetica", 16, "bold"), fg="#2c3e50").pack(pady=15)
tk.Label(credits_tab, text="Made with ❤️ by N3TW0RK-H4X0R", font=("Helvetica", 12)).pack(pady=5)
tk.Label(credits_tab, text="GitHub: https://github.com/N3tw0rk-h4x0r/CineFetch", fg="blue", cursor="hand2", font=("Helvetica", 11, "underline")).pack()
tk.Label(credits_tab, text="Instagram: https://www.instagram.com/n3tw0rk_h4x0r/", fg="purple", cursor="hand2", font=("Helvetica", 11, "underline")).pack()
tk.Label(credits_tab, text="Telegram: https://t.me/n3tw0rkh4x0rchannel", fg="green", cursor="hand2", font=("Helvetica", 11, "underline")).pack()
tk.Label(credits_tab, text="Website: https://shop.venomotpro.in/", fg="orange", cursor="hand2", font=("Helvetica", 11, "underline")).pack()

root.mainloop()
