Code can be modified in the files _crawler/config.py_, _scraper/config.py_ and _dashboard/config.py_.
Sample data gets provided. The full data is 10GB.

## Crawler
### Requirements
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
### Requirements
- Installation of ./scraper/requirements.txt
- Crawled data inside the threads folder
- Ollama running with Gemma3 4B Model downloaded

### Run via:
- Using python
```bash
pip3 install -r requirements.txt 
python3 -m spacy download en_core_web_sm
python3 _1scrape.py
python3 _2classify_war_related.py
python3 _3ner.py
```

## Dashboard
### Requirements
- Installation of ./dashboard/requirements.txt

### Run via:
- Using python
```bash
pip3 install -r requirements.txt 
streamlit run app.py
```