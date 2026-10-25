import unittest
from api.index import app
from api.db import reset_mock_data, get_db_connection

class EsportsApiTestCase(unittest.TestCase):
    def setUp(self):
        """Reset mock data state sebelum setiap tes untuk menjamin independensi tes."""
        self.client = app.test_client()
        reset_mock_data()

    def test_01_root_endpoint(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get('status'), 'success')
        self.assertIn('endpoints', res.json)
        self.assertIn('tournaments', res.json['endpoints'])

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
        self.assertIsInstance(res.json['data']['registered_teams'], list)

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
        self.assertEqual(res.json['data']['max_teams'], 20)

    def test_08_create_tournament_missing_name(self):
        res = self.client.post('/api/tournaments', json={"max_teams": 16})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')
        self.assertIn("Field 'name'", res.json.get('message', ''))

    def test_09_create_tournament_invalid_max_teams(self):
        res = self.client.post('/api/tournaments', json={"name": "Bad Tourney", "max_teams": 0})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')

    def test_10_create_tournament_boolean_max_teams(self):
        res = self.client.post('/api/tournaments', json={"name": "Bool Tourney", "max_teams": True})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')

    def test_11_create_tournament_non_dict_body(self):
        res = self.client.post('/api/tournaments', data="not json", content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')

    def test_12_update_tournament_success(self):
        res = self.client.put('/api/tournaments/1', json={"status": "completed", "max_teams": 32})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data']['status'], 'completed')
        self.assertEqual(res.json['data']['max_teams'], 32)

    def test_13_update_tournament_not_found(self):
        res = self.client.put('/api/tournaments/9999', json={"status": "completed"})
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json.get('status'), 'error')

    def test_14_update_tournament_invalid_max_teams(self):
        res = self.client.put('/api/tournaments/1', json={"max_teams": -5})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')

    def test_15_update_tournament_boolean_max_teams(self):
        res = self.client.put('/api/tournaments/1', json={"max_teams": True})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')

    def test_16_update_tournament_empty_name(self):
        res = self.client.put('/api/tournaments/1', json={"name": "   "})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')

    def test_17_update_tournament_non_dict_body(self):
        res = self.client.put('/api/tournaments/1', data="invalid", content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json.get('status'), 'error')

    def test_18_delete_tournament_conflict(self):
        # Tournament ID 1 memiliki pendaftaran tim aktif di mock -> harus 409 Conflict
        res = self.client.delete('/api/tournaments/1')
        self.assertEqual(res.status_code, 409)
        self.assertEqual(res.json.get('status'), 'error')
        self.assertIn("Relational Integrity Conflict", res.json.get('message', ''))

    def test_19_delete_tournament_not_found(self):
        res = self.client.delete('/api/tournaments/9999')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json.get('status'), 'error')

    def test_20_delete_tournament_success(self):
        # Tournament ID 4 (Community Shield Cup 2026) tidak memiliki pendaftaran -> 200 OK
        res = self.client.delete('/api/tournaments/4')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get('status'), 'success')
        self.assertIn("berhasil dihapus", res.json.get('message', ''))

    def test_21_delete_tournament_lifecycle(self):
        # Siklus lengkap: Buat turnamen baru tanpa registrasi lalu hapus -> 200 OK
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

    def test_22_get_matches(self):
        res = self.client.get('/api/matches')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json.get('total', 0), 0)
        self.assertIn('team_a_name', res.json['data'][0])

    def test_23_get_registrations(self):
        res = self.client.get('/api/registrations')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json.get('total', 0), 0)
        self.assertIn('tournament_name', res.json['data'][0])

    def test_24_get_tournaments_filter_status(self):
        res = self.client.get('/api/tournaments?status=open')
        self.assertEqual(res.status_code, 200)
        for t in res.json.get('data', []):
            self.assertEqual(t.get('status').lower(), 'open')

    def test_25_get_tournaments_filter_status_empty(self):
        res = self.client.get('/api/tournaments?status=cancelled')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get('total'), 0)
        self.assertEqual(len(res.json.get('data')), 0)

    def test_26_get_tournaments_search(self):
        res = self.client.get('/api/tournaments?search=valorant')
        self.assertEqual(res.status_code, 200)
        for t in res.json.get('data', []):
            self.assertIn('valorant', t.get('name').lower())

    def test_27_get_tournaments_search_empty(self):
        res = self.client.get('/api/tournaments?search=xyznotfound')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get('total'), 0)
        self.assertEqual(len(res.json.get('data')), 0)

    def test_28_custom_404_handler(self):
        res = self.client.get('/api/route_tidak_ada')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json.get('status'), 'error')

    def test_29_method_not_allowed_405(self):
        res = self.client.post('/api/health')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json.get('status'), 'error')

    def test_30_cors_headers(self):
        res = self.client.get('/')
        self.assertIn('Access-Control-Allow-Origin', res.headers)
        self.assertEqual(res.headers.get('Access-Control-Allow-Origin'), '*')

    def test_31_options_preflight(self):
        res = self.client.open('/', method='OPTIONS')
        self.assertEqual(res.status_code, 204)
        self.assertIn('Access-Control-Allow-Methods', res.headers)

    def test_32_vercel_path_middleware(self):
        # Uji query param __path yang dipassing oleh rewrite Vercel
        res = self.client.get('/?__path=/api/tournaments')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get('status'), 'success')
        self.assertGreater(res.json.get('total', 0), 0)

    def test_33_dual_routing_without_api_prefix(self):
        # Uji dual-routing decorator: /tournaments langsung tanpa /api
        res = self.client.get('/tournaments')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get('status'), 'success')

    def test_34_mock_data_isolation(self):
        # Tes isolasi mock: mutasi data di satu tes tidak boleh bocor ke tes lain
        res1 = self.client.get('/api/tournaments')
        initial_total = res1.json['total']
        self.client.post('/api/tournaments', json={"name": "Temp Iso", "max_teams": 8})
        res2 = self.client.get('/api/tournaments')
        self.assertEqual(res2.json['total'], initial_total + 1)
        # Panggil reset_mock_data langsung
        reset_mock_data()
        res3 = self.client.get('/api/tournaments')
        self.assertEqual(res3.json['total'], initial_total)

if __name__ == '__main__':
    unittest.main()
