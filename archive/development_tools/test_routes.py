import sys
import os
sys.path.insert(0, os.path.abspath("."))
import unittest
from app import app

class TestNewRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_root_dashboard_route(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(b'BloomStudio' in res.data or b'BloomEngine' in res.data)

    def test_dashboard_route(self):
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(b'BloomStudio' in res.data or b'BloomEngine' in res.data)

    def test_landing_route(self):
        res = self.client.get('/landing')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'BloomStudio', res.data)
        self.assertIn(b'Launch BloomStudio', res.data)

    def test_auth_route(self):
        res = self.client.get('/auth')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Sign In', res.data)

if __name__ == '__main__':
    unittest.main()
