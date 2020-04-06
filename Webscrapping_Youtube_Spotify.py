# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:07:51 2020

@author: Leonardo
"""

# Step 1: Log into youtube
# Step 2: Grab our liked video
# Step 3: Create a new playlist
# Step 4: Search for the song
# Step 5: Add this song into the new Spotify playlist

# APIs: Youtube Data API: https://developers.google.com/youtube/v3
#       Spotify Web API: https://developer.spotify.com/documentation/web-api/

# Check if all the dependencies are already installed

import json
import requests
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl
from secrets import spotify_user_id, spotify_token

class CreatePlayList:
    
    def __init__(self):

        self.user_id = spotify_user_id #Spotify user id
        self.spotify_token = spotify_token # Spotify private token
        self.youtube_client = self.getYoutubeClient()
        self.all_songs_info = {}
    
# Step 1: Log into youtube    
    def getYoutubeClient(self):
        os.environ("") = "1"
        
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"
        
        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        credentials = flow.run_console()
        
        # from the Youtube Data API
        youtube_client = googleapiclient.discovery.build(api_service_name, api_versiom, credentials= credentials)
        
        return youtube_client
    
# Step 2: Grab our liked video    
    def getLikedVideos(self):
        
        request = self.youtube_client.videos().list(part="snippet,contentDetails,statistics", myRating="like")
        
        response = request.execute()
        
        # Collect each video and get important information
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["id"])
            
        # Use Youtube_DL to collect the song name & artist name
        video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download= False)
        
        song_name = video["track"]
        artist = video["artist"]

        # Salve all important information
        self.all_song_info[video_title] = {
                
                "youtube_url": youtube_url,
                "song_name": song_name,
                "artist": artist,
                
                # add the URI, easy to get song to put into playlist
                
                "spotify_url": self.getSpotifyURL(song_name)
                
                }       
        
# Step 3: Create a new playlist at Spotify        
    def createPlaylist(self):
        
        # Set parameters to the request body
        request_body = json.dumps({
                
                "name":"YouTube Liked videos",
                "description":"Liked YouTube videos",
                "public": True
                
                })
        
        # Connection string
        query = "	https://api.spotify.com/v1/users/{user_id}/playlists".format(self.user_id)        
        
        # POST request to Spotify Server
        response = requests.post(query,
                                 data = request_body,
                                 headers = {
                                             "Content-Type":"application/json",
                                             "Authorization":"Bearer{}".format(spotify_token)
                                         })
    
        # Retrieve the response in a local variable
        response_json = response.json()
        
        # Return playlist id
        return response_json["id"]
    
        
# Step 4: Search for the song    
    def getSpotifyURL(self, song_name):
        
        
        query = "	https://api.spotify.com/v1/search?q={}&type=track%2Cartist&offset=20".format(
                song_name)
 
        
        # GET request to Spotify Server
        response = requests.get(query,
                                 data = request_body,
                                 headers = {
                                             "Content-Type":"application/json",
                                             "Authorization":"Bearer{}".format(self.spotify_token)
                                         })
    
        # Retrieve the response in a local variable
        response_json = response.json()
        
        songs = response_json["tracks"]["items"]
        
        # Return playlist id
        return songs[0]["url"]      
        
        
# Step 5: Add this song into the new Spotify playlist    
    def addSongtoPlaylist(self):
        
        # Populate our songs dictionary
        self.getLikedVideos()
        
        uris = []
        # collect all url
        
        for song, info in self.all_song_info.items():
            
            uris.append(info["spotify_uri"])
        
        # create a new playlist
        playlist_id = self.create_playlist()
        
        # add all songs into new playlist
        request_data = json.dumps(uris)
        
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)
        
        response = requests.post(
                                 data = request_data,
                                 headers = {
                                             "Content-Type":"application/json",
                                             "Authorization":"Bearer{}".format(self.spotify_token)
                                         })
                
                )