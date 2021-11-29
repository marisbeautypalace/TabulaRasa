# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from processing import eventProcessing

url = "http://kompetenzzentrum-lingen.digital/wp-json/tribe/events/v1/events"

# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

class ActionGetAllEvents(Action):

    def name(self) -> Text:
        return "action_get_all_events"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        countAllEvents = eventProcessing.getAllEvents(url)
        dispatcher.utter_message(text="Hier sehen Sie alle Veranstaltungen:")
        dispatcher.utter_message(text=f"{countAllEvents}")

        return []



