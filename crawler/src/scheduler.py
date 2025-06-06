from urllib.parse import urlsplit

class Scheduler:
    def __init__(self, url):
        self.url = url
        self.split_url = urlsplit(self.url)
        self.clean_url = f"{self.split_url.scheme}://{self.split_url.netloc}{self.split_url.path}"
    
    def allow(self, visited_urls, seet_url, same_base_url=False):
        if self.already_crawled(visited_urls):
            #print(f"Already crawled {self.clean_url}")
            return False
        if same_base_url:
            if self.wrong_base_url(seet_url):
                #print(f"Wrong base url {self.clean_url}")
                return False
            
        return True
    
    # def already_stored(self, data_dir):
    #     return (data_dir / self.filename).exists()
    
    def already_crawled(self, visited_urls):
        return self.url in visited_urls
    
    def wrong_base_url(self, seet_url):
        base_seet_url = urlsplit(seet_url).netloc
        return self.split_url.netloc != base_seet_url