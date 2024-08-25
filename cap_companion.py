import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
import speech_recognition as sr
import pyttsx3
import threading
import json
import torch
from train_model.nltk_utils import bag_of_words, tokenize
from fuzzywuzzy import fuzz
import time as thyme
import datetime as dt
from datetime import datetime, timedelta, time
import random
import subprocess
import requests
import os
from playsound import playsound

from train_model.model import NeuralNet
import functions.initialiser as init
import functions.meeting_scheduler as meeting_scheduler
import functions.email as emailer
import functions.extractors as extractor
from functions.themes import themes

############## CHANGES ###############
# moved model.py, nltk_utils.py, train.py, and intents.json to /train_model
# deleted bin folder
# moved salmachatbot contents to main directory
######################################

engine = pyttsx3.init()

#load intents file into memory
with open('train_model/intents.json', 'r') as intents_json:
    intents = json.load(intents_json)

def print_user_input(text):
    """print what the user said, to the GUI"""
    #you can call this function and provide it what you want printed to the screen like so print_user_input("Hi guys")
    chat_display.configure(state='normal')
    chat_display.insert(tk.END, "You: ", "user_tag")
    chat_display.insert(tk.END, f"{text.capitalize()}\n", "user_text")
    chat_display.configure(state='disabled') 

def print_cap_companion_output(response):
    """print what the cap companion has deemed the best response, to the GUI"""
    engine = pyttsx3.init()
    chat_display.configure(state='normal')
    chat_display.insert(tk.END, f"Cap Companion: ", "chatbot_tag")
    chat_display.insert(tk.END, f"{response}\n", "chatbot_text")
    chat_display.configure(state='disabled')
    engine.say(response)
    engine.runAndWait() 

