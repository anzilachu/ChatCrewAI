from django.shortcuts import render
import random
import requests
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
import openai
import os
from dotenv import load_dotenv
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect

load_dotenv()


api_key1 = os.getenv("API_KEY")



import random

def fetch_popular_series():
    api_key = api_key1
    discover_url = "https://api.themoviedb.org/3/discover/tv"
    characters_url = "https://api.themoviedb.org/3/tv/{}/credits"

    params = {
        'api_key': api_key,
        'with_genres': '18',  # Example genre ID for Drama
        'sort_by': 'vote_count.desc',  # Sort by vote count descending (most watched)
        'language': 'en-US',  # English language
        'vote_count.gte': '100',  # Filter out series with less than 100 votes
        'vote_average.gte': '6'  # Filter out series with less than 6 average rating
    }

    # Fetch web series data based on specified parameters
    response_series = requests.get(discover_url, params=params)
    series_data = response_series.json().get('results', [])

    # Fetch characters for each series
    series = []
    for series_item in series_data:  # Fetching 16 series
        series_id = series_item['id']  # Extract the series ID
        response_characters = requests.get(characters_url.format(series_id), params=params)
        characters_data = response_characters.json().get('cast', [])

        # Filter out characters without names
        characters_with_names = [character for character in characters_data if character.get('character')]

        # Randomly select up to four actors for the series
        selected_actors = random.sample(characters_with_names, min(4, len(characters_with_names)))
        actors = []
        for actor in selected_actors:
            actor_name = actor.get('character', '')
            actor_photo = f"https://image.tmdb.org/t/p/w500{actor['profile_path']}" if actor.get('profile_path') else None
            actors.append({'name': actor_name, 'photo': actor_photo})

        # Add the series ID to the series data
        series.append({
            'id': series_id,  # Include the series ID
            'title': series_item['name'],
            'image': f"https://image.tmdb.org/t/p/w500{series_item['poster_path']}" if series_item['poster_path'] else None,
            'characters': actors,
            'viewers': series_item['popularity'],  # Assuming 'popularity' represents the number of viewers
            'num_characters': len(characters_with_names)  # Number of characters with names in the series
        })

    return series



def fetch_popular_movies():
    api_key = api_key1
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1'
    response = requests.get(url)
    data = response.json()
    movies = []
    for item in data['results']:
        movie_id = item['id']  # Extract the movie ID
        
        # Fetch actors for the movie
        actors_response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=en-US')
        actors_data = actors_response.json()
        actors = actors_data['cast']
        
        # Filter out actors with no photo and exclude "Additional Voices"
        actors_with_photos = [actor for actor in actors if actor.get('profile_path') and "Additional Voices" not in actor.get('character', '')]

        # Add the movie ID to the movies list
        movies.append({
            'id': movie_id,  # Include the movie ID
            'title': item['title'],
            'image': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item['poster_path'] else None,
            'actors': actors_with_photos,
            'num_characters': len(actors_with_photos)  # Number of characters in the movie with available photos
        })
    return movies



def fetch_recent_movies():
    api_key = api_key1
    url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={api_key}&language=en-US&page=1'
    response = requests.get(url)
    data = response.json()
    movies = []
    for item in data['results']:
        movie_id = item['id']  # Extract the movie ID
        
        # Fetch actors for the movie
        actors_response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=en-US')
        actors_data = actors_response.json()
        actors = actors_data['cast']
        
        # Filter out actors with no photo
        actors_with_photos = [actor for actor in actors if actor.get('profile_path')]

        # Add the movie ID to the movies list
        movies.append({
            'id': movie_id,  # Include the movie ID
            'title': item['title'],
            'thumbnail': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item['poster_path'] else None,
            'viewers': item['popularity'],  # Assuming 'popularity' represents the number of viewers
            'num_characters': len(actors_with_photos)  # Number of characters in the movie with available photos
        })
    return movies



def fetch_actors(media_type, media_id):
    api_key = api_key1
    url = f'https://api.themoviedb.org/3/{media_type}/{media_id}/credits?api_key={api_key}&language=en-US'
    response = requests.get(url)
    data = response.json()
    actors = []
    for actor in data['cast'][:5]:
        actors.append({
            'name': actor['name'],
            'photo': f"https://image.tmdb.org/t/p/w500{actor['profile_path']}" if actor['profile_path'] else None
        })
    return actors



