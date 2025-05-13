import os
from pathlib import Path
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.downloader import Downloader
from src.parser import Parser
from src.scheduler import Scheduler

from config import DEFAULT_DIR, THREAD_DIR as target_path

def flatten_distinct(nested_list):
    def flatten(lst):
        for item in lst:
            if isinstance(item, list):
                yield from flatten(item)
            else:
                yield item

    flat_set = set(flatten(nested_list))
    return list(flat_set)

def crawl_url(url, visited_urls, data_dir, seed):
    scheduler = Scheduler(url)
    downloader = Downloader()
    parser = Parser()

    if not scheduler.allow(visited_urls, seed):
        #print(f"Skipping {url}")
        return None

    status_code = downloader.download(url)
    if status_code != 200:
        print(f"Failed to download {url}")
        return None
    
    filename = downloader.filename(url)
    downloader.save(data_dir / filename)

    # Parse the downloaded file
    links = parser.links(downloader.content, downloader.base_url)
    #print(links)

    return links

if __name__ == '__main__':
    '''
        This will be a crawler.
        Using the UrlFrontier --> Scheduler --> Downloader --> Parser

        Using Breadth-First Search Strategy
    '''
    seed = "http://enxx3byspwsdo446jujc52ucy2pf5urdbhqw3kbsfhlfjwmbpj5smdad.onion/"
    queue = [seed] # FiFo
    visited_urls = set()

    data_dir = DEFAULT_DIR
    depth_layer = 0
    max_workers = 5
    max_depth = 2

    while queue and depth_layer < max_depth:
        print(f"🔝 Depth Layer: {depth_layer} | 📋 New Queue Length: {len(queue)}")
        print("Queue:", queue)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(crawl_url, url, visited_urls, data_dir, seed): url for url in queue if url not in visited_urls}
            new_links = []
            downloads = []
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                visited_urls.add(url)
                result = future.result()
                #print(f"Results: {result}")
                if result:
                    new_links.extend(result)
                    downloads.append(url)
        
        queue = [link for link in flatten_distinct(new_links) if link not in visited_urls]  # Update queue with new links
        depth_layer += 1
        time.sleep(1)

    print("\n🚀 Crawling completed!")
    print(f"🌐 Visited URLs: {len(visited_urls)}")
    print(f"📥 Downloaded URLs: {len(downloads)}")
    print(f"📋 Remaining Queue Length: {len(queue)}")
    print(f"🔝 Final Depth Layer Reached: {depth_layer}")