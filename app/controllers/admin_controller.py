"""Admin controller for dataset build and model training workflows."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config.settings import DATASET_PATH
from app.models.phone_price_model import PhonePriceModel
from app.utils.data_utils import dataset_summary


def train_new_model(
    records: int = 1000,
    distribution: str = "uniform",
    append_only: bool = False,
    dataset_path: Path = DATASET_PATH,
) -> dict:
    model = PhonePriceModel()
    return model.build_dataset_and_train(
        dataset_path=dataset_path,
        synthetic_records=records,
        distribution_profile=distribution,
        append_only=append_only,
    )


def get_dataset_summary(dataset_path: Path = DATASET_PATH) -> dict:
    df = pd.read_csv(dataset_path)
    return dataset_summary(df)
