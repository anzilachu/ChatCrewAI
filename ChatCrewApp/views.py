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
from django.db import IntegrityError
from django.contrib import messages
from . models import *
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import string
from django.shortcuts import render
from .utils import decrypt_params, encrypt, encrypt_params, get_converted_amount
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max


load_dotenv()


api_key1 = os.getenv("API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")



import random
import requests
import random
from datetime import datetime

def fetch_popular_series():
    api_key = api_key1
    discover_url = "https://api.themoviedb.org/3/discover/tv"
    characters_url = "https://api.themoviedb.org/3/tv/{}/credits"
    actor_details_url = "https://api.themoviedb.org/3/person/{}"

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
    series_data = response_series.json().get('results', [])[:8]  # Limit to the first 8 series

    # Fetch characters for each series
    series = []
    for series_item in series_data:
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
            actor_id = actor.get('id')

            # Fetch actor details to get the birthdate
            actor_details_response = requests.get(actor_details_url.format(actor_id), params={'api_key': api_key})
            actor_details = actor_details_response.json()
            birthdate = actor_details.get('birthday')
            age = None
            if birthdate:
                birthdate_date = datetime.strptime(birthdate, '%Y-%m-%d')
                age = (datetime.now() - birthdate_date).days // 365

            actors.append({'name': actor_name, 'photo': actor_photo, 'age': age})

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



def calculate_age(birthdate):
    if birthdate:
        birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
        today = datetime.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return None



def fetch_popular_movies():
    api_key = api_key1
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1'
    response = requests.get(url)
    data = response.json()
    movies_data = data['results'][:8]  # Limit to the first 8 movies

    movies = []
    for item in movies_data:
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



def select_random_popular_series(popular_series, num_series=2):
    """
    Selects a specified number of random popular series from the provided list.
    """
    return random.sample(popular_series, min(len(popular_series), num_series))

from django.core.cache import cache

from django.shortcuts import render
from .utils import encrypt

from .utils import encrypt  # Ensure this import is at the top of your views.py

def home(request):
    cache_key = 'home_data'
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
                    'age': character['age'],
                    'series_name': series['title'],
                    'series_id': series['id']  # Added series ID
                })

        # Randomly select characters
        random_characters = random.sample(characters_from_popular_series, min(len(characters_from_popular_series), 6))

        # Encrypt character names, series names, and photo URLs
        for character in random_characters:
            character['encrypted_name'] = encrypt(character['name'])
            character['encrypted_series_name'] = encrypt(character['series_name'])
            character['encrypted_photo'] = encrypt(character['photo'])

        # Fetch recent series and their details
        recent_series = fetch_recent_series()

        # Fetch recent movies
        recent_movies = fetch_recent_movies()

        # Fetch popular movies
        popular_movies = fetch_popular_movies()

        # Select two random popular series
        random_popular_series = select_random_popular_series(popular_series, num_series=2)



        for series in popular_series:
            series['encrypted_id'] = encrypt(str(series['id']))
            series['encrypted_title'] = encrypt(series['title'])  # Encrypt title

        for movie in popular_movies:
            movie['encrypted_id'] = encrypt(str(movie['id']))

        # Create context dictionary
        data = {
            'popular_series': popular_series,
            'random_characters': random_characters,
            'popular_movies': popular_movies,
            'random_popular_series': random_popular_series,
        }
        cache.set(cache_key, data, timeout=60 * 100)  # Cache for 60 minutes

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
            actors = []  # List to store actors' details
            for character in credits_data.get('cast', []):
                character_name = character.get('character')
                if character_name and "Additional Voices" not in character_name:  # Ensure character has a name and exclude "Additional Voices"
                    character_name = character_name.split('(voice)')[0].strip()  # Remove "(voice)" from character name
                    character_gender = character.get('gender')  # Adding gender information
                    character_photo = f"https://image.tmdb.org/t/p/w500{character.get('profile_path')}" if character.get('profile_path') else None
                    characters.append({'name': character_name, 'photo': character_photo, 'gender': character_gender})
                    
                    actor_name = character.get('name')
                    if actor_name:
                        actors.append({'name': actor_name, 'photo': character_photo, 'gender': character_gender})

            movie_data['characters'] = characters
            movie_data['actors'] = actors  # Add actors to movie_data

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
        actors = []  # New list for actors
        for character in credits_data.get('cast', []):
            character_name = character.get('character')
            actor_name = character.get('name')  # Get actor name
            if character_name:  # Ensure character has a name
                character_name = character_name.split('(voice)')[0].strip()  # Remove "(voice)" from character name
                character_gender = character.get('gender')  # Adding gender information
                character_photo = f"https://image.tmdb.org/t/p/w500{character.get('profile_path')}" if character.get('profile_path') else None
                characters.append({'name': character_name, 'photo': character_photo, 'gender': character_gender})
                actors.append({'name': actor_name, 'photo': character_photo})  # Add actor details

        series_details = {
            'title': title,
            'thumbnail': thumbnail_url,
            'characters': characters,
            'actors': actors,  # Include actors in the series details
        }
        series_details['is_animation_series'] = series_data.get('genres', []) and any(genre['name'] == 'Animation' for genre in series_data['genres'])
        return series_details
    else:
        return None


