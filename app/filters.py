import django_filters

from .models import *

class SearchResultFilter(django_filters.FilterSet):
    class Meta:
        model = SearchResult
        fields = '__all__'
        exclude = ['search_result']