import django_filters

from .models import *

class ArticleFilter(django_filters.FilterSet):
    
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    author = django_filters.ChoiceFilter(choices=[])
    source = django_filters.ChoiceFilter(choices=[])
    publishedAt = django_filters.ChoiceFilter(choices=[])

    class Meta:
        model = Article
        fields = ['title','author','source','publishedAt']
        # exclude = ['search_result']

    def __init__(self, *args, **kwargs):
        
        # print("filtersss: ",kwargs.get('queryset').values_list('title', flat=True).distinct())
        super().__init__(*args, **kwargs)
        # titles = kwargs.get('queryset').values_list('title', flat=True).distinct()
        authors = kwargs.get('queryset').values_list('author', flat=True).distinct()
        sources = kwargs.get('queryset').values_list('source', flat=True).distinct()
        publishedAt_ = kwargs.get('queryset').values_list('publishedAt', flat=True).distinct()

        # Set the choices for the title and author filters
        # self.filters['title'].extra['choices'] = [(title, title) for title in titles]
        self.filters['author'].extra['choices'] = [(author, author) for author in authors]
        self.filters['source'].extra['choices'] = [(source, source) for source in sources]
        self.filters['publishedAt'].extra['choices'] = [(publishedAt, publishedAt) for publishedAt in publishedAt_]



