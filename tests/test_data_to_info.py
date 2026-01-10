import unittest
from unittest.mock import patch, MagicMock, Mock
from wbmaker.data_to_info import DataToInfo, get_wikidata_item, load_template_as_jinja
from jinja2 import Template


class TestDataToInfo(unittest.TestCase):
    
    @patch('wbmaker.data_to_info.WB')
    def setUp(self, mock_wb_class):
        """Set up test fixtures"""
        self.mock_wb = MagicMock()
        mock_wb_class.return_value = self.mock_wb
        self.data_to_info = DataToInfo(wb=self.mock_wb)
    
    @patch('wbmaker.data_to_info.requests.get')
    def test_get_wikidata_item_success(self, mock_get):
        """Test successful retrieval of Wikidata item"""
        # Arrange
        qid = 'Q42'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'entities': {
                'Q42': {
                    'labels': {'en': {'value': 'Douglas Adams'}}
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Act
        result = self.data_to_info.get_wikidata_item(qid)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIn('entities', result)
        mock_get.assert_called_once_with(f'https://www.wikidata.org/wiki/Special:EntityData/{qid}.json')
    
    @patch('wbmaker.data_to_info.requests.get')
    def test_get_wikidata_item_failure(self, mock_get):
        """Test failed retrieval of Wikidata item"""
        # Arrange
        qid = 'Q999999999'
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Act
        result = self.data_to_info.get_wikidata_item(qid)
        
        # Assert
        self.assertIsNone(result)
    
    def test_sparql_to_template_params_success(self):
        """Test successful SPARQL query to template parameters conversion"""
        # Arrange
        qid = 'Q42'
        sparql_template = 'SELECT ?param ?value WHERE {{ wd:{qid} ?p ?o }}'
        
        mock_sparql_result = {
            'results': {
                'bindings': [
                    {'param': {'value': 'name'}, 'value': {'value': 'Douglas Adams'}},
                    {'param': {'value': 'birth_date'}, 'value': {'value': '1952-03-11'}}
                ]
            }
        }
        self.mock_wb.sparql_query.return_value = mock_sparql_result
        
        # Act
        result = self.data_to_info.sparql_to_template_params(qid, sparql_template)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Douglas Adams')
        self.assertEqual(result['birth_date'], '1952-03-11')
        self.mock_wb.sparql_query.assert_called_once()
    
    def test_sparql_to_template_params_empty_result(self):
        """Test SPARQL query with empty result"""
        # Arrange
        qid = 'Q42'
        sparql_template = 'SELECT ?param ?value WHERE {{ wd:{qid} ?p ?o }}'
        
        self.mock_wb.sparql_query.return_value = None
        
        # Act
        result = self.data_to_info.sparql_to_template_params(qid, sparql_template)
        
        # Assert
        self.assertIsNone(result)
    
    def test_get_wikipedia_template_success(self):
        """Test successful retrieval of Wikipedia template"""
        # Arrange
        template_name = 'Infobox person'
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = '{{Infobox person\n|name={{{name}}}\n}}'
        
        # Create a mock dictionary-like object for pages
        mock_pages = MagicMock()
        mock_pages.__getitem__ = MagicMock(return_value=mock_page)
        self.mock_wb.mw_site.pages = mock_pages
        
        # Act
        result = self.data_to_info.get_wikipedia_template(template_name)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIn('Infobox person', result)
    
    def test_get_wikipedia_template_not_found(self):
        """Test Wikipedia template not found"""
        # Arrange
        template_name = 'Nonexistent template'
        mock_page = MagicMock()
        mock_page.exists = False
        
        # Create a mock dictionary-like object for pages
        mock_pages = MagicMock()
        mock_pages.__getitem__ = MagicMock(return_value=mock_page)
        self.mock_wb.mw_site.pages = mock_pages
        
        # Act
        result = self.data_to_info.get_wikipedia_template(template_name)
        
        # Assert
        self.assertIsNone(result)
    
    def test_load_template_as_jinja(self):
        """Test loading template content as Jinja2 template"""
        # Arrange
        template_content = 'Hello {{name}}'
        
        # Act
        result = self.data_to_info.load_template_as_jinja(template_content)
        
        # Assert
        self.assertIsInstance(result, Template)
        rendered = result.render(name='World')
        self.assertEqual(rendered, 'Hello World')
    
    def test_create_wikitext_template(self):
        """Test creation of wikitext template"""
        # Arrange
        template_name = 'Infobox person'
        params = {
            'name': 'Douglas Adams',
            'birth_date': '1952-03-11',
            'nationality': 'British'
        }
        
        # Act
        result = self.data_to_info.create_wikitext_template(template_name, params)
        
        # Assert
        self.assertIn('{{Infobox person', result)
        self.assertIn('|name=Douglas Adams', result)
        self.assertIn('|birth_date=1952-03-11', result)
        self.assertIn('|nationality=British', result)
    
    def test_fill_template_from_sparql_success(self):
        """Test filling template from SPARQL query"""
        # Arrange
        qid = 'Q42'
        template_name = 'Infobox person'
        sparql_template = 'SELECT ?param ?value WHERE {{ wd:{qid} ?p ?o }}'
        
        mock_sparql_result = {
            'results': {
                'bindings': [
                    {'param': {'value': 'name'}, 'value': {'value': 'Douglas Adams'}}
                ]
            }
        }
        self.mock_wb.sparql_query.return_value = mock_sparql_result
        
        # Act
        result = self.data_to_info.fill_template_from_sparql(qid, template_name, sparql_template)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIn('{{Infobox person', result)
        self.assertIn('|name=Douglas Adams', result)
    
    def test_fill_template_from_sparql_no_params(self):
        """Test filling template when SPARQL returns no parameters"""
        # Arrange
        qid = 'Q42'
        template_name = 'Infobox person'
        sparql_template = 'SELECT ?param ?value WHERE {{ wd:{qid} ?p ?o }}'
        
        self.mock_wb.sparql_query.return_value = None
        
        # Act
        result = self.data_to_info.fill_template_from_sparql(qid, template_name, sparql_template)
        
        # Assert
        self.assertIsNone(result)
    
    @patch('wbmaker.data_to_info.requests.get')
    def test_fill_template_from_item_data_success(self, mock_get):
        """Test filling template from direct item data"""
        # Arrange
        qid = 'Q42'
        template_name = 'Infobox person'
        property_mapping = {
            'name': 'P1559',
            'birth_date': 'P569'
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'entities': {
                'Q42': {
                    'claims': {
                        'P1559': [
                            {
                                'mainsnak': {
                                    'datavalue': {
                                        'value': {'text': 'Douglas Adams'}
                                    }
                                }
                            }
                        ],
                        'P569': [
                            {
                                'mainsnak': {
                                    'datavalue': {
                                        'value': {'time': '+1952-03-11T00:00:00Z'}
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Act
        result = self.data_to_info.fill_template_from_item_data(qid, template_name, property_mapping)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIn('{{Infobox person', result)
        self.assertIn('|name=Douglas Adams', result)
        self.assertIn('|birth_date=+1952-03-11T00:00:00Z', result)
    
    @patch('wbmaker.data_to_info.requests.get')
    def test_fill_template_from_item_data_no_claims(self, mock_get):
        """Test filling template when item has no matching claims"""
        # Arrange
        qid = 'Q42'
        template_name = 'Infobox person'
        property_mapping = {
            'name': 'P1559'
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'entities': {
                'Q42': {
                    'claims': {}
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Act
        result = self.data_to_info.fill_template_from_item_data(qid, template_name, property_mapping)
        
        # Assert
        self.assertIsNone(result)


class TestStandaloneFunctions(unittest.TestCase):
    
    @patch('wbmaker.data_to_info.requests.get')
    def test_standalone_get_wikidata_item(self, mock_get):
        """Test standalone get_wikidata_item function"""
        # Arrange
        qid = 'Q42'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'entities': {'Q42': {}}}
        mock_get.return_value = mock_response
        
        # Act
        result = get_wikidata_item(qid)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIn('entities', result)
    
    def test_standalone_load_template_as_jinja(self):
        """Test standalone load_template_as_jinja function"""
        # Arrange
        template_content = 'Hello {{name}}'
        
        # Act
        result = load_template_as_jinja(template_content)
        
        # Assert
        self.assertIsInstance(result, Template)
        rendered = result.render(name='Test')
        self.assertEqual(rendered, 'Hello Test')


if __name__ == '__main__':
    unittest.main()