from .utils import encrypt, decrypt  # Ensure this import is at the top of your views.py


def movie_detail(request, encrypted_movie_id):
    try:
        movie_id = decrypt(encrypted_movie_id)
    except InvalidToken:
        return HttpResponseBadRequest("Invalid movie ID token")

    movie_details = fetch_movie_details(movie_id)

    if movie_details.get('title'):
        encrypted_show_name = encrypt(movie_details['title'])
        movie_details['encrypted_show_name'] = encrypted_show_name

    if movie_details.get('poster_path'):
        movie_details['encrypted_poster_path'] = encrypt(movie_details['poster_path'])

    # Encrypt character names and images
    for character in movie_details.get('characters', []):
        if character.get('name'):
            character['encrypted_name'] = encrypt(character['name'])
        if character.get('photo'):
            character['encrypted_photo'] = encrypt(character['photo'])

    # Encrypt actor names and images
    for actor in movie_details.get('actors', []):
        if actor.get('name'):
            actor['encrypted_name'] = encrypt(actor['name'])
        if actor.get('photo'):
            actor['encrypted_photo'] = encrypt(actor['photo'])

    return render(request, 'movie_detail.html', {'movie': movie_details})


# views.py
from .utils import encrypt, decrypt

def series_detail(request, encrypted_series_id):
    series_id = decrypt(encrypted_series_id)
    series_details = fetch_series_details(series_id)

    if series_details.get('title'):
        encrypted_show_name = encrypt(series_details['title'])
        series_details['encrypted_show_name'] = encrypted_show_name

    if series_details.get('thumbnail'):
        series_details['encrypted_thumbnail'] = encrypt(series_details['thumbnail'])

    # Encrypt character names and images
    for character in series_details.get('characters', []):
        if character.get('name'):
            character['encrypted_name'] = encrypt(character['name'])
        if character.get('photo'):
            character['encrypted_photo'] = encrypt(character['photo'])
    
    # Encrypt actor names and images
    for actor in series_details.get('actors', []):
        if actor.get('name'):
            actor['encrypted_name'] = encrypt(actor['name'])
        if actor.get('photo'):
            actor['encrypted_photo'] = encrypt(actor['photo'])

    return render(request, 'series_detail.html', {'series': series_details})




from django.utils import timezone
from datetime import timedelta

def get_daily_message_count(user):
    today = timezone.now().date()
    return ChatHistory.objects.filter(user=user, timestamp__date=today).count()

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from cryptography.fernet import InvalidToken
import base64

