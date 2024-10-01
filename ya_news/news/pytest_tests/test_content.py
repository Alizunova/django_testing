from django.conf import settings
from django.urls import reverse
from news.models import Comment
import pytest
from conftest import HOME_URL


@pytest.mark.django_db
def test_news_count(client, list_news):
    """10 новостей на главной странице."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_news):
    """
    Новости отсортированы от самой
    свежей к самой старой.Свежие
    новости в начале списка.
    """
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, list_comments):
    """
    Комментарии на странице отдельной новости
    отсортированы в хронологическом порядке:
    старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news = response.context['news']
    all_comments = [comment.created for comment in Comment.objects.all()]
    sorted_dates = sorted(all_comments, reverse=False)
    assert all_comments == sorted_dates


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    )
)
@pytest.mark.django_db
def test_anonymous_client_has_no_form(parametrized_client, status, comment):
    """
    Анонимному пользователю недоступна форма для отправки комментария на
    странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', args=(comment.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is status
