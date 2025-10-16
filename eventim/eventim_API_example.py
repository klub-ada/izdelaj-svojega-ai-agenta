"""
https://public-api.eventim.com/websearch/search/api/exploration/v1/products?webId=web__eventim-svn&language=sl&page=1&sort=DateAsc&=&top=50

API endpoint:
https://public-api.eventim.com/websearch/search/api/exploration/v1/products

?webId=web__eventim-svn&language=sl&page=1&sort=DateAsc&=&top=50
Query parameters
- webId: web__eventim-svn
- language: sl
- page: 1 (to get different pages, increment this number)
- sort: DateAsc (sort by date ascending)
- top: 50 (number of results per page, max 50)
... other parameters can be found and experimented with from the example response

Entry example in the products response:
        {
            "productId": "20541596",
            "productGroupId": "3956223",
            "name": "Tematski park za vso družino",
            "type": "LiveEntertainment",
            "status": "Available",
            "link": "https://www.eventim.si/event/tematski-park-za-vso-druzino-koruzni-labirint-krtina-20541596/",
            "url": {
                "path": "/event/tematski-park-za-vso-druzino-koruzni-labirint-krtina-20541596/",
                "domain": "https://www.eventim.si"
            },
            "imageUrl": "https://www.eventim.si/obj/media/SI-eventim/teaser/222x222_SI/2025/image_1755066103702.jpg",
            "price": 11.00,
            "currency": "EUR",
            "inStock": true,
            "typeAttributes": {
                "liveEntertainment": {
                    "startDate": "2025-08-13T12:00:00+02:00",
                    "endDate": "2025-10-31T20:00:00+01:00",
                    "location": {
                        "name": "Koruzni labirint Krtina",
                        "city": "Krtina",
                        "postalCode": "1233",
                        "geoLocation": {
                            "longitude": 14.662801425188553,
                            "latitude": 46.1503917927049
                        }
                    }
                }
            },
            "attractions": [
                {
                    "name": "Tematski park za vso družino"
                }
            ],
            "categories": [
                {
                    "name": "Dodatno"
                },
                {
                    "name": "Zabava",
                    "parentCategory": {
                        "name": "Dodatno"
                    }
                }
            ],
            "rating": {
                "count": 0,
                "average": 0.0
            },
            "tags": [
                "TICKETDIRECT",
                "WILL_CALL"
            ],
            "hasRecommendation": false
        },
"""

import requests
import json

class EventimAPI:
    BASE_URL = "https://public-api.eventim.com/websearch/search/api/exploration/v1/products"

    def __init__(self, web_id="web__eventim-svn", language="sl"):
        self.web_id = web_id
        self.language = language
        self.page = 1
        self.sort = "DateAsc"
        self.top = 50

    def fetch_events(self, page=1, sort="DateAsc", top=50):
        params = {
            "webId": self.web_id,
            "language": self.language,
            "page": page,
            "sort": sort,
            "top": top
        }
        response = requests.get(self.BASE_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_event_details(self, event):
        details = {
            "productId": event.get("productId"),
            "name": event.get("name"),
            "type": event.get("type"),
            "status": event.get("status"),
            "link": event.get("link"),
            "imageUrl": event.get("imageUrl"),
            "price": event.get("price"),
            "currency": event.get("currency"),
            "inStock": event.get("inStock"),
            "startDate": event.get("typeAttributes", {}).get("liveEntertainment", {}).get("startDate"),
            "endDate": event.get("typeAttributes", {}).get("liveEntertainment", {}).get("endDate"),
            "location": event.get("typeAttributes", {}).get("liveEntertainment", {}).get("location", {}),
            "categories": [cat.get("name") for cat in event.get("categories", [])],
            "tags": event.get("tags", [])
        }
        return details

if __name__ == "__main__":
    api = EventimAPI()
    events_data = api.fetch_events(page=1)
    events = events_data.get("products", [])

    for event in events:
        details = api.get_event_details(event)
        print(json.dumps(details, indent=4, ensure_ascii=False))