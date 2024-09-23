import mysql.connector
import re
import os
from .html_to_text_converter import HTMLToTextConverter


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
    def sanitize_filename(name):
        """
        Sanitize the filename by removing illegal characters.

        Parameters:
        name (str): The original filename.

        Returns:
        str: The sanitized filename.
        """
        return re.sub(r'[\\/*?:"<>|]', "_", name)

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
        """Process records from the database and save them to text files."""
        if not self.connection:
            print("No database connection.")
            return

        try:
            cursor = self.connection.cursor(dictionary=True)

            # SQL query to fetch records starting from a specific ID
            query = """
                SELECT id, pagetitle, content 
                FROM pechen_site_content 
                WHERE id >= %s 
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

                # Convert HTML content to plain text
                text_content = self.converter.convert(content)

                # Sanitize filename
                sanitized_title = self.sanitize_filename(pagetitle)
                filename = f"{sanitized_title}.txt"

                # Generate a unique filename to avoid duplication
                unique_filename = self.generate_unique_filename(filename)

                # Full path to the output file
                file_path = os.path.join(self.output_dir, unique_filename)

                # Write the text content to a file
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(text_content)

                print(f"Processed ID: {content_id}, File saved as: {unique_filename}")

            cursor.close()
            print("Finished processing all records.")

        except mysql.connector.Error as e:
            print(f"Error reading data: {e}")

        finally:
            self.close_connection()