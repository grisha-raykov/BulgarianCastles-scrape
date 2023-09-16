import logging
import requests
from lxml import html
import re
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from castle import CastleData
from models import Castle, ScrapedURL
from database import get_session
from utils import setup_logging

logger = setup_logging()


class CastleManager:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.ajax_url = "https://www.bulgariancastles.com/wp-admin/admin-ajax.php"
        self.nonce = self._get_nonce()

    def _get_nonce(self) -> str:
        try:
            src = requests.get(self.base_url, timeout=10)
            src.raise_for_status()
            nonce = re.findall(b'"nonce":"(.+?)"', src.content)[0]
            return nonce.decode("utf8")
        except requests.RequestException as e:
            logging.error(f"Error fetching nonce: {e}")
            return ""

    def _get_links(self, source: bytes) -> List[str]:
        tree = html.fromstring(source)
        return tree.xpath('//a[@class="cz_grid_link"]/@href')

    def _load_scraped_urls(self) -> set:
        session = get_session()
        scraped_urls = session.query(ScrapedURL.url).all()
        session.close()
        return {url[0] for url in scraped_urls}

    def _save_scraped_url(self, url: str):
        session = get_session()
        new_scraped_url = ScrapedURL(url=url)
        session.add(new_scraped_url)
        session.commit()
        session.close()

    def _save_castle(self, castle_data: dict):
        session = get_session()
        new_castle = Castle(
            name=castle_data["name"],
            url=castle_data["url"],
            description=castle_data.get("description", ""),
            location_text=castle_data.get("location_text", ""),
            latitude=(
                castle_data["coordinates"]["latitude"]
                if castle_data.get("coordinates")
                else None
            ),
            longitude=(
                castle_data["coordinates"]["longitude"]
                if castle_data.get("coordinates")
                else None
            ),
            coordinates_original=(
                castle_data["coordinates"]["original"]
                if castle_data.get("coordinates")
                else None
            ),
            literature=castle_data.get("literature", []),
            has_error=castle_data["has_error"],
            error_message=castle_data["error_message"],
        )
        session.add(new_castle)
        session.commit()
        session.close()

    def get_all_castle_links(self) -> List[str]:
        url = f"{self.ajax_url}?action=cz_ajax_posts&post_class=cz_grid_item&post__in%20%20%20%20=&author__in=&nonce={self.nonce}&nonce_id=cz_108374&loadmore_end=%D0%9D%D1%8F%D0%BC%D0%B0%20%D0%BF%D0%BE%D0%B2%D0%B5%D1%87%D0%B5%20%D0%BF%D1%83%D0%B1%D0%BB%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D0%B8&layout=cz_masonry%20cz_grid_c3&hover=cz_grid_1_title_sub_after%20cz_grid_1_has_excerpt&image_size=codevz_600_9999&subtitles=%5B%7B%22t%22%3A%22date%22%7D%5D&subtitle_pos=cz_grid_1_sub_after_ex&icon=fas%20fa-archway&el=20&title_lenght=&cat_tax=category&cat=50&cat_exclude=&tag_tax=category&tag_id=&tag_exclude=&post_type=post&posts_per_page=5000&order=DESC&orderby=modified&tilt_data=&svg_sizes[]=600&svg_sizes[]=600&img_fx=&custom_size=&excerpt_rm=true&title_tag=h3&s=&category_name=severozapadna-b-ya&cache_results=true&update_post_term_cache=true&lazy_load_term_meta=true&update_post_meta_cache=true&comments_per_page=50"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            all_links = self._get_links(response.content)
            scraped_urls = self._load_scraped_urls()
            new_links = [link for link in all_links if link not in scraped_urls]
            print(f"Found {len(new_links)} new castles.")
            return new_links
        except requests.RequestException as e:
            logging.error(f"Error fetching castle links: {e}")
            return []

    def get_all_castles(self) -> List[CastleData]:
        links = self.get_all_castle_links()
        castles = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(CastleData, url): url for url in links}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    castle = future.result()
                    castles.append(castle)
                    self._save_castle(castle.data)
                    self._save_scraped_url(url)
                    print(
                        f"Processed and saved castle: {castle.data['name']}, Error: {castle.data['has_error']}"
                    )
                except Exception as exc:
                    logger.error(f"Castle at {url} generated an exception: {exc}")
                    self._save_castle(
                        {
                            "name": "Unknown",
                            "url": url,
                            "has_error": True,
                            "error_message": str(exc),
                        }
                    )
        return castles
