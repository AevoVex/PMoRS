import io
import tempfile
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from lessons.serializers import InitialPostSerializer
from posts.models import Group, Post


@override_settings(ROOT_URLCONF='lessons.urls_functions')
class PostAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user('writer', password='Writer-42-pass!')
        cls.other = get_user_model().objects.create_user('reader', password='Reader-42-pass!')
        cls.token = Token.objects.create(user=cls.author)
        cls.other_token = Token.objects.create(user=cls.other)
        cls.group = Group.objects.create(title='Коты', slug='cats')
        cls.post = Post.objects.create(text='Привет, мир!', author=cls.author, group=cls.group)

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/api/v1/posts/{self.post.pk}/'

    def test_token_login_and_wrong_password(self):
        self.client.credentials()
        response = self.client.post('/api/v1/api-token-auth/', {'username': 'writer', 'password': 'Writer-42-pass!'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['token'], self.token.key)
        self.assertEqual(self.client.post('/api/v1/api-token-auth/', {'username': 'writer', 'password': 'wrong'}).status_code, 400)

    def test_anonymous_and_invalid_token_denied(self):
        self.client.credentials()
        self.assertEqual(self.client.get('/api/v1/posts/').status_code, 401)
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid')
        self.assertEqual(self.client.get('/api/v1/posts/').status_code, 401)

    def test_list_detail_and_character_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['group'], 'cats')
        self.assertEqual(response.data['character_quantity'], len(self.post.text))
        self.assertEqual(self.client.get('/api/v1/posts/').data[0]['id'], self.post.pk)

    def test_create_assigns_author_and_preserves_whitespace(self):
        text = '  Привет\nмир!  '
        response = self.client.post('/api/v1/posts/', {'text': text, 'author': self.other.pk, 'group': 'cats'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], self.author.pk)
        self.assertEqual(response.data['text'], text)
        self.assertEqual(response.data['character_quantity'], len(text))

    def test_optional_group_unknown_group_and_clearing(self):
        response = self.client.post('/api/v1/posts/', {'text': 'Без группы'})
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data['group'])
        self.assertEqual(self.client.patch(self.url, {'group': 'missing'}).status_code, 400)
        self.assertIsNone(self.client.patch(self.url, {'group': None}).data['group'])

    def test_patch_put_delete_by_author(self):
        response = self.client.patch(self.url, {'text': 'Обновление', 'author': self.other.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['author'], self.author.pk)
        self.assertEqual(self.client.put(self.url, {'text': 'Полный текст', 'group': 'cats'}).status_code, 200)
        self.assertEqual(self.client.delete(self.url).status_code, 204)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_other_user_can_read_but_cannot_mutate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.other_token.key}')
        self.assertEqual(self.client.get(self.url).status_code, 200)
        for method in ['patch', 'put', 'delete']:
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url, {'text': 'Подмена'})
                self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Привет, мир!')

    def test_bad_input_and_methods(self):
        for data in [{}, {'text': ''}, {'text': '   '}]:
            self.assertEqual(self.client.post('/api/v1/posts/', data).status_code, 400)
        self.assertEqual(self.client.put(self.url, {}).status_code, 400)
        self.assertEqual(self.client.get('/api/v1/posts/9999/').status_code, 404)
        self.assertEqual(self.client.delete('/api/v1/posts/').status_code, 405)

    def test_groups_are_read_only(self):
        self.assertEqual(self.client.get('/api/v1/groups/').data[0]['slug'], 'cats')
        self.assertEqual(self.client.post('/api/v1/groups/', {'title': 'x', 'slug': 'x'}).status_code, 405)

    def test_image_upload(self):
        stream = io.BytesIO()
        Image.new('RGB', (2, 2), color='white').save(stream, format='PNG')
        upload = SimpleUploadedFile('cat.png', stream.getvalue(), content_type='image/png')
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            response = self.client.post('/api/v1/posts/', {'text': 'Фото', 'image': upload}, format='multipart')
            self.assertEqual(response.status_code, 201)
            self.assertIn('/media/posts/', response.data['image'])

    def test_initial_serializer_excludes_id(self):
        self.assertEqual(set(InitialPostSerializer(self.post).data), {'text', 'author', 'pub_date'})

    @override_settings(ROOT_URLCONF='lessons.urls_apiview')
    def test_apiview_lesson(self):
        self.assertEqual(self.client.get('/api/v1/posts/').status_code, 200)
        self.assertEqual(self.client.post('/api/v1/posts/', {'text': 'APIView'}).status_code, 201)
        self.assertEqual(self.client.delete('/api/v1/posts/').status_code, 405)

    @override_settings(ROOT_URLCONF='lessons.urls_viewset')
    def test_viewset_lesson_crud_and_permissions(self):
        response = self.client.post('/api/v1/posts/', {'text': 'ViewSet'})
        self.assertEqual(response.status_code, 201)
        url = f'/api/v1/posts/{response.data["id"]}/'
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.put(url, {'text': 'PUT'}).status_code, 200)
        self.assertEqual(self.client.patch(url, {'text': 'PATCH'}).status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.other_token.key}')
        self.assertEqual(self.client.delete(url).status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(self.client.delete(url).status_code, 204)
