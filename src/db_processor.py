import re
import os
import html
import json  # Import the json module
import mysql.connector

# Import NLTK and necessary modules
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from langdetect import detect, LangDetectException

from .html_to_text_converter import HTMLToTextConverter

# Download NLTK resources if not already present
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)


class DatabaseProcessor:
    """A class to handle database operations and file writing."""

    def __init__(self, config):
        """
        Initialize the DatabaseProcessor.

        Parameters:
        config (dict): Configuration dictionary containing database credentials, start_id, and output directory.
        """
        self.host = config.get('DB_HOST')
        self.port = int(config.get('DB_PORT', 3306))  # Default to 3306 if not specified
        self.user = config.get('DB_USER')
        self.password = config.get('DB_PASSWORD')
        self.database = config.get('DB_NAME')
        self.start_id = int(config.get('START_ID', 0))
        self.output_dir = config.get('OUTPUT_DIR', 'output')
        self.user_id = config.get('USER_ID', 'default_user')
        self.connection = None
        self.converter = HTMLToTextConverter()

        # Ensure the output directory exists
        self.create_output_directory()

    def create_output_directory(self):
        """Create the output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
        else:
            print(f"Using existing output directory: {self.output_dir}")

    def connect(self):
        """Connect to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to the database")
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None

    def close_connection(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    @staticmethod
    def sanitize_filename(name, content_id, max_length=80):
        """
        Sanitize the filename by removing illegal characters and limiting its length.

        Parameters:
        name (str): The original filename.
        max_length (int): Maximum allowed length for the filename.

        Returns:
        str: The sanitized and truncated filename.
        """
        # Decode HTML entities
        name = html.unescape(name)

        # Remove illegal characters
        name = re.sub(r'[\\/*?:"<>|]', "_", name)

        # Replace spaces with underscores and remove extra spaces
        name = re.sub(r'\s+', '_', name).strip('_')

        # Truncate the filename to the maximum allowed length
        if len(name) > max_length:
            name = name[:max_length]

        return str(content_id) + ". " + name

    def generate_unique_filename(self, filename):
        """
        Generate a unique filename if the file already exists in the output directory.

        Parameters:
        filename (str): The original filename.

        Returns:
        str: A unique filename.
        """
        base_name, extension = os.path.splitext(filename)
        counter = 1
        unique_filename = filename
        while os.path.exists(os.path.join(self.output_dir, unique_filename)):
            unique_filename = f"{base_name}_{counter}{extension}"
            counter += 1
        return unique_filename

    def process_records(self):
        """Process records from the database and save them to JSON files."""
        if not self.connection:
            print("No database connection.")
            return

        try:
            cursor = self.connection.cursor(dictionary=True)

            # SQL query to fetch records starting from a specific ID
            query = """
                SELECT id, pagetitle, content, uri
                FROM pechen_site_content 
                WHERE id >= %s AND published = 1 
                ORDER BY id ASC
            """
            cursor.execute(query, (self.start_id,))

            rows = cursor.fetchall()
            if not rows:
                print("No records found.")
                return

            for row in rows:
                content_id = row['id']
                pagetitle = row['pagetitle']
                content = row['content']
                uri = row['uri']
                print(f"Processing URI: {uri}")

                # Convert HTML content to plain text
                text_content = self.converter.convert(content)

                # Check if text_content is empty after stripping whitespace
                if not text_content.strip():
                    print(f"Text content is empty after conversion for ID: {content_id}. Skipping this record.")
                    continue

                # Detect language
                try:
                    detected_lang = detect(text_content)
                    print(f"Detected language: {detected_lang}")
                except LangDetectException:
                    print(f"Could not detect language for ID: {content_id}. Skipping this record.")
                    continue

                # Check if NLTK has stopwords for the detected language
                if detected_lang not in stopwords.fileids():
                    print(
                        f"No stopwords available for language '{detected_lang}' for ID: {content_id}. Skipping this record.")

                # Create the JSON data
                data = {
                    "page_content": text_content,
                    "metadata": {
                        "uri": uri,
                        "user_id": self.user_id
                    }
                }

                # Sanitize filename
                sanitized_title = self.sanitize_filename(pagetitle, content_id)
                filename = f"{sanitized_title}.json"

                # Generate a unique filename to avoid duplication
                unique_filename = self.generate_unique_filename(filename)

                # Full path to the output file
                file_path = os.path.join(self.output_dir, unique_filename)

                # Write the JSON data to a file
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)

                print(f"Processed ID: {content_id}, File saved as: {unique_filename}")

            cursor.close()
            print("Finished processing all records.")

        except mysql.connector.Error as e:
            print(f"Error reading data: {e}")

        finally:
            self.close_connection()
