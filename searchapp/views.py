from django.shortcuts import render
import requests
from datetime import datetime

api_key1 = "8567907539df0a097b6f71deee2c4d22"


def search(request):
    search_query = request.GET.get('search')
    search_results = []

    if search_query:
        api_key = api_key1
        url = f'https://api.themoviedb.org/3/search/multi'
        params = {
            'api_key': api_key,
            'query': search_query
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json().get('results', [])

            search_results = [result for result in results if (result.get('title') or result.get('name')) and (result.get('poster_path') or result.get('backdrop_path'))]

            filtered_results = []

            for result in search_results:
                media_type = result.get('media_type')
                media_id = result.get('id')
                if media_type in ['movie', 'tv']:
                    details_url = f'https://api.themoviedb.org/3/{media_type}/{media_id}'
                    details_params = {
                        'api_key': api_key,
                        'append_to_response': 'credits'
                    }
                    details_response = requests.get(details_url, params=details_params)
                    details_response.raise_for_status()
                    details_data = details_response.json()

                    characters = details_data.get('credits', {}).get('cast', [])
                    num_characters_with_photo = sum(1 for character in characters if character.get('profile_path'))

                    if num_characters_with_photo > 0:
                        result['num_characters'] = num_characters_with_photo
                        filtered_results.append(result)

            search_results = filtered_results

        except requests.RequestException as e:
            print(f"Request Exception: {e}")

    context = {
        'search_results': search_results,
    }

    return render(request, 'search_results.html', context)


from django.shortcuts import render
import requests
from ChatCrewApp.utils import encrypt, decrypt  # Assuming you have encryption utility functions

api_key1 = "8567907539df0a097b6f71deee2c4d22"


from django.shortcuts import render
import requests
from ChatCrewApp.utils import encrypt, decrypt  # Assuming you have encryption utility functions

api_key1 = "8567907539df0a097b6f71deee2c4d22"

def result_detail(request, result_id, media_type):
    api_key = api_key1
    if media_type == 'movie':
        url = f'https://api.themoviedb.org/3/movie/{result_id}'
    elif media_type == 'tv':
        url = f'https://api.themoviedb.org/3/tv/{result_id}'
    else:
        # Handle invalid media type
        return render(request, 'error.html')

    params = {
        'api_key': api_key,
        'append_to_response': 'credits'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result_data = response.json()

        characters = result_data.get('credits', {}).get('cast', [])
        thumbnail = result_data.get('poster_path')
        title = result_data.get('title') if media_type == 'movie' else result_data.get('name')

        # Encrypt the title for use in URLs
        encrypted_title = encrypt(title)

        # Extract character names and photos, encrypt them
        character_info = [
            {
                'name': character.get('character'),
                'photo': f"https://image.tmdb.org/t/p/w500{character.get('profile_path')}",
                'encrypted_name': encrypt(character.get('character')),
                'encrypted_photo': encrypt(f"https://image.tmdb.org/t/p/w500{character.get('profile_path')}")
            }
            for character in characters if character.get('profile_path')
        ]

        # Extract actor names and photos, encrypt them
        actor_info = [
            {
                'name': character.get('name'),
                'photo': f"https://image.tmdb.org/t/p/w500{character.get('profile_path')}",
                'encrypted_name': encrypt(character.get('name')),
                'encrypted_photo': encrypt(f"https://image.tmdb.org/t/p/w500{character.get('profile_path')}")
            }
            for character in characters if character.get('profile_path')
        ]

        # Check if the result is animated
        is_animated = any(genre['name'].lower() == 'animation' for genre in result_data.get('genres', []))

        context = {
            'thumbnail': thumbnail,
            'title': title,
            'encrypted_title': encrypted_title,
            'characters': character_info,
            'actors': actor_info,
            'is_animated': is_animated
        }
        return render(request, 'result_detail.html', context)

    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return render(request, 'error.html')

