"""Drift detection: on-disk and upstream blanks must match the manifest hash.

All offline — a synthetic manifest and a stubbed downloader, so the suite stays
network-free and runs in CI.
"""
import hashlib
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine import verify  # noqa: E402


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _manifest(blank: bytes):
    return {"forms": {"TEST_X": {
        "sha256": _sha(blank), "bytes": len(blank),
        "url": "https://example.test/TEST_X",
    }}}


class VerifyBlank(unittest.TestCase):
    def _write(self, root, blank):
        d = pathlib.Path(root) / "TEST_X"
        d.mkdir()
        (d / "TEST_X.pdf").write_bytes(blank)

    def test_match(self):
        blank = b"%PDF-1.7 the enriched revision\n"
        with tempfile.TemporaryDirectory() as td:
            self._write(td, blank)
            ok, detail = verify.verify_blank("TEST_X", forms_root=td, manifest=_manifest(blank))
            self.assertTrue(ok, detail)

    def test_detects_swap(self):
        blank = b"%PDF-1.7 the enriched revision\n"
        with tempfile.TemporaryDirectory() as td:
            self._write(td, b"%PDF-1.7 a DIFFERENT revision\n")
            ok, detail = verify.verify_blank("TEST_X", forms_root=td, manifest=_manifest(blank))
            self.assertFalse(ok)
            self.assertTrue("mismatch" in detail.lower() or "size" in detail.lower())

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as td:
            ok, detail = verify.verify_blank("TEST_X", forms_root=td, manifest=_manifest(b"x"))
            self.assertFalse(ok)
            self.assertIn("not present", detail)

    def test_strict_raises(self):
        with tempfile.TemporaryDirectory() as td:
            self._write(td, b"swapped")
            with self.assertRaises(verify.BlankRevisionError):
                verify.guard_blank("TEST_X", forms_root=td, mode="strict",
                                   manifest=_manifest(b"original"))

    def test_warn_does_not_raise(self):
        with tempfile.TemporaryDirectory() as td:
            self._write(td, b"swapped")
            with self.assertWarns(verify.BlankRevisionWarning):
                result = verify.guard_blank("TEST_X", forms_root=td, mode="warn",
                                            manifest=_manifest(b"original"))
            self.assertFalse(result)

    def test_off_skips(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertTrue(verify.guard_blank("TEST_X", forms_root=td, mode="off",
                                               manifest=_manifest(b"original")))


class CheckUpstream(unittest.TestCase):
    def test_classifies(self):
        import tools.check_upstream as cu
        upstream = b"%PDF-1.7 what the portal serves today\n"

        def fake_download(url, timeout, retries):
            if "gone" in url:
                raise OSError("404 Not Found")
            return upstream

        with mock.patch.object(cu, "_download", fake_download):
            self.assertEqual(cu.check_one(
                "A", {"sha256": _sha(upstream), "bytes": len(upstream), "url": "u"},
                1, 1)["status"], "ok")
            self.assertEqual(cu.check_one(
                "B", {"sha256": _sha(b"older"), "bytes": 5, "url": "u"},
                1, 1)["status"], "CHANGED")
            self.assertEqual(cu.check_one(
                "C", {"sha256": _sha(b"x"), "bytes": 1, "url": "gone"},
                1, 1)["status"], "GONE")


class RealManifest(unittest.TestCase):
    def test_every_entry_anchored(self):
        man = verify.load_manifest()
        self.assertTrue(man.get("forms"), "manifest has no forms")
        for fid, e in man["forms"].items():
            self.assertTrue(e.get("sha256") and len(e["sha256"]) == 64, fid)
            self.assertTrue(e.get("bytes"), fid)
            self.assertTrue(e.get("url", "").startswith("http"), fid)


if __name__ == "__main__":
    unittest.main()
