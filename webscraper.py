# Source - https://stackoverflow.com/a
# Posted by LeOverflow
# Retrieved 2025-11-20, License - CC BY-SA 4.0
from requests import get
from bs4 import BeautifulSoup
from json import loads


def get_links_for_images(url: str) -> list[str]:
    res = get(url)

    if res.status_code == 200:

        soup = BeautifulSoup(res.text, features="html.parser")

        return [link.get('src') for link in soup.find_all('img')]

    return {"error": "No dice"}
