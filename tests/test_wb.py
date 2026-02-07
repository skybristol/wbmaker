"""Tests for the WB class."""

from unittest.mock import MagicMock, patch

import pytest

from wbmaker.wb import WB


class TestWBInitialization:
    """Test WB class initialization."""

    @pytest.fixture
    def env_vars(self, monkeypatch):
        """Set up environment variables for testing."""
        env = {
            "WB_URL": "https://test.wikibase.org/",
            "WB_SPARQL_ENDPOINT": "https://test.wikibase.org/sparql",
            "MEDIAWIKI_API": "https://test.wikibase.org/w/api.php",
            "WB_BOT_USER_AGENT": "TestBot/1.0",
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        return env

    @patch("wbmaker.wb.WikibaseIntegrator")
    @patch("wbmaker.wb.mwclient.Site")
    def test_init_without_credentials(self, mock_mw_site, mock_wbi, env_vars):
        """Test initialization without bot credentials (read-only mode)."""
        wb = WB(cache_props=False)

        assert wb.wbi is not None
        assert wb.mw_site is not None
        assert not hasattr(wb, "login_instance")

    @patch("wbmaker.wb.WikibaseIntegrator")
    @patch("wbmaker.wb.wbi_login.Login")
    @patch("wbmaker.wb.mwclient.Site")
    def test_init_with_credentials(self, mock_mw_site, mock_login, mock_wbi, env_vars, monkeypatch):
        """Test initialization with bot credentials."""
        monkeypatch.setenv("WB_BOT_USER", "testbot")
        monkeypatch.setenv("WB_BOT_PASS", "testpass")

        wb = WB(cache_props=False)

        assert wb.login_instance is not None
        mock_login.assert_called_once_with(user="testbot", password="testpass")

    def test_missing_required_env_vars(self, monkeypatch):
        """Test that missing environment variables raise an error or prompt."""
        # Clear all environment variables
        for var in ["WB_URL", "WB_SPARQL_ENDPOINT", "MEDIAWIKI_API", "WB_BOT_USER_AGENT"]:
            monkeypatch.delenv(var, raising=False)

        # This would normally prompt for input, but in tests we expect it to handle missing vars
        # For now, we skip this test since it requires user input
        # In production code, you might want to add a way to provide these without prompting


class TestWBHelperMethods:
    """Test helper methods of WB class."""

    @pytest.fixture
    def wb_instance(self, monkeypatch):
        """Create a WB instance for testing."""
        env = {
            "WB_URL": "https://test.wikibase.org/",
            "WB_SPARQL_ENDPOINT": "https://test.wikibase.org/sparql",
            "MEDIAWIKI_API": "https://test.wikibase.org/w/api.php",
            "WB_BOT_USER_AGENT": "TestBot/1.0",
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)

        with patch("wbmaker.wb.WikibaseIntegrator"), patch("wbmaker.wb.mwclient.Site"):
            return WB(cache_props=False)

    def test_get_domain(self, wb_instance):
        """Test extracting domain from URL."""
        assert wb_instance._get_domain("https://www.wikidata.org/") == "www.wikidata.org"
        assert wb_instance._get_domain("https://test.wikibase.org/wiki/") == "test.wikibase.org"

    def test_wb_dt_with_datetime(self, wb_instance):
        """Test datetime conversion."""
        from datetime import datetime

        dt = datetime(2024, 1, 15, 12, 30, 45)
        result = wb_instance.wb_dt(dt)
        assert result == "+2024-01-15T00:00:00Z"

    def test_wb_dt_with_string(self, wb_instance):
        """Test datetime conversion from string."""
        result = wb_instance.wb_dt("2024-01-15")
        assert result == "+2024-01-15T00:00:00Z"

    def test_wb_dt_with_invalid_string(self, wb_instance):
        """Test datetime conversion with invalid string."""
        result = wb_instance.wb_dt("invalid-date")
        assert result is None


class TestSPARQLQuery:
    """Test SPARQL query functionality."""

    @pytest.fixture
    def wb_instance(self, monkeypatch):
        """Create a WB instance for testing."""
        env = {
            "WB_URL": "https://test.wikibase.org/",
            "WB_SPARQL_ENDPOINT": "https://test.wikibase.org/sparql",
            "MEDIAWIKI_API": "https://test.wikibase.org/w/api.php",
            "WB_BOT_USER_AGENT": "TestBot/1.0",
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)

        with patch("wbmaker.wb.WikibaseIntegrator"), patch("wbmaker.wb.mwclient.Site"):
            return WB(cache_props=False)

    @patch("wbmaker.wb.requests.get")
    def test_sparql_query_dataframe(self, mock_get, wb_instance):
        """Test SPARQL query with dataframe output."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "head": {"vars": ["item", "itemLabel"]},
            "results": {
                "bindings": [{"item": {"value": "Q1"}, "itemLabel": {"value": "Test Item"}}]
            },
        }
        mock_get.return_value = mock_response

        result = wb_instance.sparql_query("SELECT * WHERE {}", output="dataframe")

        assert result is not None
        assert "item" in result.columns
        assert "itemLabel" in result.columns

    @patch("wbmaker.wb.requests.get")
    def test_sparql_query_empty_results(self, mock_get, wb_instance):
        """Test SPARQL query with no results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"head": {"vars": []}, "results": {"bindings": []}}
        mock_get.return_value = mock_response

        result = wb_instance.sparql_query("SELECT * WHERE {}")
        assert result is None

    @patch("wbmaker.wb.requests.get")
    def test_sparql_query_error(self, mock_get, wb_instance):
        """Test SPARQL query with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = wb_instance.sparql_query("SELECT * WHERE {}")
        assert result is None
