# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from processing import eventProcessing

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

        dispatcher.utter_message(text="Wir haben unterschiedliche Veranstaltungs- und Workshop-Angebote. Nach welchen Kriterien sollen die Veranstaltungen gefiltert werden?", buttons=buttons)
        

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
        
        dispatcher.utter_message(text="Nach welcher Kategorie soll gefiltert werden?", buttons=buttons)

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

        dispatcher.utter_message(text="Nach welchem Zeitraum soll gefiltert werden?", buttons=buttons)
        

        return []

# class ActionShowHyperlinkInUtter(Action):

#     def name(self) -> Text:
#         return "action_show_hyperlink_in_utter"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         Link-FAQ="https://kicc-prozesse.digital/faq/"
#         dispatcher.utter_template("utter_use_of_cloud", tracker, link=Link-FAQ)
        

#         return []

import datetime
from rasa_sdk.events import ReminderScheduled
from rasa_sdk import Action

class ActionSetReminder(Action):
    """Schedules a reminder for 15 seconds of no interaction"""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        date = datetime.datetime.now() + datetime.timedelta(seconds=15)

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

        dispatcher.utter_message(f"Sie haben seit 15 Sekunden keine neue Nachricht eingegeben.")

        return []