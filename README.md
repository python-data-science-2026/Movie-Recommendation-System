# Movie Recommendation System

The goal of this project is to develop a personalized movie recommendation system that helps users discover new films.

## Group members 

- Mario González
- Dario Walker
- Harsh Nayak
- Moïse Meka

## Installation  

### Clone the repository 

```bash
git clone https://github.com/python-data-science-2026/Movie-Recommendation-System.git

cd Movie-Recommendation-System
```

### Set up environment 

Follow the installation [link](http://github.com/pyenv/pyenv) to install pyenv if not yet installed.
Then run the commands bellow :

```bash
pyenv install 3.12
pyenv local 3.12

python --version
```

Follow the installation [link](https://python-poetry.org/docs/#installing-with-the-official-installer) to install poetry if not yet installed 

```bash
poetry install 
```

## Run the application  
```bash
#poetry run python -m streamlit run main.py
poetry run python main.py
```

## Example 

```
=== Movie Recommendation System ===
1. Register
2. Login
0. Exit
Choose an option: 2

--- Login ---
Username: mmeka
Password: Qwerty@1234
Welcome, mmeka!

=== Movie Recommendation System === [mmeka]
1. Add watched movie
2. Set preferences
3. Show watched movies
4. Show preferences
5. Get recommendations
0. Logout

Choose an option: 1

--- Add Watched Movie ---
Movie title: Kirikou and the Sorceress
Release date (YYYY-MM-DD): 1998-01-01
Genres (comma separated): Adventure, Fantasy
Actors (comma separated):: Doudou Gueye Thiaw, Awa Sene Sarr, Maimouna N'Diaye, Robert Liensol
Watch date (YYYY-MM-DD): 2025-12-10
Rating (1 to 5): 4
Comment (optional): Amazing
Movie added successfully.

Choose an option: 2

--- Set Preferences ---
Favorite genres (comma separated): Documentary, History, Music
Rate each genre between 1 and 5 (comma separated): 2
Favorite actors (comma separated): 
Rate each actor between 1 and 5 (comma separated): 
Preferences saved successfully.

Choose an option: 3

--- Your Watched Movies ---
watch_date  rating                                            title release_date
2013-10-18     3.0                            Safety Not Guaranteed   2012-06-08
2023-09-10     1.0                               Sex With Strangers   2002-02-22
2020-07-21     4.0                          The Secret Life of Pets   2016-06-18
2009-01-03     3.0                                     Analyze This   1999-03-05
2015-01-09     2.0                           Straight Outta Compton   2015-08-13
2018-09-29     4.0                                       Spider-Man   2002-05-01
2025-01-21     4.0                                        The Yards   2000-04-27
2014-12-19     2.0                                        Admission   2013-03-21

Choose an option: 4

--- Your Preferences ---
Favourite genres:
     genre_name  genre_rating
       Thriller             3
      Animation             4
            War             1
            War             4
Science Fiction             4
      Adventure             4
        Mystery             2

Favourite actors:
 actor_full_name  actor_rating actor_date_of_birth
    Ron Crawford             1          1990-05-11
      Method Man             4          2009-11-11
     Goldie Hawn             1          1986-08-12
     Kerry Bishé             2          1977-10-10
    Faye Dunaway             2          2008-08-05
     Glenn Close             3          2003-03-02
Stephen Spinella             1          2001-09-07

Choose an option: 5

--- Movie Recommendations ---
Based on your history, you might like:
                                   title release_date
Harry Potter and the Prisoner of Azkaban   2004-05-31
                       Anna and the King   1999-12-16
                            Last Holiday   2006-01-13
            The Greatest Story Ever Told   1965-02-15
                   To Kill a Mockingbird   1962-12-25

```