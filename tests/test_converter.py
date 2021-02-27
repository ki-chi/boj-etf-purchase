import os
import sys

sys.path.append(
    os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../src/")
)

from pathlib import Path

import pytest

from converter import ConversionFormatHandler, Converter, FormatParam
from downloader import Downloader


class TestConverter:
    @classmethod
    def setup_class(self):
        url = "https://www3.boj.or.jp/market/jp/menu_etf.htm"
        shared_datadir = Path(__file__).parent / "data"
        downloader = Downloader(shared_datadir.joinpath("raw"))
        downloader.download(url)
        downloader.extract()

    @classmethod
    def teardown_class(self):
        shared_datadir = Path(__file__).parent / "data"
        for f in shared_datadir.joinpath("raw").iterdir():
            if ".gitkeep" not in f.name:
                f.unlink()

    def test_convert_before_purchase_supportive_etf(self, shared_datadir):
        format_param = FormatParam(
            1,
            {0: ["Date", "IndexETF", "J-REIT"]},
            {0: 7},
            {0: [1, 2, 3]},
        )
        converter = Converter(format_param)
        df = converter.convert(shared_datadir.joinpath("raw/2010.xls"))
        assert list(df.columns) == ["Date", "IndexETF", "J-REIT"]
        assert df.shape[0] == 17
        assert df.shape[1] == 3

    def test_convert_with_purchase_supportive_etf(self, shared_datadir):
        format_param = FormatParam(
            1,
            {0: ["Date", "IndexETF", "SupportiveETF", "J-REIT"]},
            {0: 9},
            {0: [1, 2, 3, 4]},
        )
        converter = Converter(format_param)
        df = converter.convert(shared_datadir.joinpath("raw/2017.xls"))
        assert list(df.columns) == ["Date", "IndexETF", "SupportiveETF", "J-REIT"]
        assert df.shape[0] == 365
        assert df.shape[1] == 4

    def test_convert_with_lending_etf(self, shared_datadir):
        format_param = FormatParam(
            2,
            {
                0: ["Date", "IndexETF", "SupportiveETF", "J-REIT"],
                1: ["Date", "LendingETF"],
            },
            {0: 9, 1: 6},
            {0: [1, 2, 3, 4], 1: [1, 2]},
        )
        converter = Converter(format_param)
        df = converter.convert(shared_datadir.joinpath("raw/2020.xlsx"))
        assert list(df.columns) == [
            "Date",
            "IndexETF",
            "SupportiveETF",
            "J-REIT",
            "LendingETF",
        ]
        assert df.shape[0] == 366
        assert df.shape[1] == 5

    def test_conversion_format_handler(self, shared_datadir):
        handler = ConversionFormatHandler()
        actual01 = handler.choose_converter(shared_datadir.joinpath("raw/2010.xls"))
        expected01 = Converter(
            FormatParam(
                1,
                {0: ["Date", "IndexETF", "J-REIT"]},
                {0: 7},
                {0: [1, 2, 3]},
            )
        )

        actual02 = handler.choose_converter(shared_datadir.joinpath("raw/2017.xls"))
        expected02 = Converter(
            FormatParam(
                1,
                {0: ["Date", "IndexETF", "SupportiveETF", "J-REIT"]},
                {0: 9},
                {0: [1, 2, 3, 4]},
            )
        )

        actual03 = handler.choose_converter(shared_datadir.joinpath("raw/2020.xlsx"))
        expected03 = Converter(
            FormatParam(
                2,
                {
                    0: ["Date", "IndexETF", "SupportiveETF", "J-REIT"],
                    1: ["Date", "LendingETF"],
                },
                {0: 9, 1: 6},
                {0: [1, 2, 3, 4], 1: [1, 2]},
            )
        )

        assert actual01.format_param == expected01.format_param
        assert actual02.format_param == expected02.format_param
        assert actual03.format_param == expected03.format_param
