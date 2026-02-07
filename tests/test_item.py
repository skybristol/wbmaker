"""Tests for the Item class."""

from unittest.mock import MagicMock

import pytest

from wbmaker.item import Item
from wbmaker.wb import WB


class TestItemInitialization:
    """Test Item class initialization."""

    @pytest.fixture
    def mock_wb(self):
        """Create a mock WB instance."""
        wb = MagicMock(spec=WB)
        wb.props = {"instance of": {"property": "P31", "dataType": "WikibaseItem"}}
        wb.wbi = MagicMock()
        wb.wbi.item.new.return_value = MagicMock()
        wb.wbi.item.get.return_value = MagicMock()
        wb.wbi_enums = MagicMock()
        wb.datatypes = MagicMock()
        wb.mw_site = MagicMock()
        return wb

    def test_new_item_creation(self, mock_wb):
        """Test creating a new item without QID."""
        data = {"label": "Test Item", "description": "A test item", "aliases": ["Test"]}

        item = Item(data, wb=mock_wb, commit=False)

        assert item.data == data
        assert item.wb == mock_wb
        mock_wb.wbi.item.new.assert_called_once()

    def test_existing_item_update(self, mock_wb):
        """Test updating an existing item with QID."""
        data = {"qid": "Q123", "label": "Updated Item"}

        Item(data, wb=mock_wb, commit=False)

        mock_wb.wbi.item.get.assert_called_once_with("Q123")

    def test_item_with_aliases_list(self, mock_wb):
        """Test item with multiple aliases as list."""
        data = {"label": "Test", "aliases": ["Alias1", "Alias2", "Alias3"]}

        item = Item(data, wb=mock_wb, commit=False)

        assert item.item.aliases.set.called

    def test_item_with_aliases_string(self, mock_wb):
        """Test item with single alias as string."""
        data = {"label": "Test", "aliases": "SingleAlias"}

        item = Item(data, wb=mock_wb, commit=False)

        assert item.item.aliases.set.called


class TestItemMethods:
    """Test Item class methods."""

    @pytest.fixture
    def mock_wb(self):
        """Create a mock WB instance."""
        wb = MagicMock(spec=WB)
        wb.props = {
            "instance of": {"property": "P31", "dataType": "WikibaseItem"},
            "reference URL": {"property": "P854", "dataType": "Url"},
        }
        wb.wbi = MagicMock()
        wb.wbi.item.new.return_value = MagicMock()
        wb.wbi.property.get.return_value = MagicMock(datatype="WikibaseItem")
        wb.wbi_enums = MagicMock()
        wb.datatypes = MagicMock()
        wb.datatypes.Item = MagicMock
        wb.datatypes.String = MagicMock
        wb.datatypes.Time = MagicMock
        wb.wb_dt = MagicMock(return_value="+2024-01-01T00:00:00Z")
        return wb

    def test_property_type(self, mock_wb):
        """Test getting property type."""
        item = Item({"label": "Test"}, wb=mock_wb, commit=False)

        # This should work if the property is cached
        prop_type = item._property_type(prop_name="instance of")
        assert prop_type == "WikibaseItem"

    def test_item_data_template(self, mock_wb):
        """Test getting item data template."""
        item = Item({"label": "Test"}, wb=mock_wb, commit=False)

        template = item.item_data_template()

        assert "qid" in template
        assert "label" in template
        assert "description" in template
        assert "aliases" in template
        assert "claims" in template

    def test_get_value_string(self, mock_wb):
        """Test extracting string value from statement."""
        item = Item({"label": "Test"}, wb=mock_wb, commit=False)

        mock_statement = MagicMock()
        mock_statement.mainsnak.datavalue = {"value": "test_value"}

        value = item.get_value(mock_statement)
        assert value == "test_value"

    def test_get_value_dict_with_id(self, mock_wb):
        """Test extracting ID from dict value."""
        item = Item({"label": "Test"}, wb=mock_wb, commit=False)

        mock_statement = MagicMock()
        mock_statement.mainsnak.datavalue = {"value": {"id": "Q123"}}

        value = item.get_value(mock_statement)
        assert value == "Q123"


class TestBuildStatement:
    """Test statement building."""

    @pytest.fixture
    def mock_wb(self):
        """Create a mock WB instance."""
        wb = MagicMock(spec=WB)
        wb.props = {"instance of": {"property": "P31", "dataType": "WikibaseItem"}}
        wb.wbi = MagicMock()
        wb.wbi.item.new.return_value = MagicMock()
        wb.wbi.property.get.return_value = MagicMock(datatype="WikibaseItem")
        wb.wbi_enums = MagicMock()
        wb.wbi_enums.WikibaseSnakType.KNOWN_VALUE = "KNOWN_VALUE"
        wb.wbi_enums.WikibaseSnakType.UNKNOWN_VALUE = "UNKNOWN_VALUE"
        wb.wbi_enums.WikibaseSnakType.NO_VALUE = "NO_VALUE"

        # Mock datatypes
        wb.datatypes = MagicMock()
        wb.datatypes.Item = MagicMock(return_value=MagicMock())
        wb.datatypes.String = MagicMock(return_value=MagicMock())
        wb.datatypes.URL = MagicMock(return_value=MagicMock())

        return wb

    def test_build_statement_item(self, mock_wb):
        """Test building an item statement."""
        item = Item({"label": "Test"}, wb=mock_wb, commit=False)

        statement = item.build_statement(pid="P31", p_datatype="ITEM", value="Q5")

        assert statement is not None
        mock_wb.datatypes.Item.assert_called_once()

    def test_build_statement_special_unknown(self, mock_wb):
        """Test building statement with unknown value."""
        item = Item({"label": "Test"}, wb=mock_wb, commit=False)

        statement = item.build_statement(
            pid="P31", p_datatype="ITEM", value="SPECIAL:UNKNOWN_VALUE"
        )

        assert statement is not None

    def test_build_statement_special_no_value(self, mock_wb):
        """Test building statement with no value."""
        item = Item({"label": "Test"}, wb=mock_wb, commit=False)

        statement = item.build_statement(pid="P31", p_datatype="ITEM", value="SPECIAL:NO_VALUE")

        assert statement is not None
