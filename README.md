Code can be modified in the files _crawler/config.py_, _scraper/config.py_ and _dashboard/config.py_.
Sample data gets provided. The full data is 10GB.

## Crawler
### Requires
- Access to the dark web

### Run via:
- Option1: Run using Docker from inside the crawler directory:
```bash
docker build -t crawler .
docker run -v $(pwd)/../data:/data crawler
```
- Option2: Run using python from inside the crawler directory:
```bash
pip3 install -r requirements.txt
python3 app.py
```

## Scraper
### Requires
- Installation of ./scraper/requirements.txt
- Crawled data inside the threads folder
- Ollama running with Gemma3 4B Model downloaded

### Run via:
- Using python
```bash
pip3 install -r requirements.txt 
python3 app.py
```

## Dashboard
### Requires
- Installation of ./dashboard/requirements.txt

### Run via:
- Using python
```bash
streamlit run app.py
```