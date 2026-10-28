"""Unit tests for KittyBot image service behavior."""

import unittest
from unittest.mock import Mock, patch

import requests

import kittybot


class ImageServiceTests(unittest.TestCase):
    @patch("kittybot.requests.get")
    def test_returns_cat_image(self, mock_get: Mock) -> None:
        response = Mock()
        response.json.return_value = [{"url": "https://example.com/cat.jpg"}]
        mock_get.return_value = response

        self.assertEqual(kittybot.get_new_image(), "https://example.com/cat.jpg")
        mock_get.assert_called_once_with(
            kittybot.CAT_API_URL,
            timeout=kittybot.REQUEST_TIMEOUT_SECONDS,
        )

    @patch("kittybot.requests.get")
    def test_uses_dog_fallback(self, mock_get: Mock) -> None:
        cat_failure = requests.ConnectionError("cat service unavailable")
        dog_response = Mock()
        dog_response.json.return_value = [{"url": "https://example.com/dog.jpg"}]
        mock_get.side_effect = [cat_failure, dog_response]

        self.assertEqual(kittybot.get_new_image(), "https://example.com/dog.jpg")
        self.assertEqual(mock_get.call_count, 2)

    @patch("kittybot.requests.get")
    def test_reports_when_both_services_fail(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.ConnectionError("offline")

        with self.assertRaisesRegex(RuntimeError, "No image service"):
            kittybot.get_new_image()

    def test_requires_token(self) -> None:
        with patch.dict("kittybot.os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "TOKEN is not set"):
                kittybot.build_bot()


if __name__ == "__main__":
    unittest.main()

