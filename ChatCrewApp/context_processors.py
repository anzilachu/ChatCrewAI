# In your app's directory, create a file named context_processors.py
# For example: yourapp/context_processors.py

from .views import fetch_genres

def genres_processor(request):
    # Fetch genres
    genres = fetch_genres()
    
    # Return the context data as a dictionary
    return {'genres': genres}
