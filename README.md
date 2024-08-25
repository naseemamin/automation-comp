# **Cap Companion, Personal Assistant** 
### Team: Callum McGregor, Salma Mohamud, Jasleen Kaur, and Naseem Amin
### See our product website: https://jasleenakaur.wixsite.com/aicapcompanion
---
## **How to run Cap Companion**

1. Git clone this repository to your local machine
2. Pip install all python modules required packages listed in this readme file
3. in a terminal, cd into wherever you have cloned this repository on your local machine
4. once inside the main directory this repository, run: **python cap_companion.py**
5. If you have installed all the below repositories after 5-10 seconds Cap Companion should open
   1. if it doesn't, check the terminal for error messages of missing packages or files
   2. if a package is missing, try pip installing that package
   3. if a file is missing, such as data.pth in train_model/ run the train.py file by running: **python train_model/train.py**
   4. if you encounter any other issues, contact the Cap Companion Team

---
## **How to use Cap Companion's prebuilt features**

### **Interacting with Cap Companion**
You can interact with Cap Companion in two main ways
1. Typing your input into the text box at the bottom of the GUI and pressing enter  
   1. as long as Cap Companion is trained to interpret your input, it will respond
2. Using your voice by pressing the microphone button at the bottom of the GUI
   1. Press the mic button, wait half a second or so, and clearly and loudly say your prompt
   2. background noise and quiet speech will reduce the effectiveness of this feature

Most of Cap Companion's main features have 'how to' prompts that can be used when you're unsure how to prompt cap companion for a specific feature. If you know *kind of* what you want Cap Companion to do, try asking it, 'what prompt does X for me?' 
Failing this; check the train_model/intents.json file for exact prompts required

### **Meeting Scheduler**
One example of a prompt that will schedule a meeting for you is "Book a meeting on the 5th of August at 13:30 with Callum McGregor and Salma Mohamud about Terraform"

### **Email Reminder**
One example of a prompt that will set an eamil reminder for you is "Remind me to go to the gym at 18:30 on the 5th of August"
Note: You must have submitted an email at the top of the GUI for this function to work, and because of firewalls, **your Capgemini email will not work**
Note: Inputting dates and times in the past may cause bugs

### **Checklist Creator**
One example of a prompt that will create a checklist for you is "Create me a checklist my tasks are to first go to the gym, 2 go shopping, 3rd get milk"
Note: as demonstrated in the above prompt, you can use either words or integers to specify the items of your checklist

### **Wiki Feature**
One example prompt that will query Wikipedia for you is "tell me about goldfish"
Note: Ensure the topic is the last word in the prompt
Note: To query multi-word topics, place a - between each word, e.g., "tell me about agile-methodology"

### **Weather Checker**
One example prompt that will check the weather for you in any given city is "whats the weather like in london?"
Note: ensure the city is the last word in the prompt

### **Changing Themes** (from selection of preset themes)
To change colour theme, right click the main chatbot GUI text window where input and output is shown, a popup will appear with a drop down menu of preset colour themes

### **Changing Voices**
To change the voice from masculine to feminine and vice versa, click the man and woman icon in the bottom right of the GUI and select the voice you'd like Cap Companion to respond to you in
---

## **How to modify Cap Companion to your needs**

### Modifying what Cap Companion can interpret and respond with
To modify the prompts Cap Companion can interpret and respond with, you must first update the train_model/intents.json file
1. follow the format we've used for existing prompts in the file to add your own custom information
   1. the 'patterns' are what cap companion will look for in your prompt, add as many prompts as you like to make cap companions ability to understand your prompt robust
   2. the 'responses' are what cap companion will respond with

2. Once you've updated the intents.json file, you need to run the train_model/train.py file, simply cd into train_model and run **python train.py**
3. Once this has finished the chatbot will now be able to respond to your new inputs with the specified responses

### Modifying Cap Companion's Themes
To modify Cap Companions themes, open the functions/themes.py file, this contains a nested dictionary of themes. To view what colours Tkinter readily supports, open this link: https://i0.wp.com/www.wikipython.com/wp-content/uploads/Color-chart-capture-082321.jpg?resize=1536%2C869&ssl=1

You can change elements of the tkinter GUI interface from here and add new themes by following the format we've used for existing colour themes

### Modifying Cap Companion's Functions
To add custom functions to Cap Companion, you'll need to develop the function yourself (obviously), and for Cap Companion to be able to trigger your function, you add to the intents.json as we explained above, then follow the way we trigger functions by looking at the tag called 'wiki_function', note the response.

Then, look at the function in the main cap_companion.py file called 'process_text', follow how we've triggered functions here and you'll be well on your way to triggering custom functions!
---

### **Python module requirements you may need to install via pip:**
1. speechrecognition
2. pyttsx3
3. pyaudio
4. torch
5. spacy
6. nltk
7. fuzzywuzzy
8. dateutil
9. numpy
10. pyautogui
11. opencv
12. requests
13. win32api
14. win32con
15. win32gui
16. playsound==1.2.2 (latest version of playsound has a bug)

### **Other required packages:**
1. python -m spacy download en_core_web_sm

### Python module requirements that should be preinstalled with Python, but if you encounter errors, try pip installing them:
1. tkinter
2. threading
3. json
4. time
5. datetime
6. email
7. re
8. os

