"""Aggregator of CSV files

    * This script concatenate CSV files in `data/interim` and export the aggregated dataframe to `data/processed`

"""
import logging
from pathlib import Path

import pandas as pd  # type: ignore

OUTPUT_FILENAME = "boj_etf_reit_amount.csv"


class Aggregator:
    """Aggregator of CSV files

    Attributes:
        logger (:obj: Logger): Logger

    """

    def __init__(self, *, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def aggregate_csv(self, csv_dir: Path) -> pd.DataFrame:
        "Concatenate the CSV files in `csv_dir`"
        self.logger.info(f"Start to aggregate CSV files in {csv_dir}")
        dfs = [pd.read_csv(p, parse_dates=["Date"]) for p in csv_dir.glob("*.csv")]
        df = pd.concat(dfs).sort_values("Date")
        return df


def main():
    logger = logging.getLogger(__name__)

    src_dir = Path(__file__).resolve().parent
    project_root = src_dir.parent
    interim_data_path = project_root.joinpath("data/interim")
    processed_data_path = project_root.joinpath("data/processed")

    agg = Aggregator(logger=logger)
    df_agg = agg.aggregate_csv(interim_data_path)
    target = processed_data_path.joinpath(OUTPUT_FILENAME)
    df_agg.to_csv(target, index=False)
    logger.info(f"Saved: {target}")


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s- %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    main()
