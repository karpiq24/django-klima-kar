from django.contrib import admin
from apps.wiki.models import Article, Tag, ExternalLink, ArticleFile

admin.site.register(Article)
admin.site.register(Tag)
admin.site.register(ExternalLink)
admin.site.register(ArticleFile)
