import requests
from lxml import html
import re
from typing import Dict
from dms2dec.dms_convert import dms2dec
from utils import setup_logging

logger = setup_logging()


class CastleData:
    def __init__(self, info_url: str):
        self.info_url = info_url
        self.data = self.fetch_castle_info()

    def fetch_castle_info(self) -> Dict:
        castle = {"url": self.info_url, "has_error": False, "error_message": None}

        try:
            r = requests.get(self.info_url, timeout=10)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_message = f"Request error fetching {self.info_url}: {e}"
            logger.error(error_message)
            castle.update(
                {"name": "Unknown", "has_error": True, "error_message": error_message}
            )
            return castle
        tree = html.fromstring(r.content)

        castle["name"] = self._parse_name(tree)
        castle["description"], castle["location_text"] = (
            self._parse_description_location(tree)
        )
        castle["coordinates"] = self._parse_coordinates(castle["location_text"])
        castle["literature"] = self._parse_literature(tree)
        castle["url"] = r.url

        return castle

    def _parse_name(self, tree):
        try:
            return tree.xpath('//h1[@class="xtra-post-title-headline"]/text()')[
                0
            ].strip()
        except Exception as e:
            error_message = f"Error parsing name for {self.info_url}: {e}"
            logger.error(error_message)
            self.data["has_error"] = True
            self.data["error_message"] = error_message
            return "Unknown"

    def _parse_description_location(self, tree):
        try:
            description = tree.xpath(
                '//p[following-sibling::h2[text()="Местоположение"]]/text()'
            )
            location_text = tree.xpath(
                '//h2[text()="Местоположение"]/following-sibling::p[1]/text()'
            )
            return " ".join(description).strip(), " ".join(location_text).strip()
        except Exception as e:
            error_message = (
                f"Error parsing description or location for {self.info_url}: {e}"
            )
            logger.error(error_message)
            self.data["has_error"] = True
            self.data["error_message"] = error_message
            return "", ""

    def _parse_coordinates(self, location_text):
        try:
            coordinate_pattern = (
                r"(\d{2}°\d{2}'\d{2}\")\s*С\.Ш\.\s*и\s*(\d{2}°\d{2}'\d{2}\")\s*И\.Д\."
            )
            coordinates_match = re.search(coordinate_pattern, location_text)
            if coordinates_match:
                dms_lat, dms_lon = coordinates_match.groups()
                return {
                    "latitude": dms2dec(dms_lat),
                    "longitude": dms2dec(dms_lon),
                    "original": f"{dms_lat} С.Ш. и {dms_lon} И.Д.",
                }
            return None
        except Exception as e:
            error_message = f"Error parsing coordinates for {self.info_url}: {e}"
            logger.error(error_message)
            self.data["has_error"] = True
            self.data["error_message"] = error_message
            return None

    def _parse_literature(self, tree):
        try:
            return [
                lit.strip()
                for lit in tree.xpath(
                    "//p[preceding-sibling::h2[text()='Литература']]/text()"
                )
                if lit.strip()
            ]
        except Exception as e:
            error_message = f"Error parsing literature for {self.info_url}: {e}"
            logger.error(error_message)
            self.data["has_error"] = True
            self.data["error_message"] = error_message
            return []

    def __str__(self):
        return f"Castle: {self.data['name']}, Location: {self.data.get('location_text', 'N/A')}, Coordinates: {self.data.get('coordinates', 'N/A')}"


def __str__(self):
    return f"Castle: {self.data['name']}, Location: {self.data.get('location_text', 'N/A')}, Coordinates: {self.data.get('coordinates', 'N/A')}, Error: {self.data['has_error']}"
