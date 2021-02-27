"""Visualizer of the data of amount of index ETFs & J-REITs purchased by Bank of Japan

    * This script read `data/processed/boj_etf_reit_amount.csv`
      and output the figure to `reports/figures`

"""

import logging
from pathlib import Path

import matplotlib.dates as mdates  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore

OUTPUT_FIG_FILENAME = "total_amount_purchased_etf_reit.png"


class TimeSeriesVisualizer:
    def __init__(self, *, logger=None):
        self.logger = logging.getLogger(__name__)
        self.df = pd.DataFrame()
        self.fig, self.ax = plt.subplots(figsize=(12, 4))

    def load_csv(self, target: Path):
        self.df = pd.read_csv(target)

    def _format_df_for_visualization(self):
        date_col = pd.to_datetime(self.df["Date"])
        cumsum_cols = self.df.drop("Date", axis=1).fillna(0.0).cumsum()
        _df = pd.concat([date_col, cumsum_cols], axis=1).assign(
            Total=lambda df: df["IndexETF"] + df["SupportiveETF"] + df["J-REIT"]
        )

        self.df = _df

    def _make_fig(self):
        self.ax.step(self.df["Date"], self.df["Total"], where="post")

        day_loc = mdates.MonthLocator(bymonth=range(1, 13), interval=12, tz=None)
        date_formatter = mdates.DateFormatter("%Y-%m-%d")

        self.ax.xaxis.set_major_locator(day_loc)
        self.ax.xaxis.set_major_formatter(date_formatter)

        labels = self.ax.get_xticklabels()
        plt.setp(labels, rotation=45, fontsize=10)

        title = "Total Amount of Index ETFs & J-REITs Purchased by Bank of Japan (100 million yen)"
        self.ax.set_title(title)
        self.ax.grid()
        self.fig.subplots_adjust(bottom=0.25)

    def save_fig(self, save_loc: Path):
        self._format_df_for_visualization()
        self._make_fig()
        self.fig.savefig(save_loc)


def main():
    logger = logging.getLogger(__name__)

    src_dir = Path(__file__).resolve().parent
    project_root = src_dir.parent
    fig_data_path = project_root.joinpath("reports/figures").joinpath(
        OUTPUT_FIG_FILENAME
    )
    processed_data_path = project_root.joinpath(
        "data/processed/boj_etf_reit_amount.csv"
    )

    tsv = TimeSeriesVisualizer(logger=logger)
    tsv.load_csv(processed_data_path)
    tsv.save_fig(fig_data_path)


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s- %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    main()
