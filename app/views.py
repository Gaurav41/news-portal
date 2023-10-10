from datetime import datetime, timedelta
from django.shortcuts import render, redirect,get_object_or_404
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
    ''' If get request then serve index page, if post then fetch the result as per keyword and return with 
        index page.
        If search result is alredy exists in time interval of last 15 min then return the same. or fetch the 
        new result and return
    '''
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

        # Fetch the new results
        data = search_news(keyword)
        if data['status']=='ok':
            sorted_articles = sorted(data['articles'], key=lambda x: x['publishedAt'],reverse=True)
            articles=[ {"title":article['title'],
                        "description":article['description'],
                        "author":article['author'],
                        "source":article['source'],
                        "url":article['url'],
                        "publishedAt": datetime.fromisoformat(article['publishedAt'][:-1]).strftime('%B %d, %Y %I:%M %p')} 
                        for article in sorted_articles if article['title'] !='[Removed]'] 
            # print(sorted_articles)
            result= {
            'status':'Success',
            'keyword':keyword,
            'total_results':data['totalResults'],
            'articles': articles
            }

            search_history = SearchHistory.objects.create(user=logged_in_user, query=keyword, date=datetime.now())
            SearchResult.objects.create(search=search_history, 
                                    search_result = result
                                    )
            return render(request, "index.html",{'data':result})
        else:
            print(data)
            result= {
            'status': data['status'],
            'error':'Something went wrong, Try again later'
            }
            return render(request, "index.html",{'data':result})
    else:
        return render(request, "index.html",)



def search_news(keywords):
    ''' Call API and return the result '''
    print("New API")
    url = f"{API_URL}/everything?q={keywords}&from=2023-09-10&language=en&sortBy=publishedAt&pageSize=20&apiKey={API_KEY}"
    response = requests.get(url)
    print(response)
    data = response.json()
    return data

def search_history(request):
    ''' get the users search history from database '''
    logged_in_user = request.user
    searches = SearchHistory.objects.filter(user=logged_in_user).order_by('-date')
    return render(request, 'search_history.html', {'searches': searches})


def history_result(request, keyword):
    ''' show the history search result '''
    history_result = SearchHistory.objects.filter(user=request.user, query=keyword)
    search_data = SearchResult.objects.filter(search=history_result.first())
    data = search_data.first().search_result
    return render(request, 'view_history_result.html', {'data': data})


def delete_search(request, keyword):
    ''' delete the history search from database '''
    search = get_object_or_404(SearchHistory, query=keyword,user=request.user)
    search.delete()
    return redirect('search_history')


def refresh_search(request, keyword):
    ''' delete the history search from database '''
    recent_searches = SearchHistory.objects.filter(user=request.user, query=keyword)
    exsiting_result = SearchResult.objects.filter(search=recent_searches.first()).first()
    if exsiting_result:
        exsiting_search_result = exsiting_result.search_result
        recent_news_date = exsiting_search_result['articles'][0]['publishedAt']
        ISO_date = datetime.strptime(recent_news_date, '%B %d, %Y %I:%M %p').isoformat()
        # all API and return the result '''
        url = f"{API_URL}/everything?q={keyword}&from={ISO_date}&language=en&sortBy=publishedAt&pageSize=20&apiKey={API_KEY}"
        response = requests.get(url)
        # print(response)
        new_results = response.json()
        if new_results['status']=='ok' and new_results['totalResults'] > 0:
            totalResults = new_results['totalResults']+exsiting_search_result['total_results']
            articles=[ {"title":article['title'],
                        "description":article['description'],
                        "author":article['author'],
                        "source":article['source'],
                        "url":article['url'],
                        "publishedAt": datetime.fromisoformat(article['publishedAt'][:-1]).strftime('%B %d, %Y %I:%M %p')} 
                        for article in new_results['articles'] if article['title'] !='[Removed]'] 
            articles = articles+exsiting_search_result['articles']
            combined_result = {
                'status':'Success',
                'keyword':keyword,
                'total_results':totalResults,
                'articles': articles
            }
            exsiting_result.search_result = combined_result
            exsiting_result.save()
            recent_searches.date = datetime.now()
        return render(request, "index.html",{'data':combined_result})
    else:
        return redirect('index')

    



def signup(request):
    ''' Register new user and after successful registration redirect user to login page '''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_view')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    ''' login view for users to login into app '''
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

