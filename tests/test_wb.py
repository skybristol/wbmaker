import unittest
from unittest.mock import patch, MagicMock
from wb.wb import WB
import configparser
import os

class TestWB(unittest.TestCase):
    @patch('wb.configparser.ConfigParser')
    @patch('os.path.exists')
    def test_init(self, mock_exists, mock_config):
        # Arrange
        mock_exists.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.__getitem__.return_value = {
            'sparql_endpoint': 'test_endpoint',
            'bot_user_agent': 'test_agent',
            'mediawiki_api_url': 'test_api_url',
            'wikibase_url': 'test_url',
            'bot_user': 'test_user',
            'bot_pass': 'test_pass'
        }

        # Act
        wb = WB()

        # Assert
        mock_exists.assert_called_once_with('config.ini')
        mock_config.assert_called_once()
        mock_config_instance.read.assert_called_once_with('config.ini')
        self.assertEqual(wb.wbi_config['SPARQL_ENDPOINT_URL'], 'test_endpoint')
        self.assertEqual(wb.wbi_config['USER_AGENT'], 'test_agent')
        self.assertEqual(wb.wbi_config['MEDIAWIKI_API_URL'], 'test_api_url')
        self.assertEqual(wb.wbi_config['WIKIBASE_URL'], 'test_url')

if __name__ == '__main__':
    unittest.main()