@login_required(login_url=reverse_lazy('login'))
def chat_with_character(request, show_name, encrypted_character_name):
    try:
        show_name = decrypt(show_name)
        character_name = decrypt(encrypted_character_name)

        encrypted_character_image_url = request.GET.get('character_image_url')
        character_image_url = decrypt(encrypted_character_image_url) if encrypted_character_image_url else ''

        is_actor = request.GET.get('actor') == 'true'

        username = request.user.username
        character_gender = request.GET.get('character_gender')

        conversation_key = f'{username}_{character_name}'

        # Retrieve conversation history from the session
        if conversation_key in request.session:
            conversation = request.session[conversation_key]
        else:
            conversation = []

        context = {
            'conversation': conversation,
            'show_name': show_name,
            'character_name': character_name,
            'character_image_url': character_image_url,
            'character_gender': character_gender,
            'is_actor': is_actor,
        }

        if request.method == 'POST':
            user_input = request.POST.get('user_input')

            profile = Profile.objects.get(user=request.user)
            profile.reset_daily_message_counts()

            daily_message_count = profile.daily_message_count_characters
            if not profile.has_paid and daily_message_count >= 10:
                ai_response = f"Sorry {username}, your daily message limit reached. Try premium plan for unlimited messages."
                return JsonResponse({'user_input': user_input, 'ai_response': ai_response, 'limit_reached': True, 'payment_url': reverse('payment_page')})

            if user_input:
                conversation.append({'user': username, 'text': user_input})

                ai_response = chat(conversation, show_name, character_name, username, is_actor)

                conversation.append({'user': character_name, 'text': ai_response, 'character_name': character_name})

                # Save conversation to session
                request.session[conversation_key] = conversation

                ChatHistory.objects.create(
                    user=request.user,
                    show_name=show_name,
                    character_name=character_name,
                    character_image_url=character_image_url,
                    message=user_input
                )
                ChatHistory.objects.create(
                    user=request.user,
                    show_name=show_name,
                    character_name=character_name,
                    character_image_url=character_image_url,
                    message=ai_response
                )

                # Increment daily message count
                profile.daily_message_count_characters += 1
                profile.save()

                return JsonResponse({'user_input': user_input, 'ai_response': ai_response})

        return render(request, 'chat.html', context)

    except (InvalidToken, base64.binascii.Error):
        return render(request, 'error.html', {'message': 'Invalid encryption token'})






@login_required(login_url=reverse_lazy('login'))
def chatted_characters(request):
    query = request.GET.get('q')
    latest_chats = (
        ChatHistory.objects.filter(user=request.user)
        .values('character_name', 'show_name', 'character_image_url')
        .annotate(latest_timestamp=Max('timestamp'))
        .order_by('-latest_timestamp')
    )

    if query:
        latest_chats = latest_chats.filter(Q(character_name__icontains=query))

    encrypted_chats = []
    for chat in latest_chats:
        encrypted_chats.append({
            'encrypted_show_name': encrypt(chat['show_name']),
            'encrypted_character_name': encrypt(chat['character_name']),
            'encrypted_character_image_url': encrypt(chat['character_image_url']),
            'character_name': chat['character_name'],
            'show_name': chat['show_name'],
            'character_image_url': chat['character_image_url'],
        })

    context = {
        'chatted_characters': encrypted_chats,
        'search_query': query,
    }
    return render(request, 'chatted_characters.html', context)




