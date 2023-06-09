import re
from dateutil.parser import parse
from datetime import datetime
from unidecode import unidecode
import json



def get_cleanedDate_and_numFields(date:str):
    # Simple Cleaning
    date = unidecode(date)
    date = date.replace("/"," ")
    date = date.replace(","," ")
    date = date.replace("."," ")
    date = date.replace("\""," ")
    date = date.replace("-"," ")
    date = " ".join(date.split())
    
    #Try to Parse
    try:
        parsed_date = parse(date, default=datetime(9999, 1, 1))
        num_fields = len(date.split())
        if parsed_date.year == 9999:
            num_fields += 1

    # If Parsing failed, the date needs heavy cleanup.
    except:
        print("got to here")
        # filter out strings that are not months of the year or ints
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec",]
        date = re.sub(r'[^\w\s]', '', date) # Gets rid of not letters or numbers
        date = re.sub(r'(?<=[a-zA-Z])(?=\d)|(?<=\d)(?=[a-zA-Z])', ' ', date) # Adds spaces when letters and numbers are next to each other
        date = re.sub(r'(' + '|'.join(months) + r')', r' \1 ', date, flags=re.IGNORECASE) #Adds space between words and their substrings if the substrings are months
        date = re.sub(r"\b(?!\d|\b" + "|".join(months) + r"\b)\w+\b", "", date, flags=re.IGNORECASE)
        print(f"date became {date}")

        # Tries again after the cleanup
        try:
            parsed_date = parse(date, default=datetime(9999, 1, 1))
            num_fields = len(date.split())
            if parsed_date.year == 9999:
                num_fields += 1

        # If the date can still not be parsed, there's nothing we can do
        except:
            num_fields = 0
    return parsed_date, num_fields



class Date_Class:
    def __init__(self, likelyDate):
        # The only 3 attributes
        self.likely_year = None
        self.likely_month = None
        self.likely_day = None

        # Cleans the string
        parsed_date, num_fields = get_cleanedDate_and_numFields(likelyDate)
        if num_fields == 0:
            return
        if num_fields == 3:
            self.likely_day = parsed_date.day
        if num_fields >= 2:
            self.likely_month = parsed_date.month
        if num_fields >= 1:
            if parsed_date.year != 9999:
                self.likely_year = parsed_date.year