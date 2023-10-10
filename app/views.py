from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from dotenv import load_dotenv
import os
import requests
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import SearchHistory, SearchResult
from django.utils import timezone

load_dotenv()

# Create your views here.
API_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

def index(request):
    if request.user.is_authenticated:
        logged_in_user = request.user
        print("User logged in: ",logged_in_user.username)
    else:
        return redirect('login_view')
    
    if request.method=='POST':
        keyword = request.POST.get('keyword')
        recent_searches = SearchHistory.objects.filter(user=logged_in_user, query=keyword)
    
        if recent_searches.exists():
            result=""
            recent_result = recent_searches.latest('date')
            time_threshold = timezone.now() - timedelta(minutes=15)

            search_data = SearchResult.objects.filter(search=recent_searches.first())
            if recent_result.date > time_threshold:
                print("In history")
                data = search_data.first().search_result
                return render(request, "index.html",{'data':data})
            else:
                search_data.delete()
                recent_searches.delete()

        data = search_news(keyword)
        if data['status']=='ok':
            sorted_articles = sorted(data['articles'], key=lambda x: x['publishedAt'],reverse=True)
            articles=[ {"title":article['title'],"description":article['description'],"author":article['author'],"source":article['source'],"url":article['url'],'publishedAt': datetime.fromisoformat(article['publishedAt'][:-1]).strftime('%B %d, %Y %I:%M %p')} for article in sorted_articles if article['title'] !='[Removed]'] 
            # print(sorted_articles)
            result= {
            'status':'Success',
            'keyword':keyword,
            'total_results':data['totalResults'],
            'articles': articles
            }
        else:
            result= {
            'status':'Failed',
            'error':'Something went wrong, Try again later'
            }
        search_history = SearchHistory.objects.create(user=logged_in_user, query=keyword, date=datetime.now())
        SearchResult.objects.create(search=search_history, 
                                    search_result = result
                                    )
        return render(request, "index.html",{'data':result})
    else:
        return render(request, "index.html",)



def search_news(keywords):
    print("calling new API")
    url = f"{API_URL}/everything?q={keywords}&from=2023-09-09&language=en&sortBy=publishedAt&pageSize=20&apiKey={API_KEY}"
    response = requests.get(url)
    print(response)
    data = response.json()
    return data


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_view')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Redirect to your home page
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login_view')