from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('popular/movies/', popular_movies, name='popular_movies'),
    path('popular/series/', popular_series, name='popular_series'),
    path('recent/movies/', recent_movies, name='recent_movies'),
    path('recent/series/', recent_series, name='recent_series'),

    path('genre/<str:genre>/', genre_detail, name='genre_detail'),

    path('movies/<int:movie_id>/', movie_detail, name='movie_detail'),
    path('series/<int:series_id>/', series_detail, name='series_detail'),
    path('chat/<str:show_name>/<path:character_name>/', chat_with_character, name='chat_with_character'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('payment/', user_payment, name='payment'),

    path('about/', about, name='about'),


]