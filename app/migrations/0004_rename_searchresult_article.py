# Generated by Django 4.2.6 on 2023-10-11 17:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_searchresult_search_result_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SearchResult',
            new_name='Article',
        ),
    ]
