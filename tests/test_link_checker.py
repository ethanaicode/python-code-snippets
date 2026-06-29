import importlib.util
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT_DIR / "tools" / "link_checker.py"

spec = importlib.util.spec_from_file_location("link_checker", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"无法加载模块: {MODULE_PATH}")

link_checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = link_checker
spec.loader.exec_module(link_checker)

LinkChecker = link_checker.LinkChecker
collect_urls = link_checker.collect_urls
extract_urls_from_text = link_checker.extract_urls_from_text
load_urls_from_file = link_checker.load_urls_from_file
parse_status_spec = link_checker.parse_status_spec


class _LinkHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        if self.path == "/head-only":
            self.send_response(405)
            self.end_headers()
            return

        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
            return

        if self.path == "/bad":
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
            return

        if self.path == "/bad":
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        return


class LinkCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _LinkHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base_url = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_extract_urls_from_text(self):
        text = "see https://example.com and https://github.com, plus https://example.com"
        self.assertEqual(
            extract_urls_from_text(text),
            ["https://example.com", "https://github.com"],
        )

    def test_load_urls_from_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "urls.txt"
            file_path.write_text(
                "https://example.com\nhttps://github.com\nhttps://example.com",
                encoding="utf-8",
            )

            self.assertEqual(
                load_urls_from_file(str(file_path)),
                ["https://example.com", "https://github.com"],
            )

    def test_collect_urls_merges_inputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "urls.md"
            file_path.write_text("https://example.com\n", encoding="utf-8")

            urls = collect_urls(
                ["https://github.com", "https://example.com"],
                [str(file_path)],
                False,
            )

            self.assertEqual(urls, ["https://github.com", "https://example.com"])

    def test_parse_status_spec(self):
        self.assertIn(200, parse_status_spec("200-399"))
        self.assertIn(302, parse_status_spec("2xx,301-399"))
        self.assertIn(404, parse_status_spec("404"))

    def test_batch_check_with_head_fallback(self):
        urls = [
            f"{self.base_url}/ok",
            f"{self.base_url}/head-only",
            f"{self.base_url}/bad",
            f"{self.base_url}/redirect",
        ]

        checker = LinkChecker(timeout=2, method="HEAD")
        results = checker.check_urls(urls, concurrency=2)

        self.assertEqual(len(results), 4)
        self.assertTrue(results[0].ok)
        self.assertTrue(results[1].ok)
        self.assertEqual(results[1].method_used, "GET")
        self.assertFalse(results[2].ok)
        self.assertEqual(results[2].status_code, 404)
        self.assertTrue(results[3].ok)
        self.assertTrue(results[3].redirected)
        self.assertTrue(results[3].final_url.endswith("/ok"))
        self.assertEqual(results[3].redirect_chain, [f"{self.base_url}/redirect", f"{self.base_url}/ok"])

    def test_redirect_tracing_can_be_disabled(self):
        checker = LinkChecker(timeout=2, method="HEAD", trace_redirects=False)
        result = checker.check_urls([f"{self.base_url}/redirect"], concurrency=1)[0]

        self.assertTrue(result.ok)
        self.assertTrue(result.redirected)
        self.assertEqual(result.final_url, f"{self.base_url}/redirect")
        self.assertEqual(result.redirect_chain, [])


if __name__ == "__main__":
    unittest.main()