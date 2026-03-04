import json
import os
import tempfile
import pytest
from config import load_config, save_config, DEFAULT_CONFIG

@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    config_dir = tmp_path / ".hotpaste"
    monkeypatch.setattr("config.CONFIG_DIR", str(config_dir))
    monkeypatch.setattr("config.CONFIG_PATH", str(config_dir / "config.json"))
    return config_dir

def test_default_config_has_5_empty_slots():
    assert DEFAULT_CONFIG == {"slots": {"1": "", "2": "", "3": "", "4": "", "5": ""}}

def test_load_config_creates_default_when_missing(tmp_config):
    result = load_config()
    assert result == DEFAULT_CONFIG
    assert (tmp_config / "config.json").exists()

def test_load_config_reads_existing(tmp_config):
    tmp_config.mkdir(parents=True)
    data = {"slots": {"1": "pw1", "2": "", "3": "", "4": "", "5": ""}}
    (tmp_config / "config.json").write_text(json.dumps(data))
    result = load_config()
    assert result["slots"]["1"] == "pw1"

def test_save_config_writes_json(tmp_config):
    data = {"slots": {"1": "test", "2": "", "3": "", "4": "", "5": ""}}
    save_config(data)
    written = json.loads((tmp_config / "config.json").read_text())
    assert written == data

def test_save_config_creates_dir_if_missing(tmp_config):
    data = {"slots": {"1": "", "2": "", "3": "", "4": "", "5": ""}}
    save_config(data)
    assert (tmp_config / "config.json").exists()
