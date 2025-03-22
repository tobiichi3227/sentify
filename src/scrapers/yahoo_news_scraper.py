from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from config.config import TIMESTAMP_FORMAT, UTC_DIFFERENCE
from utils import data

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}


def get_news_URLs(
    ticker_symbol: str,
    start_timestamp: str,
    end_timestamp: str,
    title_flag: bool = False,
) -> list:
    API_URL = f"https://finance.yahoo.com/xhr/ncp?location=US&queryRef=newsAll&serviceKey=ncp_fin&listName={ticker_symbol}-news&lang=en-US&region=US"

    news_URLs = []

    uuid = ""

    while True:
        payload = {
            "payload": {
                "gqlVariables": {
                    "tickerStream": {"pagination": {"uuids": uuid}}
                }
            },
            "serviceConfig": {
                "s": [f"{ticker_symbol}"],
                "snippetCount": 5000,
            },
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            streams = response.json()["data"]["tickerStream"]["stream"]

            if not streams:
                break

            for stream in streams:
                if stream["content"]["clickThroughUrl"]:
                    publish_datetime = datetime.strptime(
                        stream["content"]["pubDate"], TIMESTAMP_FORMAT
                    )
                    shifted_publish_datetime = publish_datetime + timedelta(
                        hours=UTC_DIFFERENCE
                    )
                    shifted_publish_date = shifted_publish_datetime.strftime(
                        TIMESTAMP_FORMAT
                    )

                    start_datetime = datetime.strptime(
                        start_timestamp, TIMESTAMP_FORMAT
                    )
                    end_datetime = datetime.strptime(
                        end_timestamp, TIMESTAMP_FORMAT
                    )

                    if not (
                        start_datetime
                        <= shifted_publish_datetime
                        <= end_datetime
                    ):
                        continue

                    company_name = data.get_company_name_by_ticker(
                        ticker_symbol
                    )
                    news_title = stream["content"]["title"]

                    if (
                        title_flag
                        and company_name.lower() not in news_title.lower()
                        and ticker_symbol.lower() not in news_title.lower()
                    ):
                        continue

                    news_URLs.append(
                        {
                            "publish_date": shifted_publish_date,
                            "news_URL": stream["content"]["clickThroughUrl"][
                                "url"
                            ],
                            "news_title": news_title,
                        }
                    )

            uuid = response.json()["data"]["tickerStream"]["pagination"][
                "uuids"
            ]
        else:
            print(
                f"Failed to retrieve the page. Status code: {response.status_code}"
            )

    sorted_news_URLs = sorted(
        news_URLs,
        key=lambda x: datetime.strptime(x["publish_date"], TIMESTAMP_FORMAT),
        reverse=True,
    )
    return sorted_news_URLs


def get_news_paragraphs(news_URL: str) -> list[str]:
    response = requests.get(news_URL, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    news_body = soup.select_one(".body")

    news_paragraphs = []
    if news_body:
        for child in news_body.select("p"):
            text = child.get_text().strip()
            if text:
                news_paragraphs.append(text)

    else:
        print("No element found with class name: body")

    return news_paragraphs
