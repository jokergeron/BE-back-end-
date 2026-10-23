import unittest
from api.index import app

class EsportsApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_01_root_endpoint(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get('status'), 'success')

    def test_02_health_check(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        self.assertIn('database', res.json)

    def test_03_get_teams(self):
        res = self.client.get('/api/teams')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json.get('total', 0), 0)

    def test_04_get_tournaments(self):
        res = self.client.get('/api/tournaments')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json.get('total', 0), 0)

    def test_05_get_tournament_detail_success(self):
        res = self.client.get('/api/tournaments/1')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data']['id'], 1)
        self.assertIn('registered_teams', res.json['data'])

    def test_06_get_tournament_detail_not_found(self):
        res = self.client.get('/api/tournaments/9999')
        self.assertEqual(res.status_code, 404)

    def test_07_create_tournament_success(self):
        payload = {
            "name": "Apex Legends Global Series 2026",
            "format": "Battle Royale",
            "max_teams": 20,
            "start_date": "2026-11-20"
        }
        res = self.client.post('/api/tournaments', json=payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json['data']['name'], "Apex Legends Global Series 2026")

    def test_08_create_tournament_missing_name(self):
        res = self.client.post('/api/tournaments', json={"max_teams": 16})
        self.assertEqual(res.status_code, 400)

    def test_09_update_tournament_success(self):
        res = self.client.put('/api/tournaments/1', json={"status": "completed"})
        self.assertEqual(res.status_code, 200)

    def test_10_delete_tournament_conflict(self):
        # Tournament ID 1 memiliki pendaftaran tim aktif di mock -> harus 409 Conflict
        res = self.client.delete('/api/tournaments/1')
        self.assertEqual(res.status_code, 409)

    def test_11_get_matches(self):
        res = self.client.get('/api/matches')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json.get('total', 0), 0)

    def test_12_get_registrations(self):
        res = self.client.get('/api/registrations')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json.get('total', 0), 0)

if __name__ == '__main__':
    unittest.main()
