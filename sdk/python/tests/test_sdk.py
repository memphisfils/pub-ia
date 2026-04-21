import json
import pathlib
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from pub_ia_sdk import DEFAULT_ENDPOINT, PubIA, PubIAError


class _SdkRequestHandler(BaseHTTPRequestHandler):
    requests = []

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(payload or "{}")

        type(self).requests.append(
            {
                "path": self.path,
                "headers": dict(self.headers),
                "body": data,
            }
        )

        if self.path == "/v1/analyze-intent":
            self._write_json(
                200,
                {
                    "has_intent": True,
                    "intent": "achat_tech",
                    "confidence": 0.87,
                    "category": "tech",
                    "intent_id": "intent_123",
                },
            )
            return

        if self.path == "/v1/get-ad":
            self._write_json(
                200,
                {
                    "ad_id": "ad_123",
                    "headline": "Ultra Laptop",
                    "body": "Le meilleur laptop pour travailler.",
                    "cta_text": "Voir l'offre",
                    "cta_url": "https://example.com/ad",
                    "native_text": "Essayez Ultra Laptop.",
                    "impression_id": "imp_123",
                },
            )
            return

        if self.path == "/v1/track-click":
            self._write_json(200, {"tracked": True})
            return

        if self.path == "/v1/unauthorized":
            self._write_json(401, {"error": "Invalid or missing API key"})
            return

        self._write_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        return

    def _write_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class PubIASdkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _SdkRequestHandler.requests = []
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _SdkRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        _SdkRequestHandler.requests = []

    def test_default_endpoint_is_absolute(self):
        self.assertEqual(DEFAULT_ENDPOINT, "https://pub-ia.io/v1")

    def test_full_sdk_flow_with_origin_endpoint(self):
        client = PubIA(api_key="pk_live_test", endpoint=self.base_url, app_id="app_123")

        intent = client.analyze_intent("Quel laptop acheter ?", context="ordinateur portable")
        ad = client.get_ad(intent)
        tracked = client.track_click("imp_123")

        self.assertTrue(intent["has_intent"])
        self.assertEqual(intent["intent_id"], "intent_123")
        self.assertIsNotNone(ad)
        self.assertEqual(ad["impression_id"], "imp_123")
        self.assertTrue(tracked)

        self.assertEqual(
            [request["path"] for request in _SdkRequestHandler.requests],
            ["/v1/analyze-intent", "/v1/get-ad", "/v1/track-click"],
        )
        self.assertEqual(
            _SdkRequestHandler.requests[0]["headers"].get("X-PubIA-App-Id"),
            "app_123",
        )
        self.assertEqual(
            _SdkRequestHandler.requests[0]["body"],
            {"prompt": "Quel laptop acheter ?", "context": "ordinateur portable"},
        )

        client.close()

    def test_full_sdk_flow_with_v1_endpoint_and_camel_case_intent(self):
        client = PubIA(api_key="pk_live_test", endpoint=f"{self.base_url}/v1")

        ad = client.get_ad(
            {
                "hasIntent": True,
                "intent": "achat_tech",
                "confidence": 0.5,
                "intentId": "intent_456",
            }
        )

        self.assertIsNotNone(ad)
        self.assertEqual(
            [request["path"] for request in _SdkRequestHandler.requests],
            ["/v1/get-ad"],
        )
        self.assertEqual(
            _SdkRequestHandler.requests[0]["body"],
            {
                "intent": "achat_tech",
                "intent_id": "intent_456",
                "confidence": 0.5,
            },
        )

        client.close()

    def test_clear_error_when_not_initialized(self):
        client = PubIA()

        with self.assertRaises(PubIAError) as raised:
            client.analyze_intent("test")

        self.assertIn("not initialized", str(raised.exception))

    def test_http_error_payload_is_exposed(self):
        client = PubIA(api_key="pk_live_test", endpoint=self.base_url)

        with self.assertRaises(PubIAError) as raised:
            client._request("/unauthorized", {})

        self.assertEqual(raised.exception.status, 401)
        self.assertEqual(str(raised.exception), "Invalid or missing API key")

        client.close()

    def test_invalid_endpoint_is_rejected(self):
        with self.assertRaises(PubIAError) as raised:
            PubIA(api_key="pk_live_test", endpoint="/v1")

        self.assertIn("absolute URL", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
