import re
import datetime as dt
from bs4 import BeautifulSoup

class Detective:
    '''
    The detective is the main class that is responsible for the scraping.
    It is responsible for:
    - Splitting the files with a thread into each message (magnify)
    - concluding the information into a dictionary (conclude)
    - return a list of dictionaries (report)
    '''
    def __init__(self):
        self.regex = {
            'datetime_sub': re.compile(r'[^0-9\s:]', re.IGNORECASE),
            'magnify_pattern': re.compile(r'<!-- start post.html -->(.*?)<!-- end post.html -->', re.DOTALL),
        }
        pass

    def magnify(self, filepath):
        ''' Splits the file into chunks to have one chunk per report instance'''
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        extracted_posts = []
        for match in self.regex['magnify_pattern'].finditer(content):
            extracted_html = match.group(1)
            extracted_posts.append(BeautifulSoup(extracted_html, 'html.parser'))
        
        return extracted_posts

    def conclude(self, raw_post):
        ''' Concludes the information from the file (splitted by the magnifier) into a dictionary'''
        conclusion = dict()

        # Conclude the information from the raw_post
        conclusion['originFile'] = ""
        conclusion['messageId'] = raw_post.find('input', {'type': 'checkbox'})['name'].split('-')[2] # <input type="checkbox" class="deletionCheckBox" name="qanonresearch-19890-20696"> --> 20696 
        conclusion['threadId'] = raw_post.find('input', {'type': 'checkbox'})['name'].split('-')[0] # <input type="checkbox" class="deletionCheckBox" name="qanonresearch-19890-20696"> --> qanonresearch 
        conclusion['datetime'] = self.format_datetime(raw_post.find('span', {'class': 'labelCreated'}).text.strip())  # <span class="labelCreated">10/20/2019 (Sun) 19:00:26</span> --> self.format_datetime(10/20/2019 (Sun) 19:00:26) --> 2019-10-20 19:00:26
        conclusion['messageContent'] = raw_post.find('div', {'class': 'divMessage'}).text.strip().replace("\n", "")  # <div class="divMessage">Messageee</div> --> Messageee

        return conclusion

    def format_datetime(self, datetime):
        ''' Formats the datetime (e.g. 10/20/2019 (Sun) 19:00:26) into datetime format and then into the format (e.g. 2019-10-20 19:00:26)'''
        try:
            # Remove all non-numeric characters (except spaces) & parathesis
            datetime = re.sub(self.regex['datetime_sub'] , '', datetime) # Results in 10202019 19:00:26
            datetime = dt.datetime.strptime(datetime, "%m%d%Y %H:%M:%S")
            # Convert the datetime to the format "%Y-%m-%d %H:%M:%S"
            datetime = datetime.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            datetime = ""
        finally:
            return datetime

    def summarize(self, messageContent):
        return "Summary of the messageContent" # Placeholder for the summary function

    def report(self, filepath):
        ''' Returns a list of dictionaries with the information from the file'''
        report = []
        #print("Filepath: ", filepath)
        #print("Len Posts: ", len(self.magnify(filepath)))

        magnified_posts = self.magnify(filepath)
        if len(magnified_posts) > 0:
            for raw_post in magnified_posts:
                report.append(self.conclude(raw_post))
        
            success, violated_guidelines = self.fits_report_guideline(report)
            if success: return report
        else:
            print("No posts found in the file.", filepath)
            return False

        raise Exception(f"Report does not fit the guideline: {violated_guidelines}")

    def fits_report_guideline(self, report):
        ''' Checks if the report fits the format of the conclusion format'''
        return (True, None)
