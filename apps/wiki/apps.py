from django.apps import AppConfig


class WikiConfig(AppConfig):
    name = "apps.wiki"

    def ready(self):
        from apps.search.registry import search
        from apps.audit.registry import audit
        from apps.wiki.models import Article, ExternalLink, ArticleFile, Tag

        search.register(Article)
        audit.register(Article)
        audit.register(ArticleFile)
        audit.register(ExternalLink)
        audit.register(Tag)
