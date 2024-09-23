import unittest
from unittest.mock import patch, MagicMock
import mysql.connector
import os

from src.html_to_text_converter import HTMLToTextConverter
from src.db_processor import DatabaseProcessor


class TestHTMLToTextConverter(unittest.TestCase):
    def setUp(self):
        self.converter = HTMLToTextConverter()

    def test_convert_simple_html(self):
        html = "<p>Hello, <strong>World!</strong></p>"
        expected_text = "Hello,\nWorld!"
        result = self.converter.convert(html)
        self.assertEqual(result, expected_text)

    def test_convert_with_newlines(self):
        html = "<div>Line1</div><div>Line2</div>"
        expected_text = "Line1\nLine2"
        result = self.converter.convert(html)
        self.assertEqual(result, expected_text)

    def test_convert_complex_html(self):
        html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <h1>Header</h1>
                <p>Paragraph with <a href="#">link</a>.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
            </body>
        </html>
        """
        expected_text = "Header\nParagraph with \nlink.\nItem 1\nItem 2"
        result = self.converter.convert(html)
        self.assertEqual(result, expected_text)

    def test_convert_empty_string(self):
        html = ""
        expected_text = ""
        result = self.converter.convert(html)
        self.assertEqual(result, expected_text)

    def test_convert_non_string_input(self):
        with self.assertRaises(TypeError):
            self.converter.convert(None)


class TestDatabaseProcessor(unittest.TestCase):
    def setUp(self):
        # Configuration for testing
        self.config = {
            'DB_HOST': 'localhost',
            'DB_USER': 'user',
            'DB_PASSWORD': 'password',
            'DB_NAME': 'test_db',
            'START_ID': '0',
        }
        self.processor = DatabaseProcessor(self.config)

    @patch('src.db_processor.mysql.connector.connect')
    def test_connect_success(self, mock_connect):
        # Mock a successful database connection
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection

        self.processor.connect()
        self.assertTrue(self.processor.connection.is_connected())
        print("test_connect_success passed.")

    @patch('src.db_processor.mysql.connector.connect')
    def test_connect_failure(self, mock_connect):
        # Mock a failed database connection
        mock_connect.side_effect = mysql.connector.Error("Connection failed")
        self.processor.connect()
        self.assertIsNone(self.processor.connection)
        print("test_connect_failure passed.")

    def test_sanitize_filename(self):
        filename = 'invalid/filename:with*illegal|characters<>?'
        expected = 'invalid_filename_with_illegal_characters__'
        result = self.processor.sanitize_filename(filename)
        self.assertEqual(result, expected)
        print("test_sanitize_filename passed.")

    @patch('src.db_processor.mysql.connector.connect')
    @patch('src.db_processor.open', create=True)
    @patch('src.db_processor.HTMLToTextConverter.convert')
    def test_process_records(self, mock_convert, mock_open, mock_connect):
        # Mock database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'pagetitle': 'Test Page', 'content': '<p>Test Content</p>'}
        ]
        mock_connect.return_value = mock_connection
        mock_connection.is_connected.return_value = True

        # Mock file writing
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock HTML conversion
        mock_convert.return_value = 'Test Content'

        self.processor.connect()
        self.processor.process_records()

        mock_convert.assert_called_once_with('<p>Test Content</p>')
        mock_file.write.assert_called_once_with('Test Content')
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
        print("test_process_records passed.")

    @patch('src.db_processor.mysql.connector.connect')
    def test_process_records_no_connection(self, mock_connect):
        # Simulate no database connection
        mock_connect.return_value = None
        self.processor.connect()
        with self.assertLogs(level='INFO') as log:
            self.processor.process_records()
            self.assertIn('No database connection.', log.output)
        print("test_process_records_no_connection passed.")

    @patch('src.db_processor.mysql.connector.connect')
    def test_process_records_no_records(self, mock_connect):
        # Mock database connection and cursor with no records
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value = mock_connection
        mock_connection.is_connected.return_value = True

        self.processor.connect()
        with self.assertLogs(level='INFO') as log:
            self.processor.process_records()
            self.assertIn('No records found.', log.output)
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
        print("test_process_records_no_records passed.")

    def test_generate_unique_filename(self):
        # Assume the output directory is 'output_test'
        self.processor.output_dir = 'output_test'
        os.makedirs(self.processor.output_dir, exist_ok=True)

        # Create a dummy file to simulate existing file
        existing_file = os.path.join(self.processor.output_dir, 'TestPage.txt')
        with open(existing_file, 'w') as f:
            f.write('Dummy content')

        # Generate a unique filename
        unique_filename = self.processor.generate_unique_filename('TestPage.txt')
        self.assertEqual(unique_filename, 'TestPage_1.txt')

        # Clean up
        os.remove(existing_file)
        os.rmdir(self.processor.output_dir)
        print("test_generate_unique_filename passed.")


if __name__ == '__main__':
    unittest.main()
