import requests
import csv

url = "https://www.radiorecord.ru/api/stations"
response = requests.get(url)
data = response.json()

stations = data["result"]["stations"]

station_list = []

for station in stations:
    station_list.append({
        'station': station["title"],
        'audio_url': station.get("stream_320"),
        'data_url': f'https://app-api.radiorecord.ru/api/station/history/?id={station["id"]}'
    })

with open('../cogs/stations.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['station', 'audio_url', 'data_url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

    writer.writeheader()
    for item in station_list:
        writer.writerow(item)