def chat(conversation, show_name, character_name, username, is_actor=False):
    if is_actor:
        prompt = f"Hey there! You're {character_name}, an actor from {show_name}, talking with {username}."
    else:
        prompt = f"Hey there! You're {character_name} from {show_name} talking with {username}. You're fully immersed in character mode."

    # Construct the conversation history for context
    for message in conversation:
        prompt += f"{message['user']}: {message['text']}\n"

    prompt += f"{character_name}:"

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.6,
    )
    return response.choices[0].text.strip()



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .forms import CustomUserCreationForm
from django.core.cache import cache

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')

            # Check if the user with the provided email or username already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'register.html', {'form': form})

            if User.objects.filter(username=username).exists():
                messages.error(request, 'A user with this username already exists.')
                return render(request, 'register.html', {'form': form})

            otp = get_random_string(length=6, allowed_chars='0123456789')
            cache.set(email, otp, 300)  # Store OTP in cache for 5 minutes

            # Send OTP to the user's email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            # Temporarily store form data in session
            request.session['form_data'] = form.cleaned_data

            return redirect('verify_otp')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        form_data = request.session.get('form_data')

        if not form_data:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('register')

        cached_otp = cache.get(form_data['email'])
        if otp == cached_otp:
            # Recheck to ensure user doesn't exist before creating
            if not User.objects.filter(username=form_data['username']).exists() and not User.objects.filter(email=form_data['email']).exists():
                user = User.objects.create_user(
                    username=form_data['username'],
                    email=form_data['email'],
                    password=form_data['password1']
                )
                user.save()
                messages.success(request, 'Your account has been created. You can now login.')
                return redirect('login')
            else:
                messages.error(request, 'User with this username or email already exists.')
                return redirect('register')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')
    return render(request, 'verify_otp.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=User.objects.get(email=email).username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to a success page.
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')


from .forms import PasswordResetRequestForm
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password_reset_email.txt"
                    c = {
                        "email": user.email,
                        "domain": request.META["HTTP_HOST"],
                        "site_name": "www.chatcrewai.com",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",
                    }
                    email_content = render_to_string(email_template_name, c)
                    send_mail(subject, email_content, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
                messages.success(request, "A link to reset your password has been sent to your email address.")
                return redirect("login")
            else:
                messages.error(request, "No user is associated with this email address.")
                return render(request, "password_reset.html", {"form": form})
    else:
        form = PasswordResetRequestForm()
    return render(request, "password_reset.html", {"form": form})

from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode


def password_reset_confirm(request, uidb64=None, token=None):
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been reset successfully. You can now log in.")
                return redirect("login")
        else:
            form = SetPasswordForm(user)
    else:
        messages.error(request, "The reset link is invalid. Please request a new one.")
        return redirect("password_reset")

    return render(request, "password_reset_confirm.html", {"form": form, "user": user})


@login_required
def user_payment(request):
    return render(request,'payment.html')

def about(request):
    return render(request,'about.html')


from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
import openai
import random

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import FanChatHistory
import openai
import random

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import FanChatHistory
import openai
import random

# views.py
from .utils import decrypt

# views.py
from .utils import decrypt

# views.py
from .utils import decrypt

@login_required(login_url=reverse_lazy('login'))
def fan_to_fan_chat(request, encrypted_show_name):
    try:
        show_name = decrypt(encrypted_show_name)
    except (InvalidToken, base64.binascii.Error):
        return render(request, 'error.html', {'message': 'Invalid encryption token'})

    conversation = FanChatHistory.objects.filter(show_name=show_name).order_by('timestamp')

    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        reply_to_id = request.POST.get('reply_to')
        reply_to_message = FanChatHistory.objects.get(id=reply_to_id) if reply_to_id else None

        ai_response = fan_chat(user_input, show_name, conversation)

        # Save user message
        user_message = FanChatHistory.objects.create(
            user=request.user,
            show_name=show_name,
            message=user_input,
            is_user_message=True,
            reply_to=reply_to_message
        )

        # Save AI response
        FanChatHistory.objects.create(
            user=request.user,
            show_name=show_name,
            message=ai_response,
            is_user_message=False,
            reply_to=user_message
        )

        return JsonResponse({'user_input': user_input, 'ai_response': ai_response, 'reply_to': reply_to_id})

    context = {
        'conversation': conversation,
        'show_name': show_name,
        'encrypted_show_name': encrypted_show_name,  # Pass encrypted show name to the template
    }

    return render(request, 'fan_chat.html', context)



import openai

def fan_chat(user_input, show_name, conversation):
    ai_name = random.choice(["Jason", "Miya", "Catherin", "Alex", "Wicky", "Anzil", "Peter", "Jojo", "William", "Mad Max", "Mike", "Shibil", "Sana"])

    # Construct the conversation history for context
    conversation_history = ""
    for message in conversation:
        sender = "User" if message.is_user_message else ai_name
        conversation_history += f"{sender}: {message.message}\n"

    # Add the current user input to the conversation history
    conversation_history += f"User: {user_input}\n{ai_name}:"

    # Create the prompt for the AI
    prompt = f"You are chatting with a fan of the {show_name}. If you don't know about {show_name}, politely admit it but try to keep the user engaged and interested in the platform.\n\n{conversation_history}"

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150,  # Increased to allow more detailed responses
        n=1,
        stop=None,
        temperature=0.6,
    )

    return response.choices[0].text.strip()





import requests
from django.shortcuts import render
from django.conf import settings
from datetime import datetime
from django.core.cache import cache
import random

def calculate_age(birth_date):
    if not birth_date:
        return None
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


@login_required(login_url=reverse_lazy('login'))
@login_required
def date_characters(request):
    if request.method == 'POST':
        gender = request.POST.get('gender')
        age = request.POST.get('age')

        gender_map = {
            'male': 2,
            'female': 1,
            'other': 3
        }
        gender_id = gender_map.get(gender)

        api_key = api_key1
        movies = cache.get('popular_movies')

        if not movies:
            url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US"
            response = requests.get(url)
            movies = response.json().get('results', [])
            cache.set('popular_movies', movies, timeout=60*60)  # Cache for 1 hour

        characters = []
        min_age, max_age = (None, None)
        if age and '-' in age:
            min_age, max_age = map(int, age.split('-'))

        random.shuffle(movies)  # Shuffle the list of movies

        for movie in movies[:10]:  # Limit to first 10 movies after shuffling
            movie_id = movie['id']
            movie_title = movie['title']
            credits = cache.get(f'movie_{movie_id}_credits')

            if not credits:
                credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=en-US"
                credits_response = requests.get(credits_url)
                credits = credits_response.json().get('cast', [])
                cache.set(f'movie_{movie_id}_credits', credits, timeout=60*60)

            random.shuffle(credits)  # Shuffle the list of cast members

            for cast_member in credits[:10]:  # Limit to first 10 cast members after shuffling
                if 'gender' in cast_member and cast_member['gender'] == gender_id:
                    actor_id = cast_member['id']
                    actor_details = cache.get(f'actor_{actor_id}')

                    if not actor_details:
                        actor_url = f"https://api.themoviedb.org/3/person/{actor_id}?api_key={api_key}&language=en-US"
                        actor_response = requests.get(actor_url)
                        actor_details = actor_response.json()
                        cache.set(f'actor_{actor_id}', actor_details, timeout=60*60)

                    actor_age = calculate_age(actor_details.get('birthday'))

                    # Check conditions to skip characters
                    if actor_age is not None and min_age is not None and max_age is not None:
                        if min_age <= actor_age <= max_age and 'profile_path' in cast_member \
                                and cast_member['profile_path'] is not None \
                                and 'character' in cast_member \
                                and cast_member['character'] and 'voice' not in cast_member['character'].lower():
                            characters.append({
                                'character_name': cast_member['character'],
                                'movie_name': movie_title,
                                'profile_path': cast_member.get('profile_path'),
                                'character_age': actor_age  # Add the character age
                            })

                            if len(characters) >= 10:  # Stop collecting once we have 10 characters
                                break
            if len(characters) >= 10:  # Stop iterating over movies once we have 10 characters
                break

        return render(request, 'characters.html', {'characters': characters})

    return render(request, 'datingsearch.html')


@login_required(login_url=reverse_lazy('login'))
@login_required
def dating_chat(request, show_name, character_name):
    username = request.user.username
    conversation = request.session.get(character_name, [])
    context = {
        'conversation': conversation,
        'show_name': show_name,
        'character_name': character_name,
    }

    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        conversation.append({'user': username, 'text': user_input})
        
        ai_response = chat_date(conversation, show_name, character_name, username)
        
        conversation.append({'user': character_name, 'text': ai_response})

        request.session[character_name] = conversation

        return JsonResponse({'user_input': user_input, 'ai_response': ai_response})

    return render(request, 'dating_chat.html', context)


@login_required(login_url=reverse_lazy('login'))
@login_required
def chat_date(conversation, show_name, character_name, username):
    """
    This function sends a message to the ChatGPT API and returns the response.

    Args:
        conversation: The entire conversation history.
        show_name: The name of the selected show.
        character_name: The name of the selected character (which is often the actor's name).
        username: The username of the logged-in user, if available.

    Returns:
        The chatbot's response to the user's message.
    """
    prompt = f"You are {character_name} from {show_name}. You are chatting with {username} who likes you a lot. Here's your conversation so far:\n"

    for message in conversation:
        prompt += f"{message['user']}: {message['text']}\n"

    prompt += f"{character_name}:"

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.6,
    )
    return response.choices[0].text.strip()


