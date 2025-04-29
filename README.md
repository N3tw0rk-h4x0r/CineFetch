# 🎬 CineFetch

CineFetch is a simple GUI tool to fetch **movie metadata** from **IMDb** and **TMDB** links.  
Paste your movie links and get titles, genres, languages, cast, crew, posters, and more — automatically!

---

## ✨ Features

- ✅ Supports both **IMDb** and **TMDB** links
- ✅ Auto-pastes links line-by-line (no hitting enter needed)
- ✅ Downloads poster and backdrop images
- ✅ Saves clean formatted movie details in a text file
- ✅ Beautiful and easy-to-use GUI (no coding knowledge needed)

---

## 🚀 Installation

git clone https://github.com/N3tw0rk-h4x0r/CineFetch
cd CineFetch
pip install requests Pillow
python CineFetch.py
## Optional
pip install pyinstaller
pyinstaller --onefile --windowed CineFetch.py
dist/CineFetch.exe

## Troubleshooting
Problem	                 Solution
pyinstaller : command not found	Run pip install pyinstaller again.
Black console window opens with the app	Always use --windowed in pyinstaller to avoid it.
Pip not recognized	Add Python to PATH during installation.
EXE doesn't work on another PC	Make sure Visual C++ Redistributable is installed (common issue).
