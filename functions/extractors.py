from dateutil import parser
from datetime import datetime, timedelta
import re 
import requests

import functions.initialiser as init

nlp = init.init_nlp()

def extract_reminder_details(msg):
    """Extracts reminder details depending on the user input for date, time, and event details"""
    date, time = extract_str_date_time(msg)
    event = extract_event_details(msg)
    print(date, time)
    # Combination of the two previous functions 
    reminder_details = {
        "date": date,
        "time": time,
        "event": event
    }
    return reminder_details

def extract_event_details(msg):
    """Extracts the event details from the user input"""
    doc = nlp(msg)
    
    for token in doc:
        if token.pos_ == "NOUN":
            # Extract the event if the token is a noun e.g Can you remind me to go to the gym-gym is the noun
            return token.text
    return None

def extract_str_date_time(msg):
    """Extracts the date and time as a STRING from the user input"""
    try:
        # Parse the date and time from the message using dateutil.parser
        dt = parser.parse(msg, fuzzy=True)
        str_date = dt.strftime("%d %B")  # Format the date as "day month"
        str_time = dt.strftime("%H:%M")  # Format the time as "hour:minute"
        return str_date, str_time
    except ValueError:
        # Handle the case when date and time cannot be parsed
        return None, None

def extract_datetime_objects(msg):
    """Extracts the DATETIME objects from the user input"""
    try:
        # Parse the date and time from the message using dateutil.parser
        dt = parser.parse(msg, fuzzy=True)
        date_date = dt.date() #return actual date object
        time_time = dt.time() #return actual time object
        return date_date, time_time
    except ValueError:
        # Handle the case when date and time cannot be parsed
        return None, None
    
# Function to create a checklist using the users inputs into seperate tasks 
def extract_checklist_items(user_input):
    """Extracts the checklist items from the user input, ignoring specific phrases"""
    x = re.split('1|2|3|4|5|6|7|8|9|one|two|three|four|five|six|seven|eight|nine|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth', user_input)
    print(x)
    return x[1:]

# Extracting the meeting details from the user input starts here I split it into different fucntions for each bit so it doesnt get confused:
def extract_title(msg):
    """extract the title from the user input"""
    words = msg.split()
    title = ""
    about_flag = False
    for i, word in enumerate(words):
        if about_flag:
            title += word + " "
        if word.lower() == "about":
            about_flag = True
    return title.strip()

def extract_attendees(msg):
    """Extracts the attendees from the user input"""
    words = msg.split(" with ")
    attendees = []
    if len(words) > 1:
        attendees_str = words[1].split(" about ")[0]  # Extract only the attendee names before "about"
        attendees = [attendee.strip() for attendee in attendees_str.split(" and ")]
        # Separate first and last names of attendees
        attendees = [attendee.split(" ") for attendee in attendees]
        attendees = [" ".join(name.title() for name in attendee) for attendee in attendees]
    return attendees

def add_30_mins(start_time):
    """add 30 minutes to the start time of the user input"""
    start_time_datetime = datetime.strptime(start_time, "%H:%M")
    time_to_add = timedelta(minutes=30)
    added_time = start_time_datetime + time_to_add
    end_time = added_time.time()
    formatted_end_time = end_time.strftime("%H:%M")
    return formatted_end_time

def extract_meeting_details(msg):
    """function that extracts the details of users meeting"""
    title = extract_title(msg)
    date, start_time = extract_str_date_time(msg)
    end_time = add_30_mins(start_time)
    attendees = extract_attendees(msg)
    return title, date, start_time, end_time, attendees

# Function to extract the topic from user input
def extract_topic(user_input):
    """extract the topic the user requests information about"""
    last_word = user_input.split(" ")[-1]
    if "-" in last_word:
        topic = last_word.replace("-", " ")
        return topic
    else:
        return last_word

# Function to get information about a topic using Wikipedia API
def extract_wikipedia_summary(topic):
    """use the wikipedia API to return information about the users given topic"""
    base_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
    url = f"{base_url}{topic}"

    try:
        response = requests.get(url)
        data = response.json()

        if "extract" in data:
            # Extract only the first sentence from the summary
            first_sentence = data["extract"].split(".")[0]
            return first_sentence
        else:
            return f"Sorry, I couldn't find information about {topic}. Please try another topic."

    except requests.RequestException as e:
        return f"Error occurred while fetching data: {e}"
    
def extract_city_name(user_input):
    """extract the city name from user input and remove question marks"""
    city_name = user_input.split(" in ")[-1]
    city_name = city_name.replace("?", "")
    return city_name

