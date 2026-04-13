# Exploratory Data Analysis (EDA) and Feature Engineering Proposition Report

This report elucidates the comprehensive data science methodology utilized to investigate the `sample_phone_data.csv` dataset from a blank slate perspective. The primary objective is to exclusively leverage mathematical and statistical empirical evidence to guide the data schema design, substantiating the strategic decisions to either retain (Keep) or exclude (Drop) specific predictive features for the artificial intelligence modeling phase.

## 1. Missing Values Heatmap
![Missing Values](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/01_missing_values.png)

- **Implication & Analysis:** The raw dataset exhibits pervasive missing values (represented by yellow bands) dispersed across multiple columns. The integration of incomplete data instances directly into regression models intrinsically provokes algorithmic failures.
- **Data Engineering Conclusion:** Formulate a preprocessing pipeline implementing a `SimpleImputer` strategy, utilizing median imputation for numerical variables and mode imputation for categorical representations.

## 2. Normalized Used Price Distribution
![Distribution](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/02_price_distribution.png)

- **Implication & Analysis:** The distribution topography of the designated target variable portrays a definitive bell-curve structure (Gaussian Distribution).
- **Data Engineering Conclusion:** Machine learning paradigms inherently favor normalized distributions to mitigate algorithmic overfitting. The logarithmically transformed target variable optimally satisfies standardization criteria.

## 3. Brand vs. Used Price Boxplot
![Boxplot](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/03_brand_boxplot.png)

- **Implication & Analysis:** The boxplot delineates pronounced interquartile variance across brands (e.g., Apple and Samsung possess profoundly elevated fiscal anchors relative to Xiaomi or Oppo).
- **Feature Selection Conclusion:** Manufacturer branding acts as an instrumental demographic stratifier. **Recommendation: Indisputably retain the `device_brand` feature.**

## 4. Hardware vs. Price Scatterplots
![Scatter Plots](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/04_hardware_scatter.png)

- **Implication & Analysis:** Scatter coordinate mapping targets linear correlation metrics. Ascending coordinate distributions mathematically denote significant predictive signals.
- **Feature Selection Conclusion:** Both volatile memory (RAM) and internal storage parameter clouds exhibit an acute positive gradient. **Recommendation: Imperatively retain `ram` and `internal_memory`.**

## 5. Target Variable Pearson Correlation Plot
![Correlation Plot](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/05_correlation_plot.png)

- **Implication & Analysis:** Utilizing the Pearson correlation coefficient to benchmark feature validity against the target pricing reveals critically anomalous behavior in `normalized_new_price` (coefficient > 0.85).
- **Feature Selection Conclusion:** Pre-existing original valuation data induces a phenomenon known as Target Leakage, thereby contaminating predictive inferences. **Recommendation: Mandatorily drop the `normalized_new_price` feature.**

## 6. Comprehensive Correlation Heatmap Matrix
![Correlation Matrix](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/07_correlation_matrix.png)

- **Implication & Analysis:** The heatmap evaluates cross-feature multicollinearity dynamics. High thermal density intersections represent substantial informational redundancy between distinct variables.
- **Feature Selection Conclusion:** The evidence highlights that the `os` variable fundamentally mirrors manufacturer constraints via `device_brand` dependency (Multicollinearity constraint). **Recommendation: Exclude the `os` feature.**

## 7. Brand Market Share Countplot
![Brand Market Share](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/08_brand_market_share.png)

- **Implication & Analysis:** Uncovering severe dataset distribution imbalance (Class Imbalance) across manufacturer categories. Prominent demographic groups lack representation at pivotal data peaks.
- **Data Engineering Conclusion:** This necessitates the strategic integration of Synthetic Data Generation methodologies to interpolate missing device data (notably corresponding to flagship Apple models) ensuring an algorithmically unbiased training phase.

## 8. Price vs. Release Year Trend Lineplot
![Release Year Trend](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/09_price_vs_year_trend.png)

- **Implication & Analysis:** Chronological lineplot trajectories expose temporal deprecation rates (Time-Series Depreciation). Distinct structural inflexions originating prior to 2017 indicate an inverse ratio between chronological age and fiscal valuation.
- **Feature Selection Conclusion:** Depreciation temporal metrics provide immense baseline modeling precision. **Recommendation: Unequivocally retain `release_year` and `days_used`.**

## 9. Hardware Distribution Histograms
![Hardware Distribution](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/10_hardware_distribution.png)

- **Implication & Analysis:** Volumetric density histograms illustrate frequency groupings. Data magnitudes cluster excessively proximate to 4GB RAM thresholds and 3000 mAh battery capacity margins.
- **Data Engineering Conclusion:** The evident presence of long-tail distributions imposes strict extrapolation caveats. Predictive inferencing algorithms managing extreme systemic outliers (e.g., 12GB+ RAM flagship variants) require calibrated generalization handling mechanisms.

---
# SYNTHESIS: CONSOLIDATED FEATURE ENGINEERING PROPOSITION

Assembling the empirical verdicts generated from objective blank-slate exploratory analysis, the optimal feature domain translates into:

### ❌ Excluded Variables (Multicollinearity / Target Leakage / Noise Abatement)
1. **`normalized_new_price`**: Exclude (Mitigates target leakage contamination).
2. **`os`**: Exclude (Abrogates redundant architectural multicollinearity).
3. **`weight`** and **`front_camera_mp`**: Exclude (Presents statistically negligible correlative significance).

### 💎 Core Predictive Features (Authorized Retention of 8 Parameters)
> **`device_brand`** (Socio-economic stratified valuation identifier substantiated via Boxplot analysis).
> **`ram`**, **`internal_memory`** (Primary computational capacities displaying robust linear covariance via Scatter plotting).
> **`battery`**, **`screen_size`**, **`rear_camera_mp`** (Baseline dimensional functionality parameters driving primary regression decision nodes).
> **`release_year`**, **`days_used`** (Temporal constraints anchoring algorithmic technology lifecycle depreciation models).