@login_required(login_url=reverse_lazy('login'))
def search_characters(request):
    query = request.GET.get('query', '').lower()
    api_key = api_key1

    if query:
        # Step 1: Search for shows and movies matching the query
        response_tv = requests.get(f'https://api.themoviedb.org/3/search/tv?api_key={api_key}&query={query}')
        response_movie = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}')
        
        if response_tv.status_code == 200 and response_movie.status_code == 200:
            shows = response_tv.json().get('results', [])
            movies = response_movie.json().get('results', [])
            data = []

            # Step 2: Get characters from TV shows
            for show in shows:
                show_id = show['id']
                show_name = show['name']
                credits_response = requests.get(f'https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={api_key}')
                
                if credits_response.status_code == 200:
                    credits = credits_response.json()
                    for cast in credits.get('cast', []):
                        character_name = cast.get('character')
                        character_image_path = cast.get('profile_path')
                        
                        # Skip characters without an image and those containing "self" or "voice"
                        if character_name and character_image_path and 'self' not in character_name.lower() and 'voice' not in character_name.lower():
                            data.append({
                                'character_name': character_name,
                                'show_name': show_name,
                                'image': f"https://image.tmdb.org/t/p/w500{character_image_path}"
                            })

            # Step 3: Get characters from movies
            for movie in movies:
                movie_id = movie['id']
                movie_name = movie['title']
                credits_response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}')
                
                if credits_response.status_code == 200:
                    credits = credits_response.json()
                    for cast in credits.get('cast', []):
                        character_name = cast.get('character')
                        character_image_path = cast.get('profile_path')
                        
                        # Skip characters without an image and those containing "self" or "voice"
                        if character_name and character_image_path and 'self' not in character_name.lower() and 'voice' not in character_name.lower():
                            data.append({
                                'character_name': character_name,
                                'show_name': movie_name,
                                'image': f"https://image.tmdb.org/t/p/w500{character_image_path}"
                            })

            return JsonResponse({'results': data})

    return JsonResponse({'results': []})



