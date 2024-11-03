import os
from dotenv import load_dotenv
from src.db_processor import DatabaseProcessor


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get configuration from environment variables
    config = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT', '3306'),  # Default to '3306' if not specified
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_NAME': os.getenv('DB_NAME'),
        'START_ID': os.getenv('START_ID', '0'),
        'OUTPUT_DIR': os.getenv('OUTPUT_DIR', 'output'),
        'USER_ID': os.getenv('USER_ID', 'default_user'),
    }

    # Check for missing configuration
    missing = [key for key, value in config.items() if not value]
    if missing:
        print(f"Missing configuration for: {', '.join(missing)}")
        return

    processor = DatabaseProcessor(config)
    processor.connect()
    processor.process_records()


if __name__ == "__main__":
    main()
