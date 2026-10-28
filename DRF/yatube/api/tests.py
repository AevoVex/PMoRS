from django.contrib import admin
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from posts.models import Comment, Group, Post


class NestedCommentTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.writer = get_user_model().objects.create_user('writer')
        cls.reader = get_user_model().objects.create_user('reader')
        cls.staff = get_user_model().objects.create_user('staff', is_staff=True, is_superuser=True)
        cls.post = Post.objects.create(author=cls.writer, text='Post one')
        cls.other_post = Post.objects.create(author=cls.reader, text='Post two')
        cls.comment = Comment.objects.create(author=cls.reader, post=cls.post, text='Comment')
        cls.token = Token.objects.create(user=cls.reader)

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.list_url = f'/api/v1/posts/{self.post.pk}/comments/'
        self.detail_url = f'{self.list_url}{self.comment.pk}/'

    def test_comment_under_wrong_existing_post_is_not_found(self):
        wrong_url = f'/api/v1/posts/{self.other_post.pk}/comments/{self.comment.pk}/'
        for method in ['get', 'put', 'patch', 'delete']:
            with self.subTest(method=method):
                response = getattr(self.client, method)(wrong_url, {'text': 'Wrong parent'})
                self.assertEqual(response.status_code, 404)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Comment')

    def test_missing_parent_returns_404_even_for_empty_post(self):
        missing = '/api/v1/posts/99999/comments/'
        for method, payload in [('get', {}), ('post', {}), ('post', {'text': 'New'})]:
            self.assertEqual(getattr(self.client, method)(missing, payload).status_code, 404)
        self.assertEqual(Comment.objects.count(), 1)

    def test_parent_and_author_spoofing_are_ignored(self):
        payload = {'text': 'New', 'post': self.other_post.pk, 'author': 'writer'}
        created = self.client.post(self.list_url, payload)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['post'], self.post.pk)
        self.assertEqual(created.data['author'], 'reader')
        updated = self.client.patch(self.detail_url, payload)
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data['post'], self.post.pk)
        self.assertEqual(updated.data['author'], 'reader')

    def test_post_owner_and_admin_cannot_edit_someone_elses_comment(self):
        for user in [self.writer, self.staff]:
            token = Token.objects.create(user=user)
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
            for method in ['patch', 'put', 'delete']:
                with self.subTest(user=user.username, method=method):
                    self.assertEqual(getattr(self.client, method)(self.detail_url, {'text': 'Changed'}).status_code, 403)

    def test_comment_list_is_scoped_to_parent(self):
        Comment.objects.create(author=self.reader, post=self.other_post, text='Other')
        self.assertEqual([c['id'] for c in self.client.get(self.list_url).data], [self.comment.pk])

    def test_delete_post_cascades_comments(self):
        token = Token.objects.create(user=self.writer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(self.client.delete(f'/api/v1/posts/{self.post.pk}/').status_code, 204)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_numeric_routes_reject_nonnumeric_parent(self):
        for value in ['abc', '-1', '1.5']:
            self.assertEqual(self.client.get(f'/api/v1/posts/{value}/comments/').status_code, 404)

    def test_all_models_registered_in_admin(self):
        for model in [Post, Group, Comment]:
            self.assertTrue(admin.site.is_registered(model))

    def test_drf2_post_contract(self):
        group = Group.objects.create(title='Cats', slug='cats')
        response = self.client.post('/api/v1/posts/', {'text': 'New', 'group': group.pk, 'author': 'writer'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], 'reader')
        self.assertEqual(response.data['group'], group.pk)
        self.assertEqual(set(response.data), {'id', 'text', 'author', 'image', 'group', 'pub_date'})
        self.assertEqual(self.client.post('/api/v1/posts/', {'text': 'Wrong group type', 'group': 'cats'}).status_code, 400)
