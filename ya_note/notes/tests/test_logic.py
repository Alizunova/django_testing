from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertTrue(Note.objects.exists())
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.client.post(self.url, self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, redirect_url)
        self.assertFalse(Note.objects.exists())

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertTrue(Note.objects.exists())

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug,
        то он формируется автоматически.
        """
        self.form_data.pop('slug')
        response = self.author_client.post(self.url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertTrue(Note.objects.exists())
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertFalse(Note.objects.exists())

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.exists())

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.reader_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.form_data['title'])
        self.assertNotEqual(self.note.text, self.form_data['text'])
        self.assertNotEqual(self.note.slug, self.form_data['slug'])