def fetch_recent_series():
    api_key = api_key1
    discover_url = "https://api.themoviedb.org/3/discover/tv"
    characters_url = "https://api.themoviedb.org/3/tv/{}/credits"

    params = {
        'api_key': api_key,
        'sort_by': 'first_air_date.desc',  # Sort by first air date descending (most recent)
        'language': 'en-US',
        'first_air_date.gte': '2022-01-01',  # Filter out series aired before 2022
        'vote_average.gte': '6'  # Filter out series with less than 6 average rating
    }

    # Fetch recent series data based on specified parameters
    response_series = requests.get(discover_url, params=params)
    series_data = response_series.json().get('results', [])

    # Extract details for each recent series
    recent_series = []
    for series_item in series_data:  # Limit to 8 recent series
        series_id = series_item['id']
        response_characters = requests.get(characters_url.format(series_id), params=params)
        characters_data = response_characters.json().get('cast', [])
        
        # Filter characters with names
        characters_with_names = [character for character in characters_data if character.get('character')]
        
        if characters_with_names:  # Check if there are characters with names for the series
            # Select one random actor from the series
            actor = random.choice(characters_with_names[:5]) if characters_with_names else None
            recent_series.append({
                'id': series_id,  # Include the series ID
                'title': series_item['name'],
                'thumbnail': f"https://image.tmdb.org/t/p/w500{series_item['poster_path']}" if series_item['poster_path'] else None,
                'actor_photo': f"https://image.tmdb.org/t/p/w500{actor['profile_path']}" if actor and actor.get('profile_path') else None,
                'viewers': series_item['popularity'],  # Add the 'popularity' attribute as 'viewers'
                'num_characters': len(characters_with_names)  # Number of characters with names in the series
            })

    return recent_series




def fetch_genres():
    api_key = api_key1  # Replace with your API key
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=en-US'
    response = requests.get(url)
    data = response.json()
    genres = [genre['name'] for genre in data['genres']]
    return genres


def select_random_popular_series(popular_series, num_series=2):
    """
    Selects a specified number of random popular series from the provided list.
    """
    return random.sample(popular_series, min(len(popular_series), num_series))

from django.core.cache import cache

def home(request):
    cache_key = 'home_data'  # Customize cache key if needed
    data = cache.get(cache_key)
    if data is None:
        # Fetch and process data
        popular_series = fetch_popular_series()

        # Get characters from the most popular series
        characters_from_popular_series = []
        for series in popular_series:
            for character in series['characters']:
                characters_from_popular_series.append({
                    'name': character['name'],
                    'photo': character['photo'],
                    'series_name': series['title']
                })

        # Randomly select characters
        random_characters = random.sample(characters_from_popular_series, min(len(characters_from_popular_series), 10))

        # Fetch recent series and their details
        recent_series = fetch_recent_series()

        # Fetch recent movies
        recent_movies = fetch_recent_movies()

        # Fetch popular movies
        popular_movies = fetch_popular_movies()

        # Select two random popular series
        random_popular_series = select_random_popular_series(popular_series, num_series=2)

        genres = fetch_genres()

        # Create context dictionary
        data = {
            'popular_series': popular_series,
            'random_characters': random_characters,
            'recent_series': recent_series,
            'recent_movies': recent_movies,
            'popular_movies': popular_movies,
            'random_popular_series': random_popular_series,
            'genres': genres,
        }
        cache.set(cache_key, data, timeout=60 * 5)  # Cache for 5 minutes

    context = data
    return render(request, 'home.html', context)






def popular_movies(request):
    movies = fetch_popular_movies()
    paginator = Paginator(movies, 16)  # 16 movies per page
    page_number = request.GET.get('page')
    try:
        movies_page = paginator.page(page_number)
    except PageNotAnInteger:
        movies_page = paginator.page(1)
    except EmptyPage:
        movies_page = paginator.page(paginator.num_pages)
    return render(request, 'popular_movies.html', {'movies': movies_page})

def popular_series(request):
    series = fetch_popular_series()
    paginator = Paginator(series, 16)  # 16 series per page
    page_number = request.GET.get('page')
    try:
        series_page = paginator.page(page_number)
    except PageNotAnInteger:
        series_page = paginator.page(1)
    except EmptyPage:
        series_page = paginator.page(paginator.num_pages)
    return render(request, 'popular_series.html', {'series': series_page})

def recent_movies(request):
    movies = fetch_recent_movies()
    paginator = Paginator(movies, 16)  # 16 movies per page
    page_number = request.GET.get('page')
    try:
        movies_page = paginator.page(page_number)
    except PageNotAnInteger:
        movies_page = paginator.page(1)
    except EmptyPage:
        movies_page = paginator.page(paginator.num_pages)
    return render(request, 'recent_movies.html', {'movies': movies_page})