@login_required(login_url=reverse_lazy('login'))
def roleplay_selection(request):
    return render(request, 'roleplay_selection.html')


@login_required(login_url=reverse_lazy('login'))
def get_encrypted_url(request):
    character_name = request.GET.get('character_name')
    opponent_name = request.GET.get('opponent_name')
    character_image_url = request.GET.get('character_image_url')
    opponent_image_url = request.GET.get('opponent_image_url')

    encrypted_params = encrypt_params({
        'character_name': character_name,
        'opponent_name': opponent_name,
        'character_image_url': character_image_url,
        'opponent_image_url': opponent_image_url,
    })

    url = reverse('roleplay_chat', args=[encrypted_params])
    return JsonResponse({'url': url})

def get_daily_message_count(user):
    today = timezone.now().date()
    return ChatHistory.objects.filter(user=user, timestamp__date=today).count()


@csrf_exempt
@login_required(login_url=reverse_lazy('login'))
def roleplay_chat(request, encrypted_params):
    try:
        params = decrypt_params(encrypted_params)
    except (InvalidToken, base64.binascii.Error):
        return render(request, 'error.html', {'message': 'Invalid encryption token'})

    character_name = params.get('character_name')
    opponent_name = params.get('opponent_name')
    character_image_url = params.get('character_image_url')
    opponent_image_url = params.get('opponent_image_url')
    conversation_key = f'roleplay_{character_name}_{opponent_name}_conversation'
    conversation = request.session.get(conversation_key, [])

    user = request.user
    profile = Profile.objects.get(user=user)
    profile.reset_daily_message_counts()

    if request.method == 'POST':
        user_input = request.POST.get('user_input')

        # Check if user has reached the daily message limit for roleplay chat
        if not profile.has_paid and profile.daily_message_count_roleplay >= 10:
            ai_response = "Daily message limit reached. Try premium plan for unlimited messages."
            return JsonResponse({
                'user_input': user_input,
                'ai_response': ai_response,
                'limit_reached': True,
                'payment_url': reverse('payment_page')
            })

        if user_input:
            conversation.append({'user': character_name, 'text': user_input})

            RoleplayChatHistory.objects.create(
                user=user,
                character_name=character_name,
                opponent_name=opponent_name,
                message=user_input,
                character_image_url=character_image_url,
                opponent_image_url=opponent_image_url
            )

            ai_response = rolechat(conversation, character_name, opponent_name)
            conversation.append({'user': opponent_name, 'text': ai_response})

            RoleplayChatHistory.objects.create(
                user=user,
                character_name=character_name,
                opponent_name=opponent_name,
                message=ai_response,
                character_image_url=character_image_url,
                opponent_image_url=opponent_image_url
            )

            # Update the daily message count for roleplay chat
            profile.daily_message_count_roleplay += 1
            profile.save()

            request.session[conversation_key] = conversation

            return JsonResponse({
                'user_input': user_input,
                'ai_response': ai_response,
                'limit_reached': False
            })

    context = {
        'character_name': character_name,
        'opponent_name': opponent_name,
        'character_image_url': character_image_url,
        'opponent_image_url': opponent_image_url,
        'conversation': conversation,
    }

    return render(request, 'roleplay_chat.html', context)