def speech_to_text():
    """convert user speech audio into text and send to processing"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=0.5)
        speech = recognizer.listen(mic)
    try:
        text = recognizer.recognize_google(speech)
        #calls the process text function with the processed text
        process_text(text.lower())
    
    except sr.UnknownValueError as e:
        print_cap_companion_output(f"Speech could not be interpreted: {e}. Please try again.\n")

    except sr.RequestError as e:
        print_cap_companion_output(f"Error occurred while requesting speech recognition service: {e}\n")

#function for directing user input to best function
def process_text(user_input):
    """Take in raw user input, print it, compute the best response, then send it to processing or printing"""
    print_user_input(user_input.capitalize())

    #generate a response from the get_response() function
    response = get_response(user_input)
    #if/elif blocks that check if the response is meant to trigger a function
    if response == "TRIGGER WEATHER PROCESSOR":
        process_weather_input(user_input)
    elif response == "TRIGGER MEETING PROCESSOR":
        process_input_schedule_meeting(user_input)
    elif response == "TRIGGER CHECKLIST PROCESSOR":
        process_input_checklist(user_input)
    elif response == "TRIGGER WIKI PROCESSOR":
        process_wikipedia_input(user_input)
    elif response == "TRIGGER REMINDER PROCESSOR":
        process_input_reminder(user_input)
    else:
        #no function triggered, print best model response
        print_cap_companion_output(response)

def send_reminder_email(subject, body):
    """send the users reminder email"""
    user_email = stored_email.get()
    emailer.set_email_content(subject, body, user_email)
    print_cap_companion_output(f"Sending reminder email.")

def compare_date(desired_date, desired_time, reminder_details):
    """compare the users desired date against the current date in a thread, then start the time thread"""
    done = False
    while not done:
        current_date = datetime.now().date()
        if desired_date <= current_date:
            compare_time_thread = threading.Thread(target=compare_time, args=(desired_time, reminder_details))
            compare_time_thread.start()
            done = True
        else:
            next_day = current_date + timedelta(days=1)
            next_day = datetime.combine(next_day, datetime.min.time())
            time_remaining = next_day - datetime.now()
            seconds_remaining = time_remaining.total_seconds()
            print(seconds_remaining)
            thyme.sleep(seconds_remaining)

def compare_time(desired_time, reminder_details):
    """compare the users desired time vs the current time, send email once desired time is reached"""
    done = False
    while not done:
        current_time = datetime.now().time()
        if desired_time <= current_time:
            email_subject = f"Your Reminder: {reminder_details['event']}"
            email_body = f"Reminder: Don't forget the {reminder_details['event']} on {reminder_details['date']} at {reminder_details['time']}"
            send_reminder_email(email_subject, email_body)
            done = True
        else:
            #print statement for testing purposes only
            print(f"Waiting {datetime.now().time()}")
            thyme.sleep(10)

def process_input_reminder(user_input): 
    """process_input_reminder processes user input if it contained the reminder key phrase
    custom processing is performed, else, the input is passed onto get_response"""
    # i had to use a flag like this because using while True: was causing some issues with threading
    done = False 
    # Check if the user input contains the phrase "remind me"
    while not done:
    # Extract the reminder details from the user input
        reminder_details = extractor.extract_reminder_details(user_input)
        if reminder_details['date'] is not None and reminder_details['time'] is not None:
            date_date, time_time = extractor.extract_datetime_objects(user_input)
            print_cap_companion_output(f"Sure, your reminder will be sent to {stored_email.get()} on {reminder_details['date']} at {reminder_details['time']}")

            compare_date_thread = threading.Thread(target=compare_date, args=(date_date, time_time, reminder_details))
            compare_date_thread.start()
            done = True 
        else:
            #if date and time couldn't be extracted
            print_cap_companion_output("Sorry, I couldn't extract some of your time and date details. Consider asking me 'how do i send an email reminder?'.")
            done = True

# Function to create a notepad file with the bullet points the user specified 
def generate_checklist(checklist_items):
    """Generates a checklist with separate bullet points for each task"""
    today = dt.date.today()
    checklist = f"Your to-do list for {today}:\n"
    item_number = 1
    for item in checklist_items:
        checklist += f"{item_number}. {item}\n"
        item_number += 1

    # Save the checklist to a text file
    file_path = "checklist.txt"
    with open(file_path, "w") as file:
        file.write(checklist)

    # Open the text file using the default associated program
    subprocess.Popen(["notepad.exe", file_path])

def process_input_checklist(user_input):
    """Process the user input and create a checklist if requested"""
    checklist_items = extractor.extract_checklist_items(user_input)
    if checklist_items:
        generate_checklist(checklist_items)
        print_cap_companion_output("Thank you for providing your tasks. I have created a to-do list for you that will pop up automatically.")
    else:
        print_cap_companion_output("No tasks found. Consider asking me: 'How do i make a checklist?'")

# Function where user says "schedule me a meeting on (date) at (time) with (attendee) and (attendee) about (title)"
def process_input_schedule_meeting(user_input):
    """Process the user input and schedule a meeting if requested"""
    title, date, start_time, end_time, attendees = extractor.extract_meeting_details(user_input)
    print(f"Meeting Details: Title: {title}, Date: {date}, Start Time: {start_time}, Attendees: {attendees}")
    
    if title and date and start_time and attendees:
        # Respond with the extracted details
        print_cap_companion_output(f"Sure, I will schedule a meeting for you at {start_time} on {date} with {', '.join(attendees)} about {title.capitalize()}.")
        
        # Call the function to open Teams and schedule the meeting here
        meeting_scheduler.open_teams()
        on_main_monitor = meeting_scheduler.compare_teams_monitor_vs_main_monitor()
        if on_main_monitor:
            #click calendar
            if meeting_scheduler.click_calendar():
            # Click "New Meeting" button
                if meeting_scheduler.click_new_meeting():
                #get date object
                    date_date, time_time = extractor.extract_datetime_objects(user_input)
                    formatted_date = date_date.strftime("%d/%m/%Y")
                    #input meeting details
                    meeting_scheduler.input_meeting_details(title, attendees, formatted_date, start_time, end_time)
                else:
                    print_cap_companion_output("Sorry, I couldn't find the new meeting button.")
            else:
                print_cap_companion_output("Sorry, I couldn't find the calendar button.")
        else:
            print_cap_companion_output("Sorry, I couldn't move teams to your main monitor.")
    else:
        print_cap_companion_output("Sorry, I couldn't extract all of your meeting details.")   

# # Function to get weather information using OpenWeatherMap API key

def process_weather_input(user_input):
    """use the OpenWeatherMap API to return the weather information of the users given city"""
    api_key = "edb0bc92f68e59b85dea2a0c395ca0cd"  #OpenWeatherMap API key
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    city_name = extractor.extract_city_name(user_input)
    if city_name:
        try:
            params = {
                "q": city_name,
                "units": "metric",  # To get the temperature in Celsius
                "appid": api_key,
            }

            response = requests.get(base_url, params=params)
            data = response.json()

            if data["cod"] == 200:
                weather_description = data["weather"][0]["description"]
                temperature = data["main"]["temp"]
                response = f"The weather in {city_name.capitalize()} is {weather_description} with a temperature of {temperature}°C."
            else:
                response = "Sorry, I didn't understand your weather-related query. Please ensure the city is the last word of your prompt."

        except requests.RequestException as e:
            response = f"Error occurred while fetching weather data: {e}"
    
    print_cap_companion_output(response)
        
# Process Wikipedia related query
def process_wikipedia_input(user_input):
    """handle cases where the user requests wikipedia information"""
    topic = extractor.extract_topic(user_input)
    print("Extracted Topic:", topic)
    
    if topic:
        response = extractor.extract_wikipedia_summary(topic)
    else:
        response = "Sorry, I didn't understand your request. Consider asking me: 'How do i wiki something?'"

    print_cap_companion_output(response)

# Function to retrieve a response from the chatbot model
def get_response(user_input):
    """get_response takes in user_input and uses our language model to tokenize
    and process the input, returns the best response according to model"""
    model = init.init_model()
    data = init.init_data()
    device = init.init_device()
    all_words  = data['all_words']
    tags = data['tags']
    user_input = tokenize(user_input)
    X = bag_of_words(user_input, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.80:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                return random.choice(intent["responses"])

    # If no exact match is found, try fuzzy matching
    else:
        fuzzy_threshold = 75
        max_ratio = -1
        best_intent = ""

        for intent in intents["intents"]:
            for pattern in intent["patterns"]:
                ratio = fuzz.ratio(user_input, pattern.lower())
                if ratio > max_ratio:
                    max_ratio = ratio
                    best_intent = intent

        if max_ratio >= fuzzy_threshold:
            print("2")
            return random.choice(best_intent["responses"])

    return "Sorry, I didn't understand that."

#create the GUI window
window = tk.Tk()
window.title("Cap Companion")
window.geometry("600x800")
window.configure(bg=themes['Azure Sunset']['window_bg'])
    
# Create the email input entry field
email_frame = tk.Frame(window, bg=themes['Azure Sunset']['window_bg'])
email_frame.pack()
email_entry = tk.Entry(email_frame, bg=themes['Azure Sunset']['entry_bg'], fg=themes['Azure Sunset']['entry_fg'], font=("Arial", 12), width=22)
email_entry.pack(side=tk.LEFT, padx=5, pady=5)
email_entry.insert(0, "Enter your email address")  # Set the default text for email entry
email_entry.bind("<FocusIn>", lambda event: email_entry.delete(0, "end") if email_entry.get() == "Enter your email address" else None)
email_entry.bind("<FocusOut>", lambda event: email_entry.insert(0, "Enter your email address") if not email_entry.get() else None)

# Function to handle the submit button click event
def submit_email():
    """button for storing user provided email"""
    email = email_entry.get()
    stored_email.set(email)
    messagebox.showinfo("Success", "Email address stored successfully!")

# Create the submit button
submit_button = tk.Button(email_frame, text="Submit", command=submit_email, bg=themes['Azure Sunset']['button_bg'], fg=themes['Azure Sunset']['button_fg'], font=("Arial Black", 10, "bold"))
submit_button.pack(side=tk.LEFT, padx=5, pady=20)

# Create the chat display text box with tags for user and chatbot responses
chat_display = tk.Text(window, height=23, width=70, wrap="word", bg=themes['Azure Sunset']['chat_display_bg'], font=("Arial", 12))
chat_display.tag_configure("user_tag", foreground=themes['Azure Sunset']['user_tag_fg'], font=("Arial", 12, "bold"))
chat_display.tag_configure("user_text", foreground=themes['Azure Sunset']['user_text_fg'])
chat_display.tag_configure("chatbot_tag", foreground=themes['Azure Sunset']['chatbot_tag_fg'], font=("Arial", 12, "bold"))
chat_display.tag_configure("chatbot_text", foreground=themes['Azure Sunset']['chatbot_text_fg'])
chat_display.pack(pady=5)
chat_display.configure(state='disabled')

def enter_handler(event):
    """handle case when user presses 'Enter' after typing input"""
    text = text_entry.get()
    process_text(text)
    text_entry.delete(0, tk.END)

# Create the text input label and entry field
text_frame = tk.Frame(window, bg=themes['Azure Sunset']['window_bg'])
text_frame.pack()

text_entry = tk.Entry(text_frame, bg=themes['Azure Sunset']['entry_bg'], fg=themes['Azure Sunset']['entry_fg'], font=("Arial", 12), width=20)
text_entry.pack(side=tk.LEFT, padx=5)
text_entry.insert(0, "Enter your text")  # Set the default text for text entry

text_entry.bind("<FocusIn>", lambda event: text_entry.delete(0, "end") if text_entry.get() == "Enter your text" else None)
text_entry.bind("<FocusOut>", lambda event: text_entry.insert(0, "Enter your text") if not text_entry.get() else None)
text_entry.bind("<Return>", enter_handler)

# Create the microphone button without text, just a microphone symbol
microphone_button = tk.Button(text_frame, text="🎤", command=speech_to_text, bg=themes['Azure Sunset']['button_bg'], fg=themes['Azure Sunset']['button_fg'], font=("Arial Black", 14), width=3, height=1)
microphone_button.pack(side=tk.LEFT, padx=5)

def change_voice():
    """change the voice of cap_companion based on user selection"""
    # Define a list of voices to choose from
    voices = [
        {'name': 'Male', 'id': 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0'},
        {'name': 'Female', 'id': 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'},
    ]
    # Create a dialog box to select a voice
    voice_dialog = tk.Toplevel()
    voice_dialog.title("Select Voice")

    selected_voice = tk.StringVar(value=voices[0]['id'])

    # Create radio buttons for each voice
    for voice in voices:
        voice_radio = tk.Radiobutton(voice_dialog, text=voice['name'], value=voice['id'], variable=selected_voice)
        voice_radio.pack()

    # Create a button to confirm the voice selection
    confirm_button = tk.Button(voice_dialog, text="Confirm", command=lambda: set_voice(selected_voice.get()))
    confirm_button.pack()

def set_voice(voice_id):
    """set the voice property for pyttsx3"""
    # Stop and restart the speech engine with the selected voice
    engine = pyttsx3.init()
    engine.stop()
    engine.setProperty('voice', voice_id)
    engine.runAndWait()

# Create the voice change dropdown arrow
voice_change_button = tk.Button(text_frame, text="🚻", command=change_voice, bg=themes['Azure Sunset']['button_bg'], fg=themes['Azure Sunset']['button_fg'], font=("Arial Black", 14), width=3, height=1)
voice_change_button.pack(side=tk.LEFT, padx=5)

# Function to show the dropdown menu for changing the color template
def show_colour_template_dropdown(event):
    """display a dropdown menu of themes for the user to choose"""
    popup = tk.Toplevel(window)
    popup.geometry("350x100")
    popup.title("Themes")
    
    # Create a label to display a message for the pop up
    style = ttk.Style(popup)
    style.configure("TLabel", font=("Arial", 12), foreground="blue")
    message_label = ttk.Label(popup, text="Pick your favorite theme!", font=("Arial", 10, "bold"))
    message_label.pack(pady=10)

    # Create the Combobox for selecting color templates
    theme_names = list(themes.keys())
    popup_colour_template_combobox = ttk.Combobox(popup, values=theme_names)
    popup_colour_template_combobox.set(theme_names[0]) #default theme for drop down
    popup_colour_template_combobox.pack(pady=10)

    def change_colour_template_popup(event):
        """allow the user to choose a colour theme from a list of presets"""
        selected_template = popup_colour_template_combobox.get()
        if selected_template in themes:
            window.configure(bg=themes[selected_template]['window_bg'])
            text_frame.configure(bg=themes[selected_template]['window_bg'])
            email_frame.configure(bg=themes[selected_template]['window_bg'])
            chat_display.configure(bg=themes[selected_template]['chat_display_bg'])
            text_entry.configure(bg=themes[selected_template]['entry_bg'], fg=themes[selected_template]['entry_fg'])
            email_entry.configure(bg=themes[selected_template]['entry_bg'], fg=themes[selected_template]['entry_fg'])
            submit_button.configure(bg=themes[selected_template]['button_bg'], fg=themes[selected_template]['button_fg'])
            microphone_button.configure(bg=themes[selected_template]['button_bg'], fg=themes[selected_template]['button_fg'])
            voice_change_button.configure(bg=themes[selected_template]['button_bg'], fg=themes[selected_template]['button_fg'])
            chat_display.tag_configure("user_tag", foreground=themes[selected_template]['user_tag_fg'])
            chat_display.tag_configure("user_text", foreground=themes[selected_template]['user_text_fg'])
            chat_display.tag_configure("chatbot_tag", foreground=themes[selected_template]['chatbot_tag_fg'])
            chat_display.tag_configure("chatbot_text", foreground=themes[selected_template]['chatbot_text_fg'])
        else:
            print("theme broken")

        # Close the popup after the template is selected
        # popup.destroy()

    # Bind the event to the change_color_template_popup function
    popup_colour_template_combobox.bind("<<ComboboxSelected>>", change_colour_template_popup)

# Bind the event to show_color_template_dropdown function when chat_display is clicked
chat_display.bind("<Button-3>", show_colour_template_dropdown)

#variable storing user email address
stored_email = tk.StringVar()

def startup(event=None):
    window.bind("<Map>")
    audio_file = f"{os.path.dirname(__file__)}\\audio\\sound1.wav"
    playsound(audio_file)   
    current_time = datetime.now()
    current_time = current_time.time()
    noon = time(12, 0, 0)
    afternoon = time(17, 30, 0)
    greetings = ["How can I help you today?", "What can I do for you?", "Is there anything I can assist you with today?", "I hope your day is going well so far."]
    if current_time < noon:
        print_cap_companion_output(f"Good Morning! {random.choice(greetings)}")
    elif current_time < afternoon:
        print_cap_companion_output(f"Good Afternoon! {random.choice(greetings)}")
    else:
        print_cap_companion_output(f"Good Evening! {random.choice(greetings)}")
    window.unbind("<Map>")

def delayed_startup(event=None):
    window.after(100, startup)

if __name__ == "__main__":
    #runs the GUI window on a loop until quit
    delayed_startup()
    window.mainloop()