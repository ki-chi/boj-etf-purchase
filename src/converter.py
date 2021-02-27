"""Converter of xls or xlsx files to intermediate CSV files

    * This script converts the Excel files in `data/raw` to the intermediate CSV files
    * It currently skips the monthly data file of outstanding balance of ETF lending

Todo:
    * Refactor `ConversionFormatHandler`

"""
import datetime
import logging
import re
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Optional

import pandas as pd  # type: ignore


@dataclass(frozen=True)
class FormatParam:
    "Parameters for parsing xlsx file"
    num_sheet: int
    col_names: dict[int, list[str]]  # {sheet_idx: colnames, }
    skiprows: dict[int, int]  # {sheet_idx: skiprows, }
    usecols: dict[int, list[int]]  # {sheet_idx: usecols, }

    def __post_init__(self):
        "parameter validation"
        if len(self.col_names) != self.num_sheet:
            raise ValueError("Unmatch the length of sheet_names")
        elif len(self.skiprows) != self.num_sheet:
            raise ValueError("Unmatch the length of skiprows")
        elif len(self.usecols) != self.num_sheet:
            raise ValueError("Unmatch the length of usecols")
        else:
            pass


class Converter:
    """Converter of xls or xlsx files

    This class reads and converts the xls or xlsx files describing BoJ operating data.
    The difference of the file formats are absorbed by `format_param`.

    Attributes:
        fortmat_param (:obj: FormatParam): Parameters to read xlsx files
        logger (:obj: Logger): Logger

    """

    def __init__(self, format_param: FormatParam, *, logger=None):
        self.format_param = format_param
        self.logger = logger or logging.getLogger(__name__)

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        "Modify the column's format, and remove invalid dates"
        proper_date_flags = df["Date"].apply(lambda x: isinstance(x, datetime.datetime))

        _df = df[proper_date_flags].assign(Date=lambda df: pd.to_datetime(df["Date"]))

        return _df

    def convert(self, target_file_path: Path) -> pd.DataFrame:
        """Convert the file on `target_file_path` to pandas.DataFrame

        Args:
            target_file_path (:obj: Path):  The file path of xls or xlsx file

        Returns:
            pd.DataFrame: the dataframe extracted from xls or xlsx file
        """
        if not target_file_path.exists():
            raise FileNotFoundError(f"{target_file_path}")

        dfs = []
        for i in range(self.format_param.num_sheet):
            df = pd.read_excel(
                target_file_path,
                sheet_name=i,
                names=self.format_param.col_names[i],
                usecols=self.format_param.usecols[i],
                skiprows=self.format_param.skiprows[i],
            ).pipe(self._clean)
            dfs.append(df)

        if len(dfs) == 1:
            return dfs[0]
        else:
            df_merged = reduce(lambda l, r: pd.merge(l, r, on="Date", how="outer"), dfs)
            return df_merged


class ConversionFormatHandler:
    """Handle the format to parse the xlsx file

    Attributes:
        logger (:obj: Logger): Logger.

    """

    def __init__(self, *, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def choose_converter(self, target_path) -> Optional[Converter]:
        """Choose a converter which has a proper format params.

        Args:
            target_path (:obj: Path): File path to open

        Returns:
            Optional[Converter]: the proper converter to convert `target_path` (if it exists).

        """
        filenames_before_purchase_supportive_etf = [
            "2010.xls",
            "2011.xls",
            "2012.xls",
            "2013.xls",
            "2014.xls",
            "2015.xls",
            "2016 (Purchases until March).xls",
        ]
        filenames_with_purchase_supportive_etf = [
            "2016 (Purchases from April).xls",
            "2017.xls",
            "2018.xls",
            "2019.xls",
        ]
        filenames_with_lending_etf = ["2020.xlsx"]

        if target_path.name in filenames_before_purchase_supportive_etf:
            format_param = FormatParam(
                1,
                {0: ["Date", "IndexETF", "J-REIT"]},
                {0: 7},
                {0: [1, 2, 3]},
            )
            return Converter(format_param, logger=self.logger)

        elif target_path.name in filenames_with_purchase_supportive_etf:
            format_param = FormatParam(
                1,
                {0: ["Date", "IndexETF", "SupportiveETF", "J-REIT"]},
                {0: 9},
                {0: [1, 2, 3, 4]},
            )
            return Converter(format_param, logger=self.logger)

        elif target_path.name in filenames_with_lending_etf:
            format_param = FormatParam(
                2,
                {
                    0: ["Date", "IndexETF", "SupportiveETF", "J-REIT"],
                    1: ["Date", "LendingETF"],
                },
                {0: 9, 1: 6},
                {0: [1, 2, 3, 4], 1: [1, 2]},
            )
            return Converter(format_param, logger=self.logger)

        elif re.search(r"etfreit\d{2}.xlsx$", target_path.name):
            # Latest format
            format_param = FormatParam(
                2,
                {
                    0: ["Date", "IndexETF", "SupportiveETF", "J-REIT"],
                    1: ["Date", "LendingETF"],
                },
                {0: 9, 1: 6},
                {0: [1, 2, 3, 4], 1: [1, 2]},
            )
            return Converter(format_param, logger=self.logger)

        else:
            return None


def main():
    logger = logging.getLogger(__name__)

    src_dir = Path(__file__).resolve().parent
    project_root = src_dir.parent
    raw_data_path = project_root.joinpath("data/raw")
    interim_data_path = project_root.joinpath("data/interim")

    raw_files: list[Path] = [
        p for p in raw_data_path.glob("*") if re.search("\\.(xls|xlsx)$", str(p))
    ]

    handler = ConversionFormatHandler(logger=logger)

    for raw_file in raw_files:
        if converter := handler.choose_converter(raw_file):
            logger.info(f"Open: {raw_file}")
            df = converter.convert(raw_file)
            logger.info(f"Converted: {raw_file}")
            save_location = interim_data_path.joinpath(
                raw_file.with_suffix(".csv").name
            )
            df.to_csv(save_location, index=False)
            logger.info(f"Saved: {save_location}")
        else:
            logger.info(f"Skipped: {raw_file}")


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s- %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    main()