def rolechat(conversation, character_name, opponent_name):
    prompt = f"You are roleplaying as {character_name}. Respond concisely as {opponent_name}. Here is the conversation so far:\n"
    for message in conversation:
        if isinstance(message, dict):
            prompt += f"{message['user']}: {message['text']}\n"
    prompt += f"{opponent_name}:"

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.6,
    )

    return response.choices[0].text.strip()

# views.py
from django.urls import reverse
from django.utils.http import urlencode

@login_required(login_url=reverse_lazy('login'))
def roleplay_chatted_characters(request):
    latest_chats = (
        RoleplayChatHistory.objects.filter(user=request.user)
        .values('character_name', 'opponent_name', 'character_image_url', 'opponent_image_url')
        .annotate(latest_timestamp=Max('timestamp'))
        .order_by('-latest_timestamp')
    )

    for chat in latest_chats:
        encrypted_params = encrypt_params({
            'character_name': chat['character_name'],
            'opponent_name': chat['opponent_name'],
            'character_image_url': chat['character_image_url'],
            'opponent_image_url': chat['opponent_image_url'],
        })
        chat['encrypted_url'] = encrypted_params

    context = {'roleplay_chats': latest_chats}
    return render(request, 'roleplay_chatted_characters.html', context)



# views.py

import razorpay
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse
from .utils import get_razorpay_client


def create_order(amount, currency='USD'):
    converted_amount = get_converted_amount(amount, currency)
    client = get_razorpay_client()
    order_data = {
        'amount': int(converted_amount * 100),  # amount in cents for USD
        'currency': currency,
        'payment_capture': 1
    }
    order = client.order.create(data=order_data)
    return order


def payment_page(request):
    if request.method == 'POST':
        plan = request.POST.get('plan')
        if plan == 'monthly':
            amount = 13  # in USD
        elif plan == 'yearly':
            amount = 88  # in USD
        else:
            return HttpResponseBadRequest('Invalid plan selected.')

        order = create_order(amount)
        context = {
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'order_id': order['id'],
            'amount': int(amount * 100),  # amount in cents for USD
            'currency': 'USD',
        }
        return render(request, 'payment_page.html', context)
    else:
        return render(request, 'select_plan.html')


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

@login_required
def initiate_payment(request):
    currency = 'USD'
    amount = 8800  # Amount in cents for USD (88 USD)

    payment = client.order.create({
        'amount': amount,
        'currency': currency,
        'payment_capture': '1'
    })

    context = {
        'payment': payment,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount // 100,
    }
    return render(request, 'initiate_payment.html', context)

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            # Payment successful, update user's profile
            request.user.profile.has_paid = True
            request.user.profile.save()
            return redirect('home')
        except:
            return render(request, 'payment_failed.html')
    return redirect('home')


import hmac
import hashlib
import json
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        webhook_secret = settings.RAZORPAY_SECRET_KEY
        payload = request.body
        received_signature = request.headers.get('X-Razorpay-Signature')

        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(received_signature, expected_signature):
            event = json.loads(payload)
            # Process the event (e.g., update payment status in database)
            return JsonResponse({'status': 'success'})
        else:
            return HttpResponseBadRequest('Invalid signature')

    return HttpResponseBadRequest('Invalid request')


def handler404(request, exception):
    return render(request, 'error.html', status=404)

def handler500(request):
    return render(request, 'error.html', status=500)
