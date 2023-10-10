from django.db import models
from django.contrib.auth.models import User

# Model for tracking the search history of users
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        formatted_date = self.date.strftime('%B %d, %Y %I:%M %p')
        return f"{self.user.username} - query: {self.query}, {formatted_date}"
    
    
# Model to store search result data
class SearchResult(models.Model):
    search = models.ForeignKey(SearchHistory, on_delete=models.CASCADE)
    search_result = models.JSONField(null=True)
    def __str__(self):
        return f"{self.search.query}"