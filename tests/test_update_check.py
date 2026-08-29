"""Tests for the outdated-installment banner (core/update_check.py)."""
from __future__ import annotations

import json

import pytest

from rtmpl.core import update_check as uc


class TestStalenessBanner:
    def test_outdated_shows_banner_with_upgrade_cmd(self):
        b = uc.staleness_banner("0.1.0", "0.2.0")
        assert b is not None
        assert "OUTDATED" in b
        assert "0.1.0" in b and "0.2.0" in b
        assert "uv tool install --upgrade git+https://github.com/yulong-ge/ResearchTemplate" in b

    def test_same_version_no_banner(self):
        assert uc.staleness_banner("0.1.2", "0.1.2") is None

    def test_older_remote_no_banner(self):
        # running newer than remote (e.g. local dev ahead) — silence, no downgrade nag
        assert uc.staleness_banner("0.2.0", "0.1.0") is None

    def test_unknown_latest_no_banner(self):
        assert uc.staleness_banner("0.1.0", None) is None

    def test_banner_mentions_silence_env(self):
        b = uc.staleness_banner("0.1.0", "0.2.0")
        assert "RTMPL_NO_UPDATE_CHECK" in b


class TestLatestKnownVersion:
    def test_env_disable_short_circuits(self, tmp_path, monkeypatch):
        monkeypatch.setenv("RTMPL_NO_UPDATE_CHECK", "1")
        monkeypatch.setattr(uc, "_cache_path", lambda: tmp_path / "c.json")
        assert uc.latest_known_version("0.1.0") is None

    def test_fresh_cache_hit_skips_network(self, tmp_path, monkeypatch):
        cache = tmp_path / "c.json"
        cache.write_text(json.dumps({"checked_at": __import__("time").time(), "version": "9.9.9"}))
        monkeypatch.setenv("RTMPL_NO_UPDATE_CHECK", "")
        monkeypatch.setattr(uc, "_cache_path", lambda: cache)

        def _boom():
            raise AssertionError("network must not be touched on fresh cache")

        monkeypatch.setattr(uc, "_fetch_remote_version", _boom)
        assert uc.latest_known_version("0.1.0") == "9.9.9"

    def test_stale_cache_refetches_and_rewrites(self, tmp_path, monkeypatch):
        import time as t

        cache = tmp_path / "c.json"
        cache.write_text(json.dumps({"checked_at": t.time() - 10 * 3600, "version": "0.0.1"}))
        monkeypatch.setenv("RTMPL_NO_UPDATE_CHECK", "")
        monkeypatch.setattr(uc, "_cache_path", lambda: cache)
        monkeypatch.setattr(uc, "_fetch_remote_version", lambda: "0.3.0")
        assert uc.latest_known_version("0.1.0") == "0.3.0"
        assert json.loads(cache.read_text())["version"] == "0.3.0"

    def test_network_failure_returns_none(self, tmp_path, monkeypatch):
        cache = tmp_path / "c.json"
        monkeypatch.setenv("RTMPL_NO_UPDATE_CHECK", "")
        monkeypatch.setattr(uc, "_cache_path", lambda: cache)

        def _offline():
            raise OSError("offline")

        monkeypatch.setattr(uc, "_fetch_remote_version", _offline)
        assert uc.latest_known_version("0.1.0") is None


class TestVersionParsing:
    @pytest.mark.parametrize(
        "body,expected",
        [
            ('[project]\nname = "rtmpl"\nversion = "0.4.2"\n', "0.4.2"),
            ('version = "1.0"\n', "1.0"),
            ("no version here", None),
        ],
    )
    def test_parse(self, monkeypatch, body, expected):
        class _Resp:
            def read(self_inner):
                return body.encode()

            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, *a):
                return False

        monkeypatch.setattr(uc.urllib.request, "urlopen", lambda req, timeout: _Resp())
        assert uc._fetch_remote_version() == expected


def test_cli_banner_integration(monkeypatch, capsys):
    """main() prints the banner to stderr before running a command."""
    from rtmpl import cli

    monkeypatch.setenv("RTMPL_NO_UPDATE_CHECK", "")
    monkeypatch.setattr(cli, "latest_known_version", lambda v: "99.0.0")
    rc = cli.main(["list"])
    err = capsys.readouterr().err
    assert rc == 0
    assert "OUTDATED" in err and "uv tool install --upgrade" in err
