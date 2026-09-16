import io
import unittest

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_wikipedia_route_returns_json(self):
        response = self.client.post('/wiki', json={'query': 'Photosynthesis'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('title', data)
        self.assertIn('summary', data)

    def test_wikipedia_route_accepts_question_style_queries(self):
        response = self.client.post('/wiki', json={'query': 'What is Machine Learning? Explain with examples'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['title'], 'Machine learning')

    def test_google_source_links_have_fallback_values(self):
        from app import build_google_source_links

        links = build_google_source_links('machine learning')
        self.assertEqual(len(links), 3)
        self.assertTrue(all(link.startswith('https://www.google.com/search?') for link in links))

    def test_standard_diagram_is_always_available(self):
        from app import build_standard_diagram

        diagram = build_standard_diagram('What is machine learning?')
        self.assertTrue(diagram.startswith('flowchart TD'))
        self.assertIn('Core idea', diagram)
        self.assertIn('Conclusion', diagram)

    def test_generic_upload_route_accepts_any_file(self):
        payload = io.BytesIO(b'hello world')
        response = self.client.post(
            '/upload-file',
            data={'file': (payload, 'notes.pdf')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('filename', data)
        self.assertIn('file_type', data)

    def test_pdf_analysis_rejects_missing_file_cleanly(self):
        response = self.client.post('/analyze-file')
        self.assertEqual(response.status_code, 400)
        self.assertIn('PDF', response.get_json()['error'])


if __name__ == '__main__':
    unittest.main()
