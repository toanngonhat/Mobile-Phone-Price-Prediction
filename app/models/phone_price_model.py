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

	def _try_load_version(self, version: int) -> bool:
		model_path = MODEL_VERSIONS_DIR / f"v{version}" / "model.pkl"
		if not model_path.exists():
			return False
		try:
			self.model = joblib.load(model_path)
			self.loaded_version = version
			return True
		except Exception:
			return False

	def _load(self, version: int | None = None) -> None:
		self.model = None
		self.loaded_version = None

		if version is not None:
			if not self._try_load_version(version):
				raise RuntimeError(f"Model version v{version} could not be loaded")
			return

		settings = self._read_app_settings()
		active_version = settings.get("active_model_version")
		versions = sorted(self._available_versions(), reverse=True)

		candidates: list[int] = []
		if isinstance(active_version, int):
			candidates.append(active_version)
		candidates.extend([v for v in versions if v not in candidates])

		for candidate in candidates:
			if self._try_load_version(candidate):
				return

	def _mock_predict(self, features: dict) -> float:
		# Deterministic fallback used when no serialized model can be loaded.
		base_price = 120.0
		base_price += float(features.get("ram", 4)) * 35.0
		base_price += float(features.get("storage", 64)) * 1.1
		base_price += float(features.get("camera_mp", 12)) * 4.0
		base_price += float(features.get("screen_size", 6.1)) * 18.0
		base_price += float(features.get("battery_capacity", 3000)) * 0.05
		base_price -= float(features.get("days_used", 365)) * 0.2
		year_bonus = max(0.0, float(features.get("release_year", 2022)) - 2018) * 20.0
		price = base_price + year_bonus
		return round(max(50.0, price), 2)

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

	def _prepare_training_matrix(self, raw_df: pd.DataFrame, features: list[str] = None) -> tuple[pd.DataFrame, pd.Series]:
		all_X = {
			"brand": raw_df["device_brand"].astype(str),
			"os": raw_df["os"].astype(str),
			"ram": raw_df["ram"].astype(float),
			"storage": raw_df["internal_memory"].astype(float),
			"battery_capacity": raw_df["battery"].astype(float),
			"screen_size": raw_df["screen_size"].astype(float) / 2.54,
			"camera_mp": raw_df["rear_camera_mp"].astype(float),
			"front_camera_mp": raw_df["front_camera_mp"].astype(float),
			"weight": raw_df["weight"].astype(float),
			"release_year": raw_df["release_year"].astype(float),
			"days_used": raw_df["days_used"].astype(float),
			"normalized_new_price": raw_df["normalized_new_price"].astype(float),
		}
		if features:
			available_keys = [k for k in all_X.keys() if k in features]
			if not available_keys:
				available_keys = list(all_X.keys())
			all_X = {k: all_X[k] for k in available_keys}
		
		X = pd.DataFrame(all_X)
		y = np.exp(raw_df["normalized_used_price"].astype(float))
		return X, y

	def _new_pipeline(self, n_estimators: int = 100, max_depth: int | None = None, min_samples_split: int = 2, min_samples_leaf: int = 1, features: list[str] = None) -> Pipeline:
		if not features:
			features = ["brand", "ram", "storage", "battery_capacity", "screen_size", "camera_mp", "release_year", "days_used"]
			
		cat_feats = [f for f in features if f in ["brand", "os"]]
		num_feats = [f for f in features if f not in ["brand", "os"]]
		
		transformers = []
		if cat_feats:
			transformers.append(("cat", Pipeline(steps=[("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))]), cat_feats))
		if num_feats:
			transformers.append(("num", Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))]), num_feats))
			
		preprocessor = ColumnTransformer(transformers=transformers)
		return Pipeline(
			steps=[
				("preprocessor", preprocessor),
				(
					"regressor",
					RandomForestRegressor(
						n_estimators=n_estimators,
						max_depth=max_depth,
						min_samples_split=min_samples_split,
						min_samples_leaf=min_samples_leaf,
						random_state=42,
						n_jobs=-1,
					),
				),
			]
		)

	def train_from_dataset(
        self, 
        dataset_path: Path = DATASET_PATH, 
        n_estimators: int = 100, 
        max_depth: int | None = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        features: list[str] = None
    ) -> dict:
		raw_df = pd.read_csv(dataset_path)
		validate_schema(raw_df)

		X, y = self._prepare_training_matrix(raw_df, features)
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

		model = self._new_pipeline(
            n_estimators=n_estimators, 
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            features=features
        )
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
			"features": features if features else FEATURE_COLUMNS,
			"excluded_features": ["4g", "5g"],
			"target": "exp(normalized_used_price)",
			"mae": float(mean_absolute_error(y_test, preds)),
			"rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
			"r2": float(r2_score(y_test, preds)),
			"n_estimators": n_estimators,
			"max_depth": max_depth,
			"min_samples_split": min_samples_split,
			"min_samples_leaf": min_samples_leaf,
			"trained_at": datetime.now(timezone.utc).isoformat(),
		}

		try:
			rf_model = model.named_steps["regressor"]
			preprocessor = model.named_steps["preprocessor"]
			importances = rf_model.feature_importances_
			feat_names = []
			for name, trans, cols in preprocessor.transformers_:
				if name == "cat":
					ohe = trans.named_steps["encoder"]
					feat_names.extend([f.split("_")[0] for f in ohe.get_feature_names_out(cols)])
				elif name == "num":
					feat_names.extend(cols)
			
			if len(feat_names) == len(importances):
				fi_dict = {}
				for fn, imp in zip(feat_names, importances):
					fi_dict[fn] = fi_dict.get(fn, 0) + float(imp)
				
				# Sort by importance
				metrics["feature_importances"] = {k: v for k, v in sorted(fi_dict.items(), key=lambda item: item[1], reverse=True)}
		except Exception:
			metrics["feature_importances"] = {}

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
		n_estimators: int = 100,
		max_depth: int | None = None,
	) -> dict:
		self.build_dataset(
			dataset_path=dataset_path,
			synthetic_records=synthetic_records,
			append_only=append_only,
			distribution_profile=distribution_profile,
		)
		return self.train_from_dataset(dataset_path=dataset_path, n_estimators=n_estimators, max_depth=max_depth)

	def predict(self, features: dict) -> float:
		if self.model is None:
			self._load(None)
		if self.model is None:
			return self._mock_predict(features)

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
