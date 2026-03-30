"""Core Random Forest model with versioning and dataset build pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json

import joblib
import kagglehub
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.config.settings import (
	APP_SETTINGS_PATH,
	DATASET_PATH,
	FEATURE_COLUMNS,
	KAGGLE_DATASET_REF,
	KAGGLE_FILE_NAME,
	MODEL_VERSIONS_DIR,
	RAW_SCHEMA,
)
from app.utils.data_utils import validate_schema


@dataclass
class TrainConfig:
	synthetic_records: int = 1000
	distribution_profile: str = "uniform"
	append_only: bool = False
	random_seed: int = 42


class PhonePriceModel:
	"""Main class handling data preparation, training, loading, and inference."""

	def __init__(self, version: int | None = None):
		self.model = None
		self.loaded_version = None
		self._ensure_dirs()
		self._load(version)

	def _ensure_dirs(self) -> None:
		MODEL_VERSIONS_DIR.mkdir(parents=True, exist_ok=True)

	def _read_app_settings(self) -> dict:
		if not APP_SETTINGS_PATH.exists():
			return {"active_model_version": None, "last_training_time": None}
		with open(APP_SETTINGS_PATH, "r", encoding="utf-8") as f:
			return json.load(f)

	def _write_app_settings(self, active_version: int | None) -> None:
		payload = {
			"active_model_version": active_version,
			"last_training_time": datetime.now(timezone.utc).isoformat(),
		}
		with open(APP_SETTINGS_PATH, "w", encoding="utf-8") as f:
			json.dump(payload, f, indent=2)

	def _available_versions(self) -> list[int]:
		versions: list[int] = []
		for p in MODEL_VERSIONS_DIR.iterdir():
			if p.is_dir() and p.name.startswith("v"):
				try:
					versions.append(int(p.name[1:]))
				except ValueError:
					continue
		return sorted(versions)

	def _next_version(self) -> int:
		versions = self._available_versions()
		return (versions[-1] + 1) if versions else 1

	def _load(self, version: int | None = None) -> None:
		if version is None:
			settings = self._read_app_settings()
			version = settings.get("active_model_version")
			if version is None:
				versions = self._available_versions()
				version = versions[-1] if versions else None

		if version is None:
			return

		model_path = MODEL_VERSIONS_DIR / f"v{version}" / "model.pkl"
		if model_path.exists():
			self.model = joblib.load(model_path)
			self.loaded_version = version

	def download_kaggle_dataset(self) -> pd.DataFrame:
		dataset_dir = Path(kagglehub.dataset_download(KAGGLE_DATASET_REF))
		source_file = dataset_dir / KAGGLE_FILE_NAME
		if not source_file.exists():
			raise FileNotFoundError(f"Cannot find {KAGGLE_FILE_NAME} in {dataset_dir}")

		df = pd.read_csv(source_file)
		validate_schema(df)
		return df[RAW_SCHEMA].copy()

	def _build_iphone_variant_templates(self) -> list[dict]:
		return [
			{"model": "iPhone 11", "ram": 4, "storage_options": [64, 128, 256], "battery": 3110, "screen_in": 6.1, "rear_camera": 12, "front_camera": 12, "weight": 194, "new_price": 699, "year": 2019},
			{"model": "iPhone 11 Pro", "ram": 4, "storage_options": [64, 256, 512], "battery": 3046, "screen_in": 5.8, "rear_camera": 12, "front_camera": 12, "weight": 188, "new_price": 999, "year": 2019},
			{"model": "iPhone 11 Pro Max", "ram": 4, "storage_options": [64, 256, 512], "battery": 3969, "screen_in": 6.5, "rear_camera": 12, "front_camera": 12, "weight": 226, "new_price": 1099, "year": 2019},
			{"model": "iPhone 12 Mini", "ram": 4, "storage_options": [64, 128, 256], "battery": 2227, "screen_in": 5.4, "rear_camera": 12, "front_camera": 12, "weight": 135, "new_price": 699, "year": 2020},
			{"model": "iPhone 12", "ram": 4, "storage_options": [64, 128, 256], "battery": 2815, "screen_in": 6.1, "rear_camera": 12, "front_camera": 12, "weight": 164, "new_price": 799, "year": 2020},
			{"model": "iPhone 12 Pro", "ram": 6, "storage_options": [128, 256, 512], "battery": 2815, "screen_in": 6.1, "rear_camera": 12, "front_camera": 12, "weight": 189, "new_price": 999, "year": 2020},
			{"model": "iPhone 12 Pro Max", "ram": 6, "storage_options": [128, 256, 512], "battery": 3687, "screen_in": 6.7, "rear_camera": 12, "front_camera": 12, "weight": 228, "new_price": 1099, "year": 2020},
			{"model": "iPhone 13 Mini", "ram": 4, "storage_options": [128, 256, 512], "battery": 2406, "screen_in": 5.4, "rear_camera": 12, "front_camera": 12, "weight": 141, "new_price": 699, "year": 2021},
			{"model": "iPhone 13", "ram": 4, "storage_options": [128, 256, 512], "battery": 3240, "screen_in": 6.1, "rear_camera": 12, "front_camera": 12, "weight": 174, "new_price": 799, "year": 2021},
			{"model": "iPhone 13 Pro", "ram": 6, "storage_options": [128, 256, 512, 1024], "battery": 3095, "screen_in": 6.1, "rear_camera": 12, "front_camera": 12, "weight": 204, "new_price": 999, "year": 2021},
			{"model": "iPhone 13 Pro Max", "ram": 6, "storage_options": [128, 256, 512, 1024], "battery": 4352, "screen_in": 6.7, "rear_camera": 12, "front_camera": 12, "weight": 240, "new_price": 1099, "year": 2021},
			{"model": "iPhone 14", "ram": 6, "storage_options": [128, 256, 512], "battery": 3279, "screen_in": 6.1, "rear_camera": 12, "front_camera": 12, "weight": 172, "new_price": 799, "year": 2022},
			{"model": "iPhone 14 Plus", "ram": 6, "storage_options": [128, 256, 512], "battery": 4325, "screen_in": 6.7, "rear_camera": 12, "front_camera": 12, "weight": 203, "new_price": 899, "year": 2022},
			{"model": "iPhone 14 Pro", "ram": 6, "storage_options": [128, 256, 512, 1024], "battery": 3200, "screen_in": 6.1, "rear_camera": 48, "front_camera": 12, "weight": 206, "new_price": 999, "year": 2022},
			{"model": "iPhone 14 Pro Max", "ram": 6, "storage_options": [128, 256, 512, 1024], "battery": 4323, "screen_in": 6.7, "rear_camera": 48, "front_camera": 12, "weight": 240, "new_price": 1099, "year": 2022},
			{"model": "iPhone 15", "ram": 6, "storage_options": [128, 256, 512], "battery": 3349, "screen_in": 6.1, "rear_camera": 48, "front_camera": 12, "weight": 171, "new_price": 799, "year": 2023},
			{"model": "iPhone 15 Plus", "ram": 6, "storage_options": [128, 256, 512], "battery": 4383, "screen_in": 6.7, "rear_camera": 48, "front_camera": 12, "weight": 201, "new_price": 899, "year": 2023},
			{"model": "iPhone 15 Pro", "ram": 8, "storage_options": [128, 256, 512, 1024], "battery": 3274, "screen_in": 6.1, "rear_camera": 48, "front_camera": 12, "weight": 187, "new_price": 999, "year": 2023},
			{"model": "iPhone 15 Pro Max", "ram": 8, "storage_options": [256, 512, 1024], "battery": 4422, "screen_in": 6.7, "rear_camera": 48, "front_camera": 12, "weight": 221, "new_price": 1199, "year": 2023},
		]

	def _variant_probabilities(self, variants: list[dict], profile: str) -> np.ndarray:
		if profile == "uniform":
			weights = np.ones(len(variants), dtype=float)
		elif profile == "latest_heavy":
			weights = np.array([max(1, v["year"] - 2018) for v in variants], dtype=float)
		elif profile == "promax_heavy":
			weights = np.array([2.5 if "Pro Max" in v["model"] else 1.0 for v in variants], dtype=float)
		else:
			raise ValueError(f"Unsupported distribution profile: {profile}")
		return weights / weights.sum()

	def generate_synthetic_iphones(
		self,
		num_records: int,
		random_seed: int = 42,
		distribution_profile: str = "uniform",
	) -> pd.DataFrame:
		rng = np.random.default_rng(random_seed)
		variants = self._build_iphone_variant_templates()
		probabilities = self._variant_probabilities(variants, distribution_profile)
		rows: list[dict] = []

		for _ in range(num_records):
			variant = variants[int(rng.choice(len(variants), p=probabilities))]
			storage = int(rng.choice(variant["storage_options"]))

			battery = int(np.clip(variant["battery"] + rng.normal(0, 110), 1800, 5500))
			weight = int(np.clip(variant["weight"] + rng.normal(0, 6), 130, 260))
			days_used = int(rng.integers(40, 900))
			new_price = variant["new_price"] + (storage - min(variant["storage_options"])) * 0.4
			used_ratio = float(np.clip(rng.normal(0.72, 0.08), 0.5, 0.92))
			battery_effect = (battery - variant["battery"]) * 0.02
			used_price = float(np.clip(new_price * used_ratio + battery_effect, 320, 2200))

			rows.append(
				{
					"device_brand": "Apple",
					"os": "iOS",
					"screen_size": round(variant["screen_in"] * 2.54 + rng.normal(0, 0.15), 2),
					"rear_camera_mp": int(variant["rear_camera"]),
					"front_camera_mp": int(variant["front_camera"]),
					"internal_memory": storage,
					"ram": int(variant["ram"]),
					"battery": battery,
					"weight": weight,
					"release_year": int(variant["year"]),
					"days_used": days_used,
					"normalized_used_price": float(np.log(used_price)),
					"normalized_new_price": float(np.log(new_price)),
				}
			)

		return pd.DataFrame(rows, columns=RAW_SCHEMA)

	def build_dataset(
		self,
		dataset_path: Path = DATASET_PATH,
		synthetic_records: int = 1000,
		append_only: bool = False,
		distribution_profile: str = "uniform",
	) -> pd.DataFrame:
		if append_only:
			if not dataset_path.exists():
				raise FileNotFoundError(f"Append-only mode requires existing dataset: {dataset_path}")
			base_df = pd.read_csv(dataset_path)
			validate_schema(base_df)
			base_df = base_df[RAW_SCHEMA].copy()
		else:
			base_df = self.download_kaggle_dataset()

		synth_df = self.generate_synthetic_iphones(
			num_records=synthetic_records,
			distribution_profile=distribution_profile,
		)
		merged_df = pd.concat([base_df, synth_df], ignore_index=True)

		dataset_path.parent.mkdir(parents=True, exist_ok=True)
		merged_df.to_csv(dataset_path, index=False)
		return merged_df

	def _prepare_training_matrix(self, raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
		X = pd.DataFrame(
			{
				"brand": raw_df["device_brand"].astype(str),
				"ram": raw_df["ram"].astype(float),
				"storage": raw_df["internal_memory"].astype(float),
				"battery_capacity": raw_df["battery"].astype(float),
				"screen_size": raw_df["screen_size"].astype(float) / 2.54,
				"camera_mp": raw_df["rear_camera_mp"].astype(float),
				"release_year": raw_df["release_year"].astype(float),
				"days_used": raw_df["days_used"].astype(float),
			}
		)
		y = np.exp(raw_df["normalized_used_price"].astype(float))
		return X, y

	def _new_pipeline(self) -> Pipeline:
		preprocessor = ColumnTransformer(
			transformers=[
				(
					"cat",
					Pipeline(
						steps=[
							("imputer", SimpleImputer(strategy="most_frequent")),
							("encoder", OneHotEncoder(handle_unknown="ignore")),
						]
					),
					["brand"],
				),
				(
					"num",
					Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))]),
					["ram", "storage", "battery_capacity", "screen_size", "camera_mp", "release_year", "days_used"],
				),
			]
		)
		return Pipeline(
			steps=[
				("preprocessor", preprocessor),
				(
					"regressor",
					RandomForestRegressor(
						n_estimators=400,
						max_depth=18,
						random_state=42,
						n_jobs=-1,
					),
				),
			]
		)

	def train_from_dataset(self, dataset_path: Path = DATASET_PATH) -> dict:
		raw_df = pd.read_csv(dataset_path)
		validate_schema(raw_df)

		X, y = self._prepare_training_matrix(raw_df)
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

		model = self._new_pipeline()
		model.fit(X_train, y_train)
		preds = model.predict(X_test)

		new_version = self._next_version()
		version_dir = MODEL_VERSIONS_DIR / f"v{new_version}"
		version_dir.mkdir(parents=True, exist_ok=True)

		model_path = version_dir / "model.pkl"
		metrics = {
			"version": new_version,
			"records": int(len(raw_df)),
			"kaggle_dataset": KAGGLE_DATASET_REF,
			"features": FEATURE_COLUMNS,
			"excluded_features": ["4g", "5g"],
			"target": "exp(normalized_used_price)",
			"mae": float(mean_absolute_error(y_test, preds)),
			"rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
			"r2": float(r2_score(y_test, preds)),
			"trained_at": datetime.now(timezone.utc).isoformat(),
		}

		joblib.dump(model, model_path)
		with open(version_dir / "metadata.json", "w", encoding="utf-8") as f:
			json.dump(metrics, f, indent=2)

		self.model = model
		self.loaded_version = new_version
		self._write_app_settings(active_version=new_version)
		return metrics

	def build_dataset_and_train(
		self,
		dataset_path: Path = DATASET_PATH,
		synthetic_records: int = 1000,
		distribution_profile: str = "uniform",
		append_only: bool = False,
	) -> dict:
		self.build_dataset(
			dataset_path=dataset_path,
			synthetic_records=synthetic_records,
			append_only=append_only,
			distribution_profile=distribution_profile,
		)
		return self.train_from_dataset(dataset_path=dataset_path)

	def predict(self, features: dict) -> float:
		if self.model is None:
			self._load(None)
		if self.model is None:
			raise RuntimeError("No trained model found. Train model first.")

		input_df = pd.DataFrame(
			[
				{
					"brand": features["brand"],
					"ram": float(features["ram"]),
					"storage": float(features["storage"]),
					"battery_capacity": float(features["battery_capacity"]),
					"screen_size": float(features["screen_size"]),
					"camera_mp": float(features["camera_mp"]),
					"release_year": float(features["release_year"]),
					"days_used": float(features["days_used"]),
				}
			]
		)
		pred = self.model.predict(input_df)[0]
		return round(float(pred), 2)
