from openai import OpenAI
import json
import os
os.chdir(os.path.dirname(__file__))


def prompt(input_text):
    
    with open("keys.txt", 'r') as file:
        keys = json.load(file)
        GPTkey = keys["GPT_KEY"]
    
    client = OpenAI(api_key=GPTkey)

    # OpenAI API call
    response = client.responses.create(
        model="gpt-5-mini-2025-08-07",
        # reasoning={"effort": "low"},
        instructions="You are given a worship song, convert it to chordpro format. Be true to the input, and only return the converted song \n Respect line breaks and keep different tacts seperate with '|' or linebreaks in instrumental parts, link chords with the text",
        input=input_text,
    )
    return response.output_text

def song_convert(song):
    converted_song = prompt(song)
    return converted_song

#læs sang
with open("song.txt", 'r',encoding='utf-8') as songfile:
    testsong = songfile.read()
    converted_song = song_convert(testsong)
#skriv sang
with open("converted_song.chordpro","w",encoding='utf-8') as file:
    file.write(converted_song)
    