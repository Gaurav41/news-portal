from datetime import datetime, timedelta
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from dotenv import load_dotenv
import os
import requests
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import SearchHistory, Article
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .filters import ArticleFilter



load_dotenv()

# Create your views here.
API_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

@login_required()
def index(request):
    ''' If get request then serve index page, if post then fetch the result as per keyword and return with 
        index page.
        If search result is alredy exists in time interval of last 15 min then return the same. or fetch the 
        new result and return
    '''

    logged_in_user = request.user
    # print("User logged in: ",logged_in_user.username)
    
    if request.method=='POST':
        keyword = request.POST.get('keyword')
        recent_searches = SearchHistory.objects.filter(user=logged_in_user, query=keyword)

        if recent_searches.exists():
            result=""
            recent_result = recent_searches.latest('date')
            time_threshold = timezone.now() - timedelta(minutes=15)

            search_data = Article.objects.filter(search=recent_searches.first()).all()
            print("discttt: ",search_data.values_list('title', flat=True).distinct())

            articleFilter = ArticleFilter(request.GET,queryset=search_data)
            search_data = articleFilter.qs
            if recent_result.date > time_threshold:
                print("In history")
                metadata= recent_searches.first().metadata
                return render(request, "index.html",{'data':search_data,"search_metadata":metadata,"articleFilter":articleFilter})
            else:
                search_data.delete()
                recent_searches.delete()

        # Fetch the new results
        data = search_news(keyword)
        # print(data)
        if data['status']=='ok':
            # sorted_articles = sorted(data['articles'], key=lambda x: x['publishedAt'],reverse=True)
            metadata= {
            'status':'Success',
            'keyword':keyword,
            'total_results':data['totalResults'],
            }
            search_history = SearchHistory.objects.create(user=logged_in_user, query=keyword, date=datetime.now(),metadata=metadata)

            articles=[
                    Article(
                    search = search_history,
                    title=article['title'],
                    description=article['description'],
                    content=article['content'],
                    author=article['author'],
                    source=article['source'],
                    url=article['url'],
                    publishedAt=datetime.fromisoformat(article['publishedAt'][:-1])
                     ) for article in data['articles'] if article['title'] !='[Removed]'
                ]  
            print(articles)
            
            Article.objects.bulk_create(articles)
            search_data = Article.objects.filter(search=recent_searches.first()).all()
            articleFilter = ArticleFilter(request.GET,queryset=search_data)
            search_data = articleFilter.qs
            return render(request, "index.html",{'data':search_data,"search_metadata":metadata,"articleFilter":articleFilter})
        else:
            print(data)
            result= {
            'status': data['status'],
            'error':'Something went wrong, Try again later'
            }
            return render(request, "index.html",{'data':result})
    else:
        return render(request, "index.html")


def get_searches(request,keyword):
    recent_searches = SearchHistory.objects.filter(user=request.user, query=keyword)
    search_data = Article.objects.filter(search=recent_searches.first()).all()
    articleFilter = ArticleFilter(request.GET,queryset=search_data)
    search_data = articleFilter.qs
    metadata= recent_searches.first().metadata
    return render(request, "index.html",{'data':search_data,"search_metadata":metadata, "articleFilter":articleFilter})
 


def search_news(keywords):
    ''' Call API and return the result '''
    print("New API")
    url = f"{API_URL}/everything?q={keywords}&language=en&sortBy=publishedAt&pageSize=3&apiKey={API_KEY}"
    response = requests.get(url)
    # print(response)
    data = response.json()
    return data

@login_required()
def search_history(request):
    ''' get the users search history from database '''
    searches = SearchHistory.objects.filter(user=request.user).order_by('-date')
    return render(request, 'search_history.html', {'searches': searches})

@login_required()
def history_result(request, keyword):
    ''' show the history search result '''
    history_result = SearchHistory.objects.filter(user=request.user, query=keyword).first()
    search_data = Article.objects.filter(search=history_result).all()
    return render(request, 'view_history_result.html', {'data': search_data,"search_metadata":history_result.metadata})


def delete_search(request, keyword):
    ''' delete the history search from database '''
    search = get_object_or_404(SearchHistory, query=keyword,user=request.user)
    search.delete()
    return redirect('search_history')


def clear_search_history(request):
    ''' delete the history search from database '''
    SearchHistory.objects.filter(user=request.user).delete()
    return redirect('search_history')


def refresh_search(request, keyword):
    ''' Refresh the search resutls. append new results to old ones  '''
    recent_searches = SearchHistory.objects.filter(user=request.user, query=keyword).first()
    exsiting_result = Article.objects.filter(search=recent_searches).all()
    if exsiting_result:
        recent_article_date = exsiting_result.latest('publishedAt').publishedAt.isoformat()
        print("recent_article_date: ",recent_article_date)
        # ISO_date = datetime.strptime(recent_news_date.publishedAt, '%B %d, %Y %I:%M %p').isoformat()
        print("ISO_date: ",recent_article_date)
        # all API and return the result '''
        url = f"{API_URL}/everything?q={keyword}&from={recent_article_date}&language=en&sortBy=publishedAt&pageSize=3&apiKey={API_KEY}"
        response = requests.get(url)
        new_results = response.json()
        if new_results['status']=='ok' and new_results['totalResults'] > 0:
            totalResults = new_results['totalResults']+ recent_searches.metadata['total_results']
            articles=[
                    Article(
                    search = recent_searches,
                    title=article['title'],
                    description=article['description'],
                    content=article['content'],
                    author=article['author'],
                    source=article['source'],
                    url=article['url'],
                    publishedAt=datetime.fromisoformat(article['publishedAt'][:-1])
                     ) for article in new_results['articles'] if article['title'] !='[Removed]'
                ]
            Article.objects.bulk_create(articles)
            recent_searches.date = datetime.now()
            recent_searches.save()
            refreshed_result = Article.objects.filter(search=recent_searches).all()
            articleFilter = ArticleFilter(request.GET,queryset=refreshed_result)
            refreshed_result = articleFilter.qs
        return render(request, "index.html",{'data':refreshed_result,'search_metadata':recent_searches.metadata,'articleFilter':articleFilter})
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
    next_page = request.GET.get('next', '')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            expiration_time = datetime.now() + timedelta(minutes=30)  # Set an expiration time (adjust as needed)
            expiration_time = expiration_time.strftime('%a, %d-%b-%Y %H:%M:%S')
            response = redirect(next_page if next_page else 'index') 
            response.set_cookie('user_authenticated', 'true', expires=expiration_time)
            response.set_cookie('username', user.username, expires=expiration_time)
            return response
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    response = redirect(login_view)
    response.delete_cookie('user_authenticated')
    response.delete_cookie('username')
    return response
