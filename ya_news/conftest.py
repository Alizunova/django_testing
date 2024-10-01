from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.test.client import Client
import pytest
from django.urls import reverse
from news.models import News, Comment

COMMENT_TEXT = 'Текст комментария'
HOME_URL = reverse('news:home')


@pytest.fixture
def author(django_user_model):
    """Создание пользователя автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Регистрация пользователя автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author(django_user_model):
    """Создание обычного пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def not_author_client(not_author):
    """Регистрация обычного пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Создание новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def comment(news, author):
    """Создание комментария."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )
    return comment


@pytest.fixture
def list_news():
    """Создание списка новостей."""
    today, list_news = datetime.today(), []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        news = News.objects.create(
            title='Новость {index}',
            text='Текст новости',
        )
        news.date = today - timedelta(days=index)
        news.save()
        list_news.append(news)
    return list_news


@pytest.fixture
def list_comments(news, author):
    """Создание списка комментариев."""
    now, list_comment = timezone.now(), []
    for index in range(10):
        comment = Comment.objects.create(
            text='Текст комментария {index}',
            news=news,
            author=author,
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        list_comment.append(comment)


@pytest.fixture
def form_data():
    """Новый текст комментария."""
    return {'text': 'Новый текст комментария'}
