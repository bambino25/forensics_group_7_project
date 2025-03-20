import requests
from fake_useragent import UserAgent
from urllib.parse import urlsplit

class Downloader:
    def __init__(self):
        self.content = None
        self.url = None
        self.base_url = None
        ua = UserAgent()
        self.headers = {
            'User-Agent': ua.random
        }
        http_proxy = "socks5h://localhost:9050"
        self.proxy = {"http": http_proxy, "https": http_proxy}

    def download(self, url) -> int|None:
        self.url = url
        self.base_url = "{0.scheme}://{0.netloc}".format(urlsplit(self.url))
        try:
            #print(f"Header: {self.headers}", f"Proxy:{self.proxy}")
            #response = requests.get(self.url, headers=self.headers, proxies=self.proxy)
            response = requests.get(self.url, headers=self.headers)
            print(response)
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
        # Replace the slashes with underscoresx 
        url = url.replace('/', '_')
    
        return url + '.html'
    
    def save(self, filename) -> bool:
        if not self.content:
            print("No content to save")
            return False
        
        with open(filename, 'w') as file:
            file.write(self.content)

        return True