import unittest
from api.index import app

class EsportsApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_01_root_endpoint(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get('status'), 'success')
        self.assertIn('endpoints', res.json)

    def test_02_health_check(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get('status'), 'healthy')
        self.assertIn('database', res.json)

    def test_03_get_teams(self):
        res = self.client.get('/api/teams')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json.get('total', 0), 0)
        self.assertIsInstance(res.json.get('data'), list)

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
        self.assertEqual(res.json.get('status'), 'error')

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
        self.assertEqual(res.json.get('status'), 'error')

    def test_09_create_tournament_invalid_max_teams(self):
        res = self.client.post('/api/tournaments', json={"name": "Bad Tourney", "max_teams": 0})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')

    def test_10_update_tournament_success(self):
        res = self.client.put('/api/tournaments/1', json={"status": "completed"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data']['status'], 'completed')

    def test_11_update_tournament_not_found(self):
        res = self.client.put('/api/tournaments/9999', json={"status": "completed"})
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json.get('status'), 'error')

    def test_12_update_tournament_invalid_max_teams(self):
        res = self.client.put('/api/tournaments/1', json={"max_teams": -5})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')

    def test_13_delete_tournament_conflict(self):
        # Tournament ID 1 memiliki pendaftaran tim aktif di mock -> harus 409 Conflict
        res = self.client.delete('/api/tournaments/1')
        self.assertEqual(res.status_code, 409)
        self.assertEqual(res.json.get('status'), 'error')

    def test_14_delete_tournament_not_found(self):
        res = self.client.delete('/api/tournaments/9999')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json.get('status'), 'error')

    def test_15_delete_tournament_success(self):
        # Buat turnamen baru tanpa registrasi lalu hapus -> 200 OK
        create_res = self.client.post('/api/tournaments', json={
            "name": "Temporary Deletable Cup",
            "format": "Single Elimination",
            "max_teams": 4
        })
        self.assertEqual(create_res.status_code, 201)
        created_id = create_res.json['data']['id']

        del_res = self.client.delete(f'/api/tournaments/{created_id}')
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.json.get('status'), 'success')

    def test_16_get_matches(self):
        res = self.client.get('/api/matches')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json.get('total', 0), 0)

    def test_17_get_registrations(self):
        res = self.client.get('/api/registrations')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json.get('total', 0), 0)

    def test_18_get_tournaments_filter_status(self):
        res = self.client.get('/api/tournaments?status=open')
        self.assertEqual(res.status_code, 200)
        for t in res.json.get('data', []):
            self.assertEqual(t.get('status').lower(), 'open')

    def test_19_get_tournaments_search(self):
        res = self.client.get('/api/tournaments?search=valorant')
        self.assertEqual(res.status_code, 200)
        for t in res.json.get('data', []):
            self.assertIn('valorant', t.get('name').lower())

    def test_20_custom_404_handler(self):
        res = self.client.get('/api/route_tidak_ada')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json.get('status'), 'error')

    def test_21_cors_headers(self):
        res = self.client.get('/')
        self.assertIn('Access-Control-Allow-Origin', res.headers)
        self.assertEqual(res.headers.get('Access-Control-Allow-Origin'), '*')

    def test_22_options_preflight(self):
        res = self.client.open('/', method='OPTIONS')
        self.assertEqual(res.status_code, 204)
        self.assertIn('Access-Control-Allow-Methods', res.headers)

if __name__ == '__main__':
    unittest.main()
