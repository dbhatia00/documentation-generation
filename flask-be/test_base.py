import unittest
from base import app
import json


class TestBase(unittest.TestCase):

    def test_get_doc(self):
        # Define a test payload, will error out (DNE)
        payload = {'repo_url': 'username/repo'}

        # Make a POST request to the endpoint
        with app.test_client() as client:
            response = client.post('/api/get_doc', json=payload)
            
            # Check the response status code
            self.assertEqual(response.status_code, 500)


    def test_get_access_token(self):
        # Define a test query parameter
        query_param = {'code': 'sample_code'}

        # Make a GET request to the endpoint
        with app.test_client() as client:
            response = client.get('/api/get_access_token', query_string=query_param)
            
            # Check the response status code
            self.assertIn(response.status_code, [200, 500])

    def test_get_confluence_token(self):
        # Define a test query parameter
        query_param = {'code': 'sample_code'}

        # Make a GET request to the endpoint
        with app.test_client() as client:
            response = client.get('/api/get_confluence_token', query_string=query_param)
            
            # Check the response status code
            self.assertIn(response.status_code, [200, 500])

    def test_create_confluence(self):
        # Define a test payload
        payload = {
            'confluence_domain': 'sample_domain',
            'repo_url': 'username/repo',
            'email': 'sample_email',
            'api_token': 'sample_token'
        }

        # Make a POST request to the endpoint
        with app.test_client() as client:
            response = client.post('/api/create_confluence', json=payload)
            
            # Check the response status code
            self.assertIn(response.status_code, [200, 400])


if __name__ == '__main__':
    unittest.main()
