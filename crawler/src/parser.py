from bs4 import BeautifulSoup
from urllib.parse import urljoin

class Parser:
    def links(self, content, base_url):
        # Parse the content (type HTML) and return a list of full URLs
        soup = BeautifulSoup(content, 'html.parser')
        return [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]