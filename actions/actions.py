# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import datetime
from datetime import datetime, timedelta
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
        
        date = datetime.now() + timedelta(seconds=20)
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
       file.write(str(rating) + ";" + str(datetime.now()) + "\n")
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