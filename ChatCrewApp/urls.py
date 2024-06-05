from django.urls import path
from .views import *
from .utils import encrypt, decrypt

urlpatterns = [
    path('', home, name='home'),
    path('popular/movies/', popular_movies, name='popular_movies'),
    path('popular/series/', popular_series, name='popular_series'),
    path('recent/movies/', recent_movies, name='recent_movies'),
    path('recent/series/', recent_series, name='recent_series'),

    path('genre/<str:genre>/', genre_detail, name='genre_detail'),

    path('movies/<str:encrypted_movie_id>/', movie_detail, name='movie_detail'),
    path('series/<str:encrypted_series_id>/', series_detail, name='series_detail'),
    path('chat/<str:show_name>/<str:encrypted_character_name>/', chat_with_character, name='chat_with_character'),
    path('fan-chat/<str:encrypted_show_name>/', fan_to_fan_chat, name='fan_chat'),
    path('register/', register, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('password-reset/', password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),



    path('about/', about, name='about'),

    path('date_characters/', date_characters, name='date_characters'),
    path('dating_chat/<str:show_name>/<str:character_name>/', dating_chat, name='dating_chat'),

    path('chatted-characters/', chatted_characters, name='chatted_characters'),
    path('select-roleplay/', roleplay_selection, name='select_roleplay'),
    path('search-characters/', search_characters, name='search_characters'),
    path('roleplay/<str:encrypted_params>/', roleplay_chat, name='roleplay_chat'),
    path('roleplay_chats/', roleplay_chatted_characters, name='roleplay_chatted_characters'),
    path('get-encrypted-url/', get_encrypted_url, name='get_encrypted_url'),

    path('payment/', payment_page, name='payment_page'),
    path('payment/callback/', payment_callback, name='payment_callback'),
    path('payment/webhook/', webhook, name='payment_webhook'),
    path('initiate-payment/', initiate_payment, name='initiate_payment'),
]
