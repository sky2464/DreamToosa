"""Tests for canonical DreamsClient (DEV-005)."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# CI does not install anthropic; stub before importing dreams_implementation.
if "anthropic" not in sys.modules:
    _mock_anthropic_mod = MagicMock()
    sys.modules["anthropic"] = _mock_anthropic_mod

from dreams_implementation import DreamConfig, DreamsClient


class TestDreamsImplementation(unittest.TestCase):
    def test_dreams_client_module_removed(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertFalse(os.path.isfile(os.path.join(repo_root, "dreams_client.py")))

    @patch("dreams_implementation.anthropic.Anthropic")
    def test_create_dream_calls_beta_api(self, mock_anthropic):
        mock_dream = MagicMock()
        mock_dream.id = "drm_test"
        mock_dream.status = "pending"
        mock_client = MagicMock()
        mock_client.beta.dreams.create.return_value = mock_dream
        mock_anthropic.return_value = mock_client

        client = DreamsClient(api_key="test-key")
        dream_id = client.create_dream(
            DreamConfig(
                memory_store_id="memstore_01Example",
                session_ids=["sesn_01Example"],
                instructions="curate",
            )
        )

        self.assertEqual(dream_id, "drm_test")
        mock_client.beta.dreams.create.assert_called_once()

    def test_canonical_import(self):
        from dreams_implementation import DreamConfig as DC, DreamsClient as DCl

        self.assertIs(DC, DreamConfig)
        self.assertIs(DCl, DreamsClient)

    @patch("dreams_implementation.anthropic.Anthropic")
    def test_integration_manager_uses_canonical_client(self, mock_anthropic):
        from dreamtoosa_dreams_integration import DreamToosaDreamsManager, DreamDomain

        mock_dream = MagicMock()
        mock_dream.id = "drm_domain"
        mock_dream.status = "pending"
        mock_client = MagicMock()
        mock_client.beta.dreams.create.return_value = mock_dream
        mock_anthropic.return_value = mock_client

        manager = DreamToosaDreamsManager()
        manager.initialize_domain(DreamDomain.CODE_GENERATION)
        dream_id = manager.create_domain_dream(
            DreamDomain.CODE_GENERATION,
            memory_store_id="memstore_01Example",
            session_ids=["sesn_01Example"],
        )
        self.assertEqual(dream_id, "drm_domain")


if __name__ == "__main__":
    unittest.main()
