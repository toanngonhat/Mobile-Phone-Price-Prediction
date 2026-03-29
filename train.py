"""Train Random Forest model from local CLI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.models.phone_price_model import PhonePriceModel


DATASET_PATH = Path("app/data/sample_phone_data.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Random Forest model")
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH, help="Output merged CSV path")
    parser.add_argument("--records", type=int, default=1000, help="Synthetic iPhone record count")
    parser.add_argument(
        "--distribution",
        type=str,
        choices=["uniform", "latest_heavy", "promax_heavy"],
        default="uniform",
        help="Sampling profile for synthetic iPhone variants",
    )
    parser.add_argument(
        "--append-only",
        action="store_true",
        help="Append only synthetic rows to existing dataset file (no Kaggle reload)",
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Skip data generation and train from existing dataset only",
    )
    args = parser.parse_args()

    model = PhonePriceModel()
    if not args.skip_generate:
        model.build_dataset(
            dataset_path=args.dataset,
            synthetic_records=args.records,
            append_only=args.append_only,
            distribution_profile=args.distribution,
        )

    metrics = model.train_from_dataset(dataset_path=args.dataset)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
