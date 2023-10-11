from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('search/', views.index, name="index"),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('search_history/', views.search_history, name='search_history'),
    path('history_result/<keyword>', views.history_result, name="history_result"),
    path('delete_search/<keyword>', views.delete_search, name='delete_search'),
    path('clear_history/', views.clear_search_history, name='clear_history'),
    path('refresh_search/<keyword>', views.refresh_search, name='refresh_search'),
   
]