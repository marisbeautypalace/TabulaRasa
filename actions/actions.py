# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
'''

import datetime as dt
from datetime import timedelta
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from processing import eventProcessing
from rasa_sdk.events import SlotSet
from rasa_sdk.events import ReminderScheduled

URL = "http://kompetenzzentrum-lingen.digital/wp-json/tribe/events/v1/events"

class actionEventSelection(Action):

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


class ActionGetAllEvents(Action):
    def name(self) -> Text:
        return "action_get_all_events"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dfAllEvents = eventProcessing.getAllEvents(URL)
        carousel = eventProcessing.dfToCarousel(dfAllEvents)

        dispatcher.utter_message(attachment=carousel)        

        return []

class ActionGetEventsForCategory(Action):
    def name(self) -> Text:
        return "action_get_events_for_category"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot = tracker.get_slot("category_selection")
        
        dfAllEvents = eventProcessing.getAllEvents(URL)
        dfEventsForCategory = eventProcessing.getEventsForCategorie(dfAllEvents, slot)
        carousel = eventProcessing.dfToCarousel(dfEventsForCategory)

        dispatcher.utter_message(attachment=carousel)

        return []

class ActionGetEventsForCategorySelection(Action):
    def name(self) -> Text:
        return "action_get_events_for_category_selection"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        
        dfAllEvents = eventProcessing.getAllEvents(URL)
        setOfCategories = eventProcessing.setOfCategories(dfAllEvents)

        buttons = []

        for category in setOfCategories:
            slot = '{"category_selection":' + '"' + category + '"' + '}'
            buttons.append({"payload": '/Events_Category_Selection'+slot, "title": category})
        
        dispatcher.utter_message(response="utter_events_category_selection", buttons=buttons)

        return []


class ActionGetEventsForTimeframe(Action):
    def name(self) -> Text:
        return "action_get_events_for_timeframe"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot = tracker.get_slot("timeframe_selection")
        k = int(slot)

        dfAllEvents = eventProcessing.getAllEvents(URL)
        dfEventsForTimeframe = eventProcessing.getEventsForTimeframe(dfAllEvents, k)
        carousel = eventProcessing.dfToCarousel(dfEventsForTimeframe)

        dispatcher.utter_message(attachment=carousel)        

        return []

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


class ActionSetReminder(Action):
    """Schedules a reminder for 20 seconds of no interaction"""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # dispatcher.utter_message("I will remind you in 20 seconds.")
        
        date = dt.now() + timedelta(seconds=20)
        # entities = tracker.latest_message.get("entities")

        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            # entities=entities,
            name="my_reminder",
            kill_on_user_message=True,
        )

        return [reminder]

class ActionReactToReminder(Action):
    """Reminds the user to rate the bot after conversation."""

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

class ActionReceiveRating(Action):

    def name(self) -> Text:
        return "action_receive_rating"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       rating = tracker.latest_message['text']
       dispatcher.utter_message(response="utter_rating_thanks")
       
       file = open("ratings.csv", "a")
       file.write(str(rating) + ";" + str(dt.now()) + "\n")
       file.close()

       return [SlotSet("rating_selection",rating)]


class ActionSayRating(Action):

    def name(self) -> Text:
        return "action_say_rating"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       rating = tracker.get_slot("rating_selection")
       if not rating:
           dispatcher.utter_message(response="utter_no_rating_specified")
       else:
           dispatcher.utter_message(response="utter_repeat_rating_for_user", rating_selection=rating)
       
       return []
'''

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


'''
Preprocessing
'''

ssl._create_default_https_context = ssl._create_unverified_context

FORMAT_DATE = "%Y-%m-%d %H:%M:%S"

'''
Scraping for a url of the kompetenzzentrum lingen (json format)
IN: url = unique identifier used to locate the event resource of the kompetenzzentrum lingen on the internet
OUT: dfallEvents = dataframe which contains all events of the kompetenzzentrum lingen
'''

def getAllEvents(URL):
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

    dfAllEvents = pd.DataFrame(events)
    dfAllEvents = dfAllEvents.replace(to_replace=r'&#8211;', value='-', regex=True)
    return dfAllEvents

'''
Processes a data frame in such a way that only those events are included which fall into a specific timeframe (start of the timeframe is now)
IN: df = dataframe for processing
    k = days that define the end of the timeframe
OUT: df = dataframe that contains events in the specific timeframe
'''

def getEventsForTimeframe(df, k):
    start = datetime.now()
    end = start + timedelta(days=k)

    checkedEvents = []
    for column in df['start_date']:
        timestamp = datetime.fromisoformat(column)
        value = timestamp < end
        checkedEvents.append(value)

    for i in range(0, len(checkedEvents)):
        if (checkedEvents[i] == False):
            df = df.drop(i)

    return df

'''
Processes a data frame in such a way that only those events are included which fall into a specific categorie
IN: df = dataframe for processing
    categorie = category to which df is processed
OUT: df = dataframe that contains events for a specific categorie
'''

def getEventsForCategorie(df, category):
    checkedEvents = []

    for column in df['categories']:
        if category in column:
            checkedEvents.append(True)
        else:
            checkedEvents.append(False)

    for i in range(0, len(checkedEvents)):
        if (checkedEvents[i] == False):
            df = df.drop(i)

    return df

