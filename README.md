# MySQL HTML Content Processor

This project connects to a MySQL database, retrieves HTML content from the `pechen_site_content` table, converts it to
plain text, and saves each entry as a text file named after the `pagetitle`. It is designed to handle large datasets and
allows you to resume processing from a specific ID in case of interruptions.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Features](#features)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
- [Usage](#usage)
    - [Running the Application](#running-the-application)
    - [Resuming Processing](#resuming-processing)
- [Testing](#testing)
- [Project Details](#project-details)
    - [HTML to Text Conversion](#html-to-text-conversion)
    - [Database Processing](#database-processing)
- [Best Practices](#best-practices)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Project Structure

```
project/
├── .env
├── example.env
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── db_processor.py
│   └── html_to_text_converter.py
└── tests/
    └── test_processor.py
```

- **`.env`**: Environment variables (database credentials). **Do not commit this file.**
- **`example.env`**: Template for `.env` without sensitive information.
- **`requirements.txt`**: Lists all Python dependencies.
- **`README.md`**: Documentation and instructions.
- **`src/`**: Source code.
    - **`__init__.py`**: Initializes the `src` package.
    - **`main.py`**: Entry point of the application.
    - **`db_processor.py`**: Contains `DatabaseProcessor` class.
    - **`html_to_text_converter.py`**: Contains `HTMLToTextConverter` class.
- **`tests/`**: Unit tests.
    - **`test_processor.py`**: Tests for the classes.

---

## Features

- **HTML to Text Conversion**: Converts HTML content to plain text, preserving structure using newlines.
- **Database Interaction**: Connects to a MySQL database and retrieves content.
- **File Output**: Saves each content entry to a text file named after the `pagetitle`.
- **Resume Capability**: Can resume processing from a specific ID.
- **Modular Design**: Clean separation of concerns with classes and modules.
- **Unit Testing**: Comprehensive tests for reliability.

---

## Getting Started

### Prerequisites

- Python 3.6 or higher
- MySQL database access
- Pip package manager
- Virtual environment (optional but recommended)

### Installation

1. **Clone the Repository**
   get the link from git, use https or ssh
   ```bash
   git clone https://github.com/shamspias/html-content-processor-mysql.git
   cd project
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Copy `example.env` to `.env`**

   ```bash
   cp example.env .env
   ```

2. **Edit `.env` and Add Your Database Credentials**

   Open `.env` in a text editor and configure:

   ```dotenv
   # Database Configuration
   DB_HOST=your_db_host
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=your_db_name

   # Starting ID (optional)
   START_ID=0
   ```

    - **`DB_HOST`**: Your database host (e.g., `localhost`).
    - **`DB_USER`**: Your database username.
    - **`DB_PASSWORD`**: Your database password.
    - **`DB_NAME`**: Name of your database.
    - **`START_ID`**: (Optional) ID to start processing from.

---

## Usage

### Running the Application

Navigate to the project directory and run:

```bash
python -m src.main
```

This command tells Python to execute the `main.py` script located in the `src` package.

### Resuming Processing

If the script stops and you need to resume:

1. **Note the Last Processed ID**

   The script outputs the ID of each processed record.

2. **Update `START_ID` in `.env`**

   ```dotenv
   START_ID=last_processed_id
   ```

3. **Rerun the Application**

   ```bash
   python -m src.main
   ```

---

## Testing

To run the unit tests, execute:

```bash
python -m unittest discover tests
```

This command discovers and runs all tests in the `tests` directory.

---

## Project Details

### HTML to Text Conversion

The `HTMLToTextConverter` class in `html_to_text_converter.py`:

- **Purpose**: Converts HTML content to plain text.
- **Features**:
    - Parses HTML using BeautifulSoup.
    - Inserts newlines at appropriate tags (`<p>`, `<div>`, headers, etc.).
    - Removes HTML tags while preserving text content.

### Database Processing

The `DatabaseProcessor` class in `db_processor.py`:

- **Purpose**: Handles database connections and processes records.
- **Features**:
    - Connects to MySQL using credentials from `.env`.
    - Retrieves records from `pechen_site_content` starting from `START_ID`.
    - Converts HTML content to text using `HTMLToTextConverter`.
    - Saves content to text files named after sanitized `pagetitle`.
    - Handles exceptions and ensures the database connection is closed properly.

---

## Best Practices

- **Environment Variables**: Use `.env` to store sensitive information.
- **Modular Code**: Organized into reusable modules and classes.
- **Testing**: Includes unit tests to ensure code reliability.
- **Logging**: Print statements provide progress updates; consider using the `logging` module for production.
- **Error Handling**: Comprehensive exception handling for robustness.
- **Version Control**: Use `.gitignore` to exclude sensitive files and directories.

---

## Dependencies

- **mysql-connector-python**: For connecting to the MySQL database.
- **beautifulsoup4**: For parsing and converting HTML content.
- **python-dotenv**: For loading environment variables from `.env` file.

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes and commit:

   ```bash
   git commit -am 'Add new feature'
   ```

4. Push to the branch:

   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a Pull Request.

---

## Acknowledgments

- **BeautifulSoup**: For making HTML parsing easy.
- **MySQL Connector/Python**: For facilitating database interactions.
- **Python Community**: For continuous support and resources.

---

## Contact

For any questions or issues, please open an issue on the repository or contact the maintainer.
