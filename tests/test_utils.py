"""Tests for utility functions."""

from __future__ import annotations

import pytest

from cv_mcp_server.utils import load_prompt


class TestLoadPrompt:
    def test_summary_returns_dict_with_prompt_key(self):
        data = load_prompt("summary")
        assert isinstance(data, dict)
        assert "prompt" in data

    def test_prompt_contains_placeholders(self):
        data = load_prompt("summary")
        prompt = data["prompt"]
        assert "{depth_level}" in prompt
        assert "{context}" in prompt

    def test_nonexistent_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_prompt("nonexistent_prompt_name")
