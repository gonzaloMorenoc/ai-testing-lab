from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

# Skip entire module if playwright or pytest-playwright not installed
pytest.importorskip(
    "playwright",
    reason=(
        "playwright not installed — install with: "
        "pip install playwright pytest-playwright && playwright install chromium"
    ),
)
pytest.importorskip(
    "pytest_playwright",
    reason=(
        "pytest-playwright not installed — install with: "
        "pip install pytest-playwright && playwright install chromium"
    ),
)

from playwright.sync_api import Page, expect  # noqa: E402


class TestChatUI:

    def test_response_appears_in_dom(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.fill("#input", "hello world")
        page.click("#send")
        expect(page.locator("#response")).not_to_have_text("", timeout=5_000)

    def test_streaming_incremental(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.fill("#input", "streaming test message with many words")
        page.click("#send")
        page.wait_for_timeout(150)
        initial = page.locator("#response").text_content() or ""
        page.wait_for_timeout(600)
        final = page.locator("#response").text_content() or ""
        assert len(final) >= len(initial), "response should grow or stay the same over time"

    def test_response_complete_attribute(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.fill("#input", "complete test")
        page.click("#send")
        expect(page.locator("#response")).to_have_attribute(
            "data-complete", "true", timeout=10_000
        )
        text = page.locator("#response").text_content()
        assert text and len(text) > 0

    def test_regex_on_response(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.fill("#input", "hello")
        page.click("#send")
        expect(page.locator("#response")).to_have_attribute(
            "data-complete", "true", timeout=10_000
        )
        text = page.locator("#response").text_content() or ""
        assert re.search(r"Echo:", text, re.IGNORECASE), f"Unexpected response: {text!r}"

    def test_empty_input_shows_error(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.click("#send")
        expect(page.locator("#messages")).to_contain_text("Error", timeout=3_000)

    def test_screenshot_saved(self, page: Page, server_url: str, tmp_path: Path) -> None:
        page.goto(server_url)
        page.fill("#input", "screenshot test")
        page.click("#send")
        expect(page.locator("#response")).to_have_attribute(
            "data-complete", "true", timeout=10_000
        )
        screenshot = tmp_path / "chat_final.png"
        page.screenshot(path=str(screenshot))
        assert screenshot.exists()

    def test_iframe_chat(self, page: Page, server_url: str) -> None:
        page.set_content(
            f"<html><body>"
            f'<iframe id="chat-frame" src="{server_url}" width="800" height="600"></iframe>'
            f"</body></html>"
        )
        frame = page.frame_locator("#chat-frame")
        frame.locator("#input").fill("iframe test")
        frame.locator("#send").click()
        expect(frame.locator("#response")).to_have_attribute(
            "data-complete", "true", timeout=10_000
        )

    @pytest.mark.slow
    def test_real_streamlit_chat(self, page: Page) -> None:
        url = os.getenv("STREAMLIT_CHAT_URL", "")
        if not url:
            pytest.skip("STREAMLIT_CHAT_URL not set")
        page.goto(url, timeout=15_000)
        page.wait_for_load_state("networkidle", timeout=15_000)
        assert page.title() != ""
