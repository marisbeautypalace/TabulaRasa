from urllib.request import urlopen
import json
import pandas as pd
import datetime as dt
import ssl
import urllib.request

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
    start = dt.datetime.now()
    end = start + dt.timedelta(days=k)

    checkedEvents = []
    for column in df['start_date']:
        timestamp = dt.datetime.fromisoformat(column)
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
    return dt.datetime.strptime(date, FORMAT_DATE)

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