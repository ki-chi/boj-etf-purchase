"""Downloader for the amount of ETF purchase by Bank of Japan

    * This script downloads Excel files from BoJ website and updates the files in `date/raw`.

"""
import logging
import re
from pathlib import Path
from urllib.parse import urljoin
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore


class Downloader:
    """The class for downloading the Excel files on BoJ website

    Attributes:
        save_loc (:obj:`Path`): The path for saving the downloaded files (e.g. `data/raw`)
        logger (:obj: `Logger`): Logger.

    """

    def __init__(self, save_location: Path, *, logger=None):
        self.save_loc = save_location
        self.logger = logger or logging.getLogger(__name__)

    def _make_soup(self, url: str):
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        return soup

    def _filter_links(self, url: str, links: list[Tag]):
        urls_contains_xls = filter(
            lambda s: re.search(".(zip|xls|xlsx)$", s),
            map(lambda l: l.get("href"), links),
        )
        abs_urls = [urljoin(url, rel_path) for rel_path in urls_contains_xls]
        return abs_urls

    def _extract_zip(self, target_path):
        with ZipFile(target_path) as existing_zip:
            existing_zip.extractall(self.save_loc)

    def download(self, url) -> None:
        """Download files from the BoJ website

        The method for downloading the files about the amount of purchased ETF.
        It updates the all xlsx files in `self.save_loc` no matter whether the file is updated.

        Returns:
            None

        """
        soup = self._make_soup(url)
        links = soup.find_all("a")
        target_urls = self._filter_links(url, links)
        for target_url in target_urls:
            filename = target_url.split("/")[-1]
            res = requests.get(target_url)
            with open(self.save_loc.joinpath(filename), "wb") as f:
                f.write(res.content)
                self.logger.info(f"Downloaded: {target_url}")

        self.logger.info(f"Downloaded {len(target_urls)} files to {self.save_loc}")

    def extract(self):
        """Extract zip files in `self.save_loc`

        Returns:
            None
        """
        for f in self.save_loc.iterdir():
            if f.suffix == ".zip":
                self._extract_zip(f)
                self.logger.info(f"Extracted: {f.name} in {self.save_loc}")


def main():
    logger = logging.getLogger(__name__)

    src_dir = Path(__file__).resolve().parent
    project_root = src_dir.parent
    raw_data_path = project_root.joinpath("data/raw")

    # URL of BoJ website providing the ETF purchasing information
    url = "https://www3.boj.or.jp/market/jp/menu_etf.htm"

    downloader = Downloader(raw_data_path, logger=logger)
    downloader.download(url)
    downloader.extract()


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s- %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    main()
