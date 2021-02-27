import os
import sys

sys.path.append(
    os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../src/")
)
import re
from pathlib import Path

import pytest

from aggregator import Aggregator
from converter import ConversionFormatHandler, Converter
from downloader import Downloader


class TestAggregator:
    @classmethod
    def setup_class(self):
        url = "https://www3.boj.or.jp/market/jp/menu_etf.htm"
        shared_datadir = Path(__file__).parent / "data"
        downloader = Downloader(shared_datadir.joinpath("raw"))
        downloader.download(url)
        downloader.extract()

        # Holds files only for the test
        for f in shared_datadir.joinpath("raw").iterdir():
            if not (
                (".gitkeep" in f.name)
                or re.search(r"(2010|2017|2020)\.(xls|xlsx)", f.name)
            ):
                f.unlink(missing_ok=True)

        # Convert
        raw_files = shared_datadir.joinpath("raw").glob("*")
        handler = ConversionFormatHandler()
        for raw_file in raw_files:
            if converter := handler.choose_converter(raw_file):
                df = converter.convert(raw_file)
                save_location = shared_datadir.joinpath(
                    "interim", raw_file.with_suffix(".csv").name
                )
                # Save
                df.to_csv(save_location, index=False)

    @classmethod
    def teardown_class(self):
        shared_datadir = Path(__file__).parent / "data"
        for f in shared_datadir.joinpath("raw").iterdir():
            if ".gitkeep" not in f.name:
                f.unlink()

        for f in shared_datadir.joinpath("interim").iterdir():
            if ".gitkeep" not in f.name:
                f.unlink()

    def test_aggregate(self, shared_datadir):
        aggregator = Aggregator()
        df = aggregator.aggregate_csv(shared_datadir.joinpath("interim"))
        assert df.shape[0] == 17 + 365 + 366
        assert df.shape[1] == 5
