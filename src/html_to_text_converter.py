from bs4 import BeautifulSoup
import re


class HTMLToTextConverter:
    """A class for converting HTML content to plain text."""

    def convert(self, html_content):
        """
        Convert HTML content to plain text, replacing new lines with '\\n'.

        Parameters:
        html_content (str): The HTML content to convert.

        Returns:
        str: The plain text representation of the HTML content.
        """
        if html_content is None:
            html_content = ""

        if not isinstance(html_content, str):
            raise TypeError("html_content must be a string.")

        soup = BeautifulSoup(html_content, 'html.parser')

        # Tags that indicate a new line
        newline_tags = [
            'br', 'p', 'div', 'li', 'ul', 'ol', 'tr',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
        ]

        # Insert newlines before and after the newline tags
        for tag in soup.find_all(newline_tags):
            tag.insert_before('\n')
            if tag.name not in ['br', 'li']:
                tag.insert_after('\n')
            tag.unwrap()

        # Get the text and replace multiple newlines with a single newline
        text = soup.get_text()
        text = re.sub(r'\n+', '\n', text)

        return text.strip()
