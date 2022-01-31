# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from datetime import timedelta, datetime
from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import ReminderScheduled
from rasa_sdk.forms import FormAction
from urllib.request import urlopen
import json
import pandas as pd
import ssl
import urllib.request

FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
URL = "http://kompetenzzentrum-lingen.digital/wp-json/tribe/events/v1/events"

ssl._create_default_https_context = ssl._create_unverified_context

'''
##############
PREPROCESSING
##############
'''

'''
Scraping for a url of the kompetenzzentrum lingen (json format)
IN: url = unique identifier used to locate the event resource of the kompetenzzentrum lingen on the internet
OUT: df_all_events = dataframe which contains all events of the kompetenzzentrum lingen
'''
def get_all_events(URL):
    response = urllib.request.urlopen(URL)
    data_json = json.loads(response.read())

    events = []

    for item in data_json['events']:
        categories = []
        for items in item['categories']:
            categories.append(items['name'])

        events.append({
            'id': item['id'],
            'url': item['url'],
            'title': item['title'],
            'excerpt': item['excerpt'][3:-4],
            'image': item['image']['url'],
            'start_date': item['start_date'],
            'end_date': item['end_date'],
            'cost': item['cost'],
            'categories': categories
        })

    df_all_events = pd.DataFrame(events)
    df_all_events = df_all_events.replace(to_replace=r'&#8211;', value='-', regex=True)

    return df_all_events

'''
Processes a data frame in such a way that only those events are included which fall into a specific timeframe (start of the timeframe is now)
IN: df = dataframe for processing
    k = days that define the end of the timeframe
OUT: df = dataframe that contains events in the specific timeframe
'''
def get_events_for_timeframe(df, k):
    start = datetime.now()
    end = start + timedelta(days=k)

    checked_events = []
    for column in df['start_date']:
        timestamp = datetime.fromisoformat(column)
        value = timestamp < end
        checked_events.append(value)

    for i in range(0, len(checked_events)):
        if (checked_events[i] == False):
            df = df.drop(i)

    return df

'''
Processes a data frame in such a way that only those events are included which fall into a specific categorie
IN: df = dataframe for processing
    categorie = category to which df is processed
OUT: df = dataframe that contains events for a specific categorie
'''
def get_events_for_categorie(df, category):
    checked_events = []

    for column in df['categories']:
        if category in column:
            checked_events.append(True)
        else:
            checked_events.append(False)

    for i in range(0, len(checked_events)):
        if (checked_events[i] == False):
            df = df.drop(i)

    return df

'''
Processes a data frame in such a way that only those events are included which cost less than the specified limit
IN: df = dataframe for processing
    limit = maximum costs that an event may cause
OUT: df = dataframe that contains events which do not exceed the limit
'''
def get_events_for_cost(df, limit):
    checked_events = []

    if limit == 'Kostenlos' or 'kostenlos':
        limit = 0

    for column in df['cost']:
        if column == 'Kostenlos' or 'kostenlos':
            column = 0
        value = limit >= column
        checked_events.append(value)

    for i in range(0, len(checked_events)):
        if (checked_events[i] == False):
            df = df.drop(i)

    return df

'''
Converts categories to string type
IN: categories = raw data from website
OUT: string_categorie = raw data converted to string type
'''
def categories_to_string(categories):
    string_categorie = ""

    for i in categories:
        string_categorie = string_categorie + i + ' | '

    return string_categorie[:-2]

'''
Converts string to datetime object
IN: date = date as string
OUT: date as datetime object
'''
def wrap_date(date):
    return datetime.strptime(date, FORMAT_DATE)

'''
Print start date and end date in suitable string format for the carousel
IN: start = startdate for an event
    end = enddate for an event
OUT: suitable string format for the carousel
'''
def print_date(start, end):
    return start.strftime("%d.%m.%Y, %H:%M") + ' bis ' + end.strftime("%H:%M") + ' Uhr | '

'''
Converts a dataframe to a carousel containing all events
IN: df = dataframe with all events
OUT: carousel = specific carousel format
'''
def df_to_carousel(df):
    carousel = { "type": "template", "payload": { "template_type": "generic", "elements": [] } }

    for index, row in df.iterrows():
        title, url, image = row['title'], row['url'], row['image']
        categories = categories_to_string(row['categories'])
        wrapped_start_date = wrap_date(row['start_date'])
        wrapped_end_date = wrap_date(row['end_date'])
        subtitle = (print_date(wrapped_start_date, wrapped_end_date) + categories)
        carousel["payload"]["elements"].append({ "title": title, "subtitle": subtitle, "image_url": image, "buttons": [{ "title": "Zur Anmeldung", "url": url, "type": "web_url" }] })
   
    return carousel

'''
Converts a list of categories to a set of categories
IN: df = dataframe with all events
OUT: set_of_categories = set of all categories 
'''
def get_set_of_categories(df):
    list_of_categories = []

    for element in df['categories']:
        list_of_categories = list_of_categories + element

    set_of_categories = set(list_of_categories)
    return set_of_categories

'''
##############
CUSTOM ACTIONS
##############
'''

'''
Action class for events selection (filter options: all, category, timeframe)
'''
class ActionEventSelection(Action):
    def name(self) -> Text:
        return "action_event_selection"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        buttons=[
            {"payload":"/Events_All", "title": "Anzeigen aller Veranstaltungen"},
            {"payload":"/Events_Category", "title": "Veranstaltungen nach Kategorie filtern"},
            {"payload":"/Events_Timeframe", "title": "Veranstaltungen nach Zeitraum filtern"}
        ]

        dispatcher.utter_message(response="utter_event_selection", buttons=buttons)  

        return []

