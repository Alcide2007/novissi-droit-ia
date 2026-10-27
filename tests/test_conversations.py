import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "backend"))
from conversations import Store, make_title

A, B = "owner-aaaaaaaa", "owner-bbbbbbbb"


class ConvTests(unittest.TestCase):
    def setUp(self):
        self.s = Store(":memory:")

    def test_title_from_first_question(self):
        c = self.s.create(A)
        self.s.add_message(A, c["id"], "u", "Mon patron ne me paie pas")
        self.assertEqual(self.s.list(A)[0]["title"], "Mon patron ne me paie pas")

    def test_long_title_truncated(self):
        self.assertTrue(make_title("x" * 200).endswith("…"))
        self.assertLessEqual(len(make_title("x" * 200)), 61)

    def test_messages_and_sources_roundtrip(self):
        c = self.s.create(A)
        self.s.add_message(A, c["id"], "a", "ok", [{"id": 1, "ref": "Code du travail - Art. 1"}], "n", "ia")
        m = self.s.messages(A, c["id"])[0]
        self.assertEqual(m["sources"][0]["ref"], "Code du travail - Art. 1")

    def test_isolation_between_owners(self):
        c = self.s.create(A)
        self.assertIsNone(self.s.messages(B, c["id"]))
        self.assertFalse(self.s.add_message(B, c["id"], "u", "x"))
        self.assertFalse(self.s.rename(B, c["id"], "pirate"))
        self.assertFalse(self.s.delete(B, c["id"]))
        self.assertEqual(self.s.list(B), [])

    def test_search_by_title_and_content(self):
        c = self.s.create(A, "Bail")
        self.s.add_message(A, c["id"], "u", "expulsion du locataire")
        self.assertEqual(len(self.s.list(A, "locataire")), 1)
        self.assertEqual(len(self.s.list(A, "zzz")), 0)

    def test_delete_cascades(self):
        c = self.s.create(A)
        self.s.add_message(A, c["id"], "u", "bonjour")
        self.assertTrue(self.s.delete(A, c["id"]))
        self.assertIsNone(self.s.messages(A, c["id"]))
        self.assertEqual(self.s._db.execute("SELECT COUNT(*) FROM messages").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
