import requests
import ua_generator
from urllib.parse import urlsplit
class Downloader:
    def __init__(self):
        self.content = None
        self.url = None
        self.base_url = None
        self.headers = {
            'User-Agent': str(ua_generator.generate())
        }
        # {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def download(self, url) -> int|None:
        self.url = url
        self.base_url = "{0.scheme}://{0.netloc}".format(urlsplit(self.url))
        try:
            response = requests.get(self.url, headers=self.headers)
            self.content = response.text
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        # print(f"Download for {self.url}: {response.status_code}")
        return response.status_code
    
    def filename(self, url) -> str:
        # Remove the protocol
        url = url.replace('http://', '').replace('https://', '')
        # Remove the query string
        #url = url.split('?')[0]
        # Replace the slashes with underscores
        url = url.replace('/', '_')
    
        return url + '.html'
    
    def save(self, filename) -> bool:
        if not self.content:
            print("No content to save")
            return False
        
        with open(filename, 'w') as file:
            file.write(self.content)

        return True