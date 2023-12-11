# generate_tourist_data.py

import requests
import time
import json

def get_places_google_textsearch(city, place_type):
    query = f"{place_type} in {city}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key=AIzaSyBlP0PfB6LGsrgS4urCdE9Mn22fwfaJSFw"
    filtered_places = []

    while True:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}, {response.text}")
            break

        data = response.json()
        places = data.get('results', [])

        for place in places:
            filtered_place = {
                "formatted_address": place.get("formatted_address"),
                "name": place.get("name"),
                "rating": place.get("rating"),
                "types": place.get("types"),
                "user_ratings_total": place.get("user_ratings_total")
            }
            filtered_places.append(filtered_place)

        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break

        time.sleep(2)
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={next_page_token}&key=AIzaSyBlP0PfB6LGsrgS4urCdE9Mn22fwfaJSFw"

    return filtered_places


def save_data_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def generate_large_data_set(api_key):
    # 假设这里有一个列表，包含不同的搜索关键词或地理位置
    search_terms = ["tourist_attraction", "establishment", "restaurant", "landmark"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", 
        "Philadelphia", "Phoenix", 
    ]

    all_places = {}

    for city in cities:
        city_places = []
        for term in search_terms:
            places = get_places_google_textsearch(city, term)
            city_places.extend(places)
        all_places[city] = city_places

    save_data_to_json(all_places, "tourist_data_set.json")


generate_large_data_set('AIzaSyBlP0PfB6LGsrgS4urCdE9Mn22fwfaJSFw')


def main():
    api_key = 'AIzaSyBlP0PfB6LGsrgS4urCdE9Mn22fwfaJSFw'
    generate_large_data_set(api_key)

if __name__ == "__main__":
    main()