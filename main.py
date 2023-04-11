from googleapiclient.discovery import build
import requests
import json

import os
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass


#===================    API KEYS    ==================
load_dotenv(find_dotenv())
@dataclass(frozen=True)
class APIkeys:
    YOUTUBE_API_KEY:str = os.getenv('YOUTUBE_API_KEY')
    TRELLO_API_KEY:str = os.getenv('TRELLO_API_KEY')
    TRELLO_API_TOKEN:str = os.getenv('TRELLO_API_TOKEN')
# ==================    ========    ==================

# FETCH Video titles from Youtube Data api, with given playlist ID

video_titles = []

def fetchYoutubeVideoTitles():
    playlist_title = ''
    """
        Fetches Video titles from PLAYLIST ID provided
        Use Youtube Data API
    """
    PLAYLIST_ID = "PLeo1K3hjS3uvCeTYTeyfe0-rN5r8zn9rw"
    next_page_token = None

    youtube = build('youtube','v3',developerKey=APIkeys.YOUTUBE_API_KEY)

    while True:
        #Get all playlist items 
        playlist_items = youtube.playlistItems().list(
            part='snippet',
            playlistId=PLAYLIST_ID,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in playlist_items['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            # save to array
            video_titles.append(video_title)
            # print(f'{video_title}:https:www.youtube.com/watch?v={video_id}')
        playlist_title += playlist_items['items'][0]['snippet']['title']
        next_page_token = playlist_items.get('next_page_token')
        if not next_page_token:
            break
        return playlist_title

card_id = 'a4rL2AkH'

def getCardID(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}"

    headers = {
    "Accept": "application/json"
    }

    query = {
    'key': APIkeys.TRELLO_API_KEY,
    'token': APIkeys.TRELLO_API_TOKEN
    }

    response = requests.request(
    "GET",
    url,
    headers=headers,
    params=query
    )
    dict_response = json.loads(response.text)
    return dict_response['id']

def create_checklist(formatted_card_id,playlist_title):
    url = "https://api.trello.com/1/checklists"

    create_checklist_query = {
      'idCard': formatted_card_id,
      'name': playlist_title,
      'key': APIkeys.TRELLO_API_KEY,
      'token': APIkeys.TRELLO_API_TOKEN
    }

    create_checklist_response = requests.request(
       "POST",
       url,
       params=create_checklist_query
    )
    print("After creating playlist:", json.loads(create_checklist_response.text))

def last_checklist_id(formatted_card_id):

    get_checklists_url = f"https://api.trello.com/1/cards/{formatted_card_id}/checklists"

    get_checklists_query = {
      'key': APIkeys.TRELLO_API_KEY,
      'token': APIkeys.TRELLO_API_TOKEN
    }

    get_checklists_response = requests.request(
       "GET",
       get_checklists_url,
       params=get_checklists_query
       )
    return json.loads(get_checklists_response.text)[-1]['id']

def addItemsToPlayList(formatted_card_id):
    create_checkitem_url = f"https://api.trello.com/1/checklists/{formatted_card_id}/checkItems"

    create_checkitem_query = {
      'name': video_titles[0],
      'key': APIkeys.TRELLO_API_KEY,
      'token': APIkeys.TRELLO_API_TOKEN
    }

    response = requests.request(
       "POST",
       create_checkitem_url,
       params=create_checkitem_query
    )

    print("After adding items to playlist, response is: {0}".format(response.text))

# get card id - 24 chr long
formatted_card_id = getCardID(card_id)

playlist_title = fetchYoutubeVideoTitles()
# create a checklist in it
create_checklist(formatted_card_id,playlist_title)

# get id corresponding to checklist
latest_checklist_id = last_checklist_id(formatted_card_id)

# add item to checklist with given id
addItemsToPlayList(latest_checklist_id)