'''
Action class to get all events
'''
class ActionGetAllEvents(Action):
    def name(self) -> Text:
        return "action_get_all_events"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        df_all_events = get_all_events(URL)
        carousel = df_to_carousel(df_all_events)

        dispatcher.utter_message(attachment=carousel)        

        return []

'''
Action class to get all events for specific category
'''
class ActionGetEventsForCategory(Action):
    def name(self) -> Text:
        return "action_get_events_for_category"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot = tracker.get_slot("category_selection")
        
        df_allevents = get_all_events(URL)
        df_events_for_category = get_events_for_categorie(df_allevents, slot)
        carousel = df_to_carousel(df_events_for_category)

        dispatcher.utter_message(attachment=carousel)

        return []

'''
Action class to get all events for specific category
'''
class ActionGetEventsForCategorySelection(Action):
    def name(self) -> Text:
        return "action_get_events_for_category_selection"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        df_all_events = get_all_events(URL)
        set_of_categories = get_set_of_categories(df_all_events)

        buttons = []

        for category in set_of_categories:
            slot = '{"category_selection":' + '"' + category + '"' + '}'
            buttons.append({"payload": '/Events_Category_Selection'+slot, "title": category})
        
        dispatcher.utter_message(response="utter_events_category_selection", buttons=buttons)

        return []

'''
Action class to get all events for specific timeframe
'''
class ActionGetEventsForTimeframe(Action):
    def name(self) -> Text:
        return "action_get_events_for_timeframe"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot = tracker.get_slot("timeframe_selection")
        k = int(slot)

        df_all_events = get_all_events(URL)
        df_events_for_timeframe = get_events_for_timeframe(df_all_events, k)
        carousel = df_to_carousel(df_events_for_timeframe)

        dispatcher.utter_message(attachment=carousel)        

        return []

'''
Action class to get all events for specific timeframe
'''
class ActionGetEventsForTimeframeSelection(Action):
    def name(self) -> Text:
        return "action_get_events_for_timeframe_selection"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        buttons=[
            {"payload": '/Events_Timeframe_Selection{"timeframe_selection":"7"}', "title": "In den nächsten 7 Tagen"},
            {"payload": '/Events_Timeframe_Selection{"timeframe_selection":"30"}', "title": "In den nächsten 30 Tagen"},
            {"payload": '/Events_Timeframe_Selection{"timeframe_selection":"60"}', "title": "In den nächsten 60 Tagen"},
        ]

        dispatcher.utter_message(response="utter_events_timeframe_selection", buttons=buttons)

        return []

'''
Action class to set a reminder after 40 seconds without interaction
'''
class ActionSetReminder(Action):
    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:      
        
        date = datetime.now() + timedelta(seconds=40)
       
        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            
            name="my_reminder",
            kill_on_user_message=True,
        )

        return [reminder]

'''
Action class to remind the user to rate the bot
'''
class ActionReactToReminder(Action):
    def name(self) -> Text:
        return "action_react_to_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_no_user_message")

        return []

'''
Action class to get a specific event category
'''
class ActionGetSpecificEventCategory(Action):
    def name(self) -> Text:
        return "action_specific_event_category"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot1 = tracker.get_slot("EventType")
        slot = str(slot1)
        empty = 1

        df_all_events = get_all_events(URL)
        set_of_categories = set_of_categories(df_all_events)

        if slot != "":
            for x in set_of_categories: 
                if slot in x:
                    #print("richtige Auswahl")
                    dfEventsForCategory = get_events_for_categorie(df_all_events, slot1)
                    #print (dfEventsForCategory)
                    carousel = df_to_carousel(dfEventsForCategory)
                    dispatcher.utter_message(attachment=carousel)
                    empty = 0
        if empty == 1:
                buttons = []
                for category in set_of_categories:
                    slot = '{"category_selection":' + '"' + category + '"' + '}'
                    buttons.append({"payload": '/Events_Category_Selection'+slot, "title": category})
                dispatcher.utter_message(response="utter_no_event_found", buttons=buttons)

        return [SlotSet("EventType", "")]

'''
Action class for receiving a rating
'''
class ActionReceiveRating(Action):
    def name(self) -> Text:
        return "action_receive_rating"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       rating = tracker.latest_message['text']
       dispatcher.utter_message(response="utter_rating_give_qualitative_feedback")
       
       file = open("ratings.csv", "a")
       file.write(str(rating) + ";" + str(datetime.now()) + "\n")
       file.close()

       return [SlotSet("rating_selection",rating)]

'''
Action class for the qualitative feedback form
'''
class QualitativeFeedbackForm(FormAction):
    def name(self) -> Text:
        return "qualitative_feedback_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["qualitative_feedback"]
    
    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "qualitative_feedback": self.from_text(),
        }

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        qualitative_feedback = tracker.get_slot("qualitative_feedback")

        file = open("ratings.csv", "a")
        file.write(str(qualitative_feedback) + ";" + str(datetime.now()) + "\n")
        file.close()

        return [SlotSet("qualitative_feedback",qualitative_feedback)]

'''
Action class for the rating
'''
class ActionSayRating(Action):
    def name(self) -> Text:
        return "action_say_rating"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       rating = tracker.get_slot("rating_selection")
       qualitative_feedback = tracker.get_slot("qualitative_feedback")
       if not rating:
           dispatcher.utter_message(response="utter_no_rating_specified")
       else:
           dispatcher.utter_message(response="utter_repeat_rating_for_user", rating_selection=rating)
           if qualitative_feedback:
               dispatcher.utter_message(response="utter_repeat_qualitative_feedback_for_user", qualitative_feedback=qualitative_feedback)
       
       return []