def recent_series(request):
    series = fetch_recent_series()
    paginator = Paginator(series, 16)  # 16 series per page
    page_number = request.GET.get('page')
    try:
        series_page = paginator.page(page_number)
    except PageNotAnInteger:
        series_page = paginator.page(1)
    except EmptyPage:
        series_page = paginator.page(paginator.num_pages)
    return render(request, 'recent_series.html', {'series': series_page})


# Import necessary libraries


# Define cache timeout in seconds (e.g., 1 day)


# Function to fetch cast details for a series by ID
def fetch_cast_for_series(series_id):
    # Check if cast details are already cached
    cached_cast = cache.get(f"series_cast_{series_id}")
    if cached_cast:
        return cached_cast

    # If not cached, fetch cast details from the API
    url = f"https://api.themoviedb.org/3/tv/{series_id}/credits"
    params = {
        'api_key': api_key1,
        'language': 'en-US'
    }
    response = requests.get(url, params=params)
    cast_data = response.json().get('cast', [])

    # Cache the cast details
    cache.set(f"series_cast_{series_id}", cast_data,)

    return cast_data



def fetch_genre_id(genre_name):
    url = f"https://api.themoviedb.org/3/genre/movie/list"
    params = {
        'api_key': api_key1,
        'language': 'en-US'
    }
    response = requests.get(url, params=params)
    data = response.json()
    genres = data.get('genres', [])
    for genre in genres:
        if genre['name'].lower() == genre_name.lower():
            return genre['id']
    return None


def fetch_series_by_genre(genre_name):
    genre_id = fetch_genre_id(genre_name)
    if genre_id is None:
        return []

    url = f"https://api.themoviedb.org/3/discover/tv"
    params = {
        'api_key': api_key1,
        'with_genres': genre_id,
        'language': 'en-US',
        'vote_count.gte': '100',  # Filter out series with less than 100 votes
        'vote_average.gte': '6',  # Filter out series with less than 6 average rating
    }

    response = requests.get(url, params=params)
    series_data = response.json().get('results', [])

    series_list = []
    for series_item in series_data:
        series_id = series_item['id']
        cast_data = fetch_cast_for_series(series_id)

        series_details = {
            'title': series_item['name'],
            'overview': series_item['overview'],
            'poster_path': f"https://image.tmdb.org/t/p/w500{series_item['poster_path']}" if series_item['poster_path'] else None,
            'num_actors': len(cast_data),  # Number of actors
            'cast': cast_data  # Cast details
        }

        series_list.append(series_details)

    return series_list



def fetch_movies_by_genre(genre_name):
    genre_id = fetch_genre_id(genre_name)
    if genre_id is None:
        return []
    url = f"https://api.themoviedb.org/3/discover/movie"
    params = {
        'api_key': api_key1,
        'with_genres': genre_id,
        'language': 'en-US',
        'vote_count.gte': '100',  # Filter out movies with less than 100 votes
        'vote_average.gte': '6'  # Filter out movies with less than 6 average rating
    }
    response = requests.get(url, params=params)
    movies_data = response.json().get('results', [])
    
    movies_list = []
    for movie_item in movies_data:
        movie_details = {
            'title': movie_item['title'],
            'overview': movie_item['overview'],
            'poster_path': f"https://image.tmdb.org/t/p/w500{movie_item['poster_path']}" if movie_item['poster_path'] else None,
            # Get number of actors
            'num_actors': 0  # Initialize to 0
        }
        
        # Make additional API call to get cast details (assuming movie_id is available)
        cast_url = f"https://api.themoviedb.org/3/movie/{movie_item['id']}/credits"
        cast_response = requests.get(cast_url, params={'api_key': api_key1})
        cast_data = cast_response.json()
        
        # Extract number of actors (modify logic as needed)
        if cast_data.get('cast'):
            movie_details['num_actors'] = len(cast_data['cast'])
        
        movies_list.append(movie_details)
    
    return movies_list


def genre_detail(request, genre):
    series = fetch_series_by_genre(genre)
    movies = fetch_movies_by_genre(genre)

    context = {
        'genre': genre,
        'series': series,
        'movies': movies,
    }
    return render(request, 'genre_detail.html', context)



