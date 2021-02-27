import os
import sys

sys.path.append(
    os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../src/")
)

from pathlib import Path

from downloader import Downloader


class TestDownloader:
    @classmethod
    def teardown_class(self):
        shared_datadir = Path(__file__).parent / "data"
        for f in shared_datadir.joinpath("raw").iterdir():
            if ".gitkeep" not in f.name:
                f.unlink(missing_ok=True)

    def test_download(self, shared_datadir):
        url = "https://www3.boj.or.jp/market/jp/menu_etf.htm"
        downloader = Downloader(shared_datadir.joinpath("raw"))
        downloader.download(url)
        downloader.extract()
        suffix_set = set([f.suffix for f in shared_datadir.joinpath("raw").iterdir()])
        assert ".xls" in suffix_set
        assert ".xlsx" in suffix_set
        assert ".zip" in suffix_set
