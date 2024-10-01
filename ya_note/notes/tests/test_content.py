
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm
User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        """
        Oтдельная заметка передаётся на страницу
        со списком заметок в списке object_list в словаре context;
        в список заметок одного пользователя не попадают заметки
        другого пользователя.
        """
        users_statuses = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user, note_in_list in users_statuses:
            with self.subTest():
                url = reverse('notes:list')
                response = user.get(url)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        """
        На страницы создания и редактирования
        заметки передаются формы.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