def fetch_movie_details(movie_id):
    api_key = api_key1
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=en-US'
    genres_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'

    response = requests.get(url)
    if response.status_code == 200:
        movie_details = response.json()
        movie_data = {
            'title': movie_details.get('title'),
            'overview': movie_details.get('overview'),
            'release_date': movie_details.get('release_date'),
            'poster_path': f"https://image.tmdb.org/t/p/w500{movie_details.get('poster_path')}" if movie_details.get('poster_path') else None,
        }

        # Fetch genres to determine if it's an animation movie
        genres_response = requests.get(genres_url)
        if genres_response.status_code == 200:
            genres_data = genres_response.json()
            genres_list = genres_data.get('genres', [])
            is_animation_movie = any(genre['name'] == 'Animation' for genre in genres_list)
            movie_data['is_animation_movie'] = is_animation_movie

        credits_response = requests.get(credits_url)
        if credits_response.status_code == 200:
            credits_data = credits_response.json()

            characters = []
            for character in credits_data.get('cast', []):
                character_name = character.get('character')
                if character_name and "Additional Voices" not in character_name:  # Ensure character has a name and exclude "Additional Voices"
                    character_name = character_name.split('(voice)')[0].strip()  # Remove "(voice)" from character name
                    character_gender = character.get('gender')  # Adding gender information
                    character_photo = f"https://image.tmdb.org/t/p/w500{character.get('profile_path')}" if character.get('profile_path') else None
                    characters.append({'name': character_name, 'photo': character_photo, 'gender': character_gender})
            movie_data['characters'] = characters

            return movie_data
        else:
            return None
    else:
        return None



def fetch_series_details(series_id):
    api_key = api_key1
    series_url = f'https://api.themoviedb.org/3/tv/{series_id}?api_key={api_key}&language=en-US'
    credits_url = f'https://api.themoviedb.org/3/tv/{series_id}/credits?api_key={api_key}&language=en-US'
    
    series_response = requests.get(series_url)
    series_data = series_response.json()
    
    credits_response = requests.get(credits_url)
    credits_data = credits_response.json()
    
    if series_response.status_code == 200 and credits_response.status_code == 200:
        title = series_data.get('name')
        thumbnail_url = f"https://image.tmdb.org/t/p/w500{series_data.get('poster_path')}" if series_data.get('poster_path') else None
        
        characters = []
        for character in credits_data.get('cast', []):
            character_name = character.get('character')
            if character_name:  # Ensure character has a name
                character_name = character_name.split('(voice)')[0].strip()  # Remove "(voice)" from character name
                character_gender = character.get('gender')  # Adding gender information
                character_photo = f"https://image.tmdb.org/t/p/w500{character.get('profile_path')}" if character.get('profile_path') else None
                characters.append({'name': character_name, 'photo': character_photo, 'gender': character_gender})
        
        series_details = {
            'title': title,
            'thumbnail': thumbnail_url,
            'characters': characters,
        }
        series_details['is_animation_series'] = series_data.get('genres', []) and any(genre['name'] == 'Animation' for genre in series_data['genres'])
        return series_details
    else:
        return None




def movie_detail(request, movie_id):

    movie_details = fetch_movie_details(movie_id)  # Implement this function to fetch movie details from TMDB API
    
    return render(request, 'movie_detail.html', {'movie': movie_details})


def series_detail(request, series_id):

    series_details = fetch_series_details(series_id)  # Implement this function to fetch series details from TMDB API
    
    return render(request, 'series_detail.html', {'series': series_details})


openai.api_key = os.getenv("OPENAI_API_KEY")

@login_required
def chat_with_character(request, show_name, character_name):
    character_name_from_query = request.GET.get('character_name')
    character_image_url = request.GET.get('character_image_url')
    character_gender = request.GET.get('character_gender')  # Retrieve character gender

    
    if character_name_from_query:
        character_name = character_name_from_query

    conversation = request.session.get(character_name, [])

    context = {
        'conversation': conversation,
        'show_name': show_name,  # Pass the show name to the template
        'character_name': character_name,
        'character_image_url': character_image_url,
        'character_gender': character_gender,  # Pass character gender to the template

    }

    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        ai_response = chat(user_input, show_name, character_name)

        user_message = {'user': 'You', 'text': user_input}
        conversation.append(user_message)
        conversation.append({'user': character_name, 'text': ai_response, 'character_name': character_name})

        request.session[character_name] = conversation

        return JsonResponse({'user_input': user_input, 'ai_response': ai_response})

    return render(request, 'chat.html', context)




def chat(user_input, show_name, character_name):
    """
    This function sends a message to the ChatGPT API and returns the response.

    Args:
        user_input: The user's message to the chatbot.
        show_name: The name of the selected show.
        character_name: The name of the selected character (which is often the actor's name).

    Returns:
        The chatbot's response to the user's message.
    """
    prompt = f"Hey there! You're chatting with {character_name.lower()} from {show_name.lower()}. I'm fully immersed in character mode. What's up? User: {user_input}\n{character_name}:"

    
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",  # Use the Davinci engine for a more nuanced response
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.6,
    )
    return response.choices[0].text.strip()


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to some page after login
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def user_payment(request):
    return render(request,'payment.html')

def about(request):
    return render(request,'about.html')