'''
Processes a data frame in such a way that only those events are included which cost less than the specified limit
IN: df = dataframe for processing
    limit = maximum costs that an event may cause
OUT: df = dataframe that contains events which do not exceed the limit
'''

def getEventsForCost(df, limit):
    checkedEvents = []

    if limit == 'Kostenlos' or 'kostenlos':
        limit = 0

    for column in df['cost']:
        if column == 'Kostenlos' or 'kostenlos':
            column = 0
        value = limit >= column
        checkedEvents.append(value)

    for i in range(0, len(checkedEvents)):
        if (checkedEvents[i] == False):
            df = df.drop(i)

    return df

def categoriesToString(categories):
    stringCategorie = ""
    for i in categories:
        stringCategorie = stringCategorie + i + ' | '
    return stringCategorie[:-2]

def wrapDate(date):
    return datetime.strptime(date, FORMAT_DATE)


def printDate(start, end):
    return start.strftime("%d.%m.%Y, %H:%M") + ' bis ' + end.strftime("%H:%M") + ' Uhr | '

def dfToCarousel(df):
    carousel = { "type": "template", "payload": { "template_type": "generic", "elements": [] } }

    for index, row in df.iterrows():
        title, url, image = row['title'], row['url'], row['image']
        categories = categoriesToString(row['categories'])
        wrappedStartDate = wrapDate(row['start_date'])
        wrappedEndDate = wrapDate(row['end_date'])
        subtitle = (printDate(wrappedStartDate, wrappedEndDate) + categories)
        carousel["payload"]["elements"].append({ "title": title, "subtitle": subtitle, "image_url": image, "buttons": [{ "title": "Zur Anmeldung", "url": url, "type": "web_url" }] })
    return carousel


def setOfCategories(df):
    listOfCategories = []
    for element in df['categories']:
        listOfCategories = listOfCategories + element

    setOfCategories = set(listOfCategories)
    return setOfCategories

'''
Custom Actions
'''

URL = "http://kompetenzzentrum-lingen.digital/wp-json/tribe/events/v1/events"

class actionEventSelection(Action):

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


class ActionGetAllEvents(Action):
    def name(self) -> Text:
        return "action_get_all_events"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dfAllEvents = getAllEvents(URL)
        carousel = dfToCarousel(dfAllEvents)

        dispatcher.utter_message(attachment=carousel)        

        return []

class ActionGetEventsForCategory(Action):
    def name(self) -> Text:
        return "action_get_events_for_category"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot = tracker.get_slot("category_selection")
        
        dfAllEvents = getAllEvents(URL)
        dfEventsForCategory = getEventsForCategorie(dfAllEvents, slot)
        carousel = dfToCarousel(dfEventsForCategory)

        dispatcher.utter_message(attachment=carousel)

        return []

class ActionGetEventsForCategorySelection(Action):
    def name(self) -> Text:
        return "action_get_events_for_category_selection"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        
        dfAllEvents = getAllEvents(URL)
        SetOfCategories = setOfCategories(dfAllEvents)

        buttons = []

        for category in SetOfCategories:
            slot = '{"category_selection":' + '"' + category + '"' + '}'
            buttons.append({"payload": '/Events_Category_Selection'+slot, "title": category})
        
        dispatcher.utter_message(response="utter_events_category_selection", buttons=buttons)

        return []


class ActionGetEventsForTimeframe(Action):
    def name(self) -> Text:
        return "action_get_events_for_timeframe"
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot = tracker.get_slot("timeframe_selection")
        k = int(slot)

        dfAllEvents = getAllEvents(URL)
        dfEventsForTimeframe = getEventsForTimeframe(dfAllEvents, k)
        carousel = dfToCarousel(dfEventsForTimeframe)

        dispatcher.utter_message(attachment=carousel)        

        return []

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


class ActionSetReminder(Action):
    """Schedules a reminder for 40 seconds of no interaction"""

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

class ActionReactToReminder(Action):
    """Reminds the user to rate the bot after conversation."""

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

class ActionGetSpecificEventCategory(Action):
    def name(self) -> Text:
        return "action_specific_event_category"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot1 = tracker.get_slot("EventType")
        slot = str(slot1)
        empty = 1

        dfAllEvents = getAllEvents(URL)
        SetOfCategories = setOfCategories(dfAllEvents)

        if slot != "":
            for x in SetOfCategories: 
                if slot in x:
                    #print("richtige Auswahl")
                    dfEventsForCategory = getEventsForCategorie(dfAllEvents, slot1)
                    #print (dfEventsForCategory)
                    carousel = dfToCarousel(dfEventsForCategory)
                    dispatcher.utter_message(attachment=carousel)
                    empty = 0
        if empty == 1:
                buttons = []
                for category in SetOfCategories:
                    slot = '{"category_selection":' + '"' + category + '"' + '}'
                    buttons.append({"payload": '/Events_Category_Selection'+slot, "title": category})
                dispatcher.utter_message(response="utter_no_event_found", buttons=buttons)

        '''
        file = open("data\lookup_eventtype.yaml", "w", encoding='utf-8')
        file.write("version: \"2.0\" \n"+
                    "nlu: \n" +
                    "- lookup: EventType \n" +
                    "  examples: | \n")
        file.close()

        file = open("data\lookup_eventtype.yaml", "a", encoding='utf-8')
        for category in setOfCategories:
            file.write("    - "+ category + "\n")
        file.close()
        '''

        return [SlotSet("EventType", "")]

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
