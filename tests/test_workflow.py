import contextlib
import io
import unittest
from unittest.mock import Mock
from config import Config
from graph_client import GraphClient, GraphError
from page_service import PageService
from publishing_service import preview_post
from main import main

class WorkflowTests(unittest.TestCase):
    def test_pagination_never_follows_external_url_or_exposes_token(self):
        client = Mock()
        client.get.side_effect = [
            {'data': [{'id': '1', 'name': 'A', 'access_token': 'SECRET'}],
             'paging': {'next': 'https://evil.example/?access_token=SECRET', 'cursors': {'after': 'cursor'}}},
            {'data': [{'id': '2', 'name': 'B'}]},
        ]
        pages = PageService(client, 'USER_SECRET').list_pages()
        self.assertEqual(len(pages), 2)
        self.assertNotIn('SECRET', str(pages))
        self.assertEqual(client.get.call_args.args[0], 'me/accounts')
        self.assertEqual(client.get.call_args.args[2]['after'], 'cursor')

    def test_preview_rejects_unmanaged_page(self):
        with self.assertRaises(ValueError):
            preview_post('2', 'hello', [{'id': '1', 'name': 'A'}])

    def test_retry_get_and_authorization_header(self):
        session = Mock()
        first = Mock(status_code=429, headers={'Retry-After': '1'})
        second = Mock(status_code=200)
        second.json.return_value = {'data': []}
        session.get.side_effect = [first, second]
        sleep = Mock()
        self.assertEqual(GraphClient(Config('v99.0'), session, sleep).get('me/accounts', 'SECRET'), {'data': []})
        sleep.assert_called_once_with(1)
        self.assertFalse(session.get.call_args.kwargs['allow_redirects'])
        self.assertEqual(session.get.call_args.kwargs['headers']['Authorization'], 'Bearer SECRET')

    def test_error_does_not_expose_remote_message(self):
        session = Mock()
        response = Mock(status_code=400)
        response.json.return_value = {'error': {'code': 190, 'message': 'SECRET'}}
        session.get.return_value = response
        with self.assertRaises(GraphError) as error:
            GraphClient(Config('v99.0'), session).get('me/accounts', 'SECRET')
        self.assertNotIn('SECRET', str(error.exception))

    def test_demo_preview_without_network_or_token(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['--demo', 'preview', '--page-id', '123456789', '--message-file', 'message.example.txt'])
        self.assertEqual(code, 0)
        self.assertIn('"network_write": false', output.getvalue())

    def test_repeated_cursor_fails(self):
        client = Mock()
        client.get.return_value = {'data': [], 'paging': {'next': 'next', 'cursors': {'after': 'same'}}}
        with self.assertRaises(GraphError):
            PageService(client, 'SECRET').list_pages()

if __name__ == '__main__':
    unittest.main()
