from typing import cast
import newspaper

news = newspaper.build(
    url="http://svt.se/",
)
newspaper.Source()

print(news.article_urls())

for article in news.articles:
    article = cast(newspaper.Article, article)
    article.download()
    article.parse()
    # article.nlp()
    print(article.title)#, article.keywords)