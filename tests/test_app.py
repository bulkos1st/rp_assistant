import unittest
from app import app

class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    # executed after each test
    def tearDown(self):
        pass

    # Test for homepage route
    def test_homepage(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Load devices from Restore Point', response.data)

    # def test_get_resource(self):
    #     response = self.app.get('/api/resource')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Resource Data', response.data)

    def test_post_resource(self):
        data = {'delete_ips': '1.1.1.1'}
        response = self.app.post('/confirm_delete', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Confirm Device Deletion', response.data)


if __name__ == "__main__":
    unittest.main()