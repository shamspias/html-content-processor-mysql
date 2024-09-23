import os
from dotenv import load_dotenv
from db_processor import DatabaseProcessor


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get configuration from environment variables
    config = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_NAME': os.getenv('DB_NAME'),
        'START_ID': os.getenv('START_ID', '0'),
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
