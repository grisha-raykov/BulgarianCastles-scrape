from typing import Dict, List
import requests
from lxml import html
import re
import logging

# import sqlite3
from dms2dec.dms_convert import dms2dec

logging.basicConfig(
    filename="castle_scraper.log",
    level=logging.ERROR,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


class Castle:
    def __init__(self, info_url: str):
        self.info_url = info_url
        self.data = self.fetch_castle_info()

    def fetch_castle_info(self) -> Dict:
        castle = {}
        try:
            r = requests.get(self.info_url, timeout=10)
            r.raise_for_status()
        except requests.exceptions.Timeout:
            logging.error(f"Timeout error fetching {self.info_url}")
            return {"name": "Unknown", "url": self.info_url, "error": "Timeout"}
        except requests.exceptions.TooManyRedirects:
            logging.error(f"Too many redirects for {self.info_url}")
            return {
                "name": "Unknown",
                "url": self.info_url,
                "error": "Too many redirects",
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error fetching {self.info_url}: {e}")
            return {"name": "Unknown", "url": self.info_url, "error": str(e)}

        try:
            tree = html.fromstring(r.content)
            castle["name"] = tree.xpath(
                '//h1[@class="xtra-post-title-headline"]/text()'
            )[0].strip()
        except IndexError:
            logging.error(f"Error parsing name for {self.info_url}")
            castle["name"] = "Unknown"
        except Exception as e:
            logging.error(f"Unexpected error parsing name for {self.info_url}: {e}")
            castle["name"] = "Unknown"
        try:
            description = tree.xpath(
                '//p[following-sibling::h2[text()="Местоположение"]]/text()'
            )
            location_text = tree.xpath(
                '//h2[text()="Местоположение"]/following-sibling::p[1]/text()'
            )
        except Exception as e:
            logging.error(
                f"Error parsing description or location for {self.info_url}: {e}"
            )
            description = []
            location_text = []

        try:
            coordinate_pattern = (
                r"(\d{2}°\d{2}'\d{2}\")\s*С\.Ш\.\s*и\s*(\d{2}°\d{2}'\d{2}\")\s*И\.Д\."
            )
            coordinates_match = re.search(coordinate_pattern, " ".join(location_text))
            if coordinates_match:
                dms_lat, dms_lon = coordinates_match.groups()
                castle["coordinates"] = {
                    "latitude": dms2dec(dms_lat),
                    "longitude": dms2dec(dms_lon),
                    "original": f"{dms_lat} С.Ш. и {dms_lon} И.Д.",
                }
            else:
                castle["coordinates"] = None
        except Exception as e:
            logging.error(f"Error parsing coordinates for {self.info_url}: {e}")
            castle["coordinates"] = None

        castle["location_text"] = (
            " ".join(location_text).strip() if location_text else None
        )
        castle["description"] = " ".join(description).strip()

        try:
            castle["literature"] = [
                lit.strip()
                for lit in tree.xpath(
                    "//p[preceding-sibling::h2[text()='Литература']]/text()"
                )
                if lit.strip()
            ]
        except Exception as e:
            logging.error(f"Error parsing literature for {self.info_url}: {e}")
            castle["literature"] = []

        castle["url"] = r.url
        return castle

    def __str__(self):
        return (
            f"Castle: {self.data['name']}, Location: {self.data['location_text']}, Coordinates:"
            f" {self.data['coordinates']}, "
            f"Description: "
            f"{self.data['description']}"
        )


class CastleManager:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.ajax_url = "https://www.bulgariancastles.com/wp-admin/admin-ajax.php"
        self.nonce = self._get_nonce()
        self.scraped_urls = self._load_scraped_urls()

    def _get_nonce(self) -> str:
        try:
            src = requests.get(self.base_url, timeout=10)
            src.raise_for_status()
            nonce = re.findall(b'"nonce":"(.+?)"', src.content)[0]
            return nonce.decode("utf8")
        except requests.RequestException as e:
            logging.error(f"Error fetching nonce: {e}")
            return ""

    @staticmethod
    def _get_links(source: bytes) -> List[str]:
        tree = html.fromstring(source)
        return tree.xpath('//a[@class="cz_grid_link"]/@href')
    def _load_scraped_urls(self) -> set:
        if not os.path.exists(SCRAPED_URLS_FILE):
            return set()
        with open(SCRAPED_URLS_FILE, 'r') as file:
            return set(line.strip() for line in file)
    def _save_scraped_urls(self, urls: List[str]):
        with open(SCRAPED_URLS_FILE, 'a') as file:
            for url in urls:
                file.write(url + '\n')
    def get_all_castle_links(self) -> List[str]:
        url = f"{self.ajax_url}?action=cz_ajax_posts&post_class=cz_grid_item&post__in%20%20%20%20=&author__in=&nonce={self.nonce}&nonce_id=cz_108374&loadmore_end=%D0%9D%D1%8F%D0%BC%D0%B0%20%D0%BF%D0%BE%D0%B2%D0%B5%D1%87%D0%B5%20%D0%BF%D1%83%D0%B1%D0%BB%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D0%B8&layout=cz_masonry%20cz_grid_c3&hover=cz_grid_1_title_sub_after%20cz_grid_1_has_excerpt&image_size=codevz_600_9999&subtitles=%5B%7B%22t%22%3A%22date%22%7D%5D&subtitle_pos=cz_grid_1_sub_after_ex&icon=fas%20fa-archway&el=20&title_lenght=&cat_tax=category&cat=50&cat_exclude=&tag_tax=category&tag_id=&tag_exclude=&post_type=post&posts_per_page=5000&order=DESC&orderby=modified&tilt_data=&svg_sizes[]=600&svg_sizes[]=600&img_fx=&custom_size=&excerpt_rm=true&title_tag=h3&s=&category_name=severozapadna-b-ya&cache_results=true&update_post_term_cache=true&lazy_load_term_meta=true&update_post_meta_cache=true&comments_per_page=50"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            all_links = self._get_links(response.content)
            new_links = [link for link in all_links if link not in self.scraped_urls]
            print(f"Found {len(new_links)} new castles.")
            return new_links
        except requests.RequestException as e:
            logging.error(f"Error fetching castle links: {e}")
            return []

    def get_all_castles(self) -> List[Castle]:
        links = self.get_all_castle_links()
        castles = []
        for i, link in enumerate(links, 1):
            castle = Castle(link)
            castles.append(castle)
            print(f"Processed castle {i}/{len(links)}: {castle.data['name']}")
        return castles


def main():
    manager = CastleManager(
        "https://www.bulgariancastles.com/category/obekti-v-balgariya/"
    )
    castles = manager.get_all_castles()

    print(f"Total castles found: {len(castles)}")
    for castle in castles:
        print(castle)
        # Here you can process or store the castle information as needed


if __name__ == "__main__":
    main()
