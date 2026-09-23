# Spam Email Validation

A modular machine learning pipeline that classifies emails as **Spam** or **Ham** (legitimate), with a Streamlit UI for single-email checks and batch `.mbox` processing.

## Key Features

- **Modular training pipeline**: data ingestion → transformation (label encoding, TF-IDF) → model training, each stage isolated in `src/components/`.
- **Multi-model evaluation**: grid-searches Logistic Regression, Decision Tree, SVM, KNN, and Random Forest, then picks the best by weighted F1-score.
- **Interactive UI**: Streamlit app for pasting a single email or uploading a Gmail-exported `.mbox` archive for batch classification.
- **CSV-safe output**: batch results are sanitized against control characters and CSV/Excel formula injection before export.

## Tech Stack

- **Language**: Python 3.13
- **Frontend/runtime**: Streamlit (also runs inference in-process — there is no separate API server)
- **ML**: scikit-learn
- **Data**: pandas, BeautifulSoup4 (HTML stripping from email bodies)
- **Project management**: `uv` (recommended) or `pip`

## Project Structure

```
├── app.py                        # Streamlit UI (single-email + batch mbox tabs)
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── components/                # Pipeline stages
│   │   ├── data_ingestion.py      # Loads the training CSV
│   │   ├── data_transformation.py # Label encoding, train/test split, TF-IDF
│   │   └── model_training.py      # Grid search across 5 models, picks the best
│   ├── pipeline/
│   │   ├── training_pipeline.py   # Orchestrates the components above
│   │   └── prediction_pipeline.py # Loads saved model/vectorizer, runs inference
│   ├── config/
│   │   └── config.py              # Paths + hyperparameter grids
│   └── utils/
│       ├── logger.py              # Shared per-run file logger
│       ├── state.py               # TrainingState / PredictionState containers
│       └── email_utils.py         # Body/recipient extraction, CSV-safe cleaning
├── data/dataset/dataset.csv       # Training data (SMS Spam Collection format)
├── outputs/                       # Training artifacts (models, vectorizer, metrics) — gitignored
└── logs/                          # Per-run logs — gitignored
```

## Installation

```bash
git clone <repository_url>
cd spam-email-validation
uv sync            # or: python -m venv .venv && pip install -r requirements.txt
```

> **Note**: pandas is pinned to `<3` — pandas 3.0's stricter string-column typing breaks the label-encoding step in `data_transformation.py`, which assigns integer labels into a string column.

## Usage

### 1. Run the web app

```bash
uv run streamlit run app.py
```

- **Single Email tab**: paste email content, get a Spam/Ham prediction with a confidence score (confidence may be unavailable depending on the trained model — see note below).
- **Batch MBOX Processing tab**: upload a Gmail-exported `.mbox` file, classify every message, preview results, and download the full set as CSV.

### 2. Train the model

```bash
uv run python -m src.pipeline.training_pipeline
```

This runs 5-fold cross-validated grid search across all 5 algorithms and writes the winning model + TF-IDF vectorizer + metrics CSVs to `outputs/<timestamp>/`.

**Important**: inference always loads from the fixed path in `src/config/config.py` (`model_path` / `feature_path`). After retraining, update those two paths to point at the new `outputs/<timestamp>/models/` folder.

## Configuration

`src/config/config.py` controls:
- `training_data_path` / `validation_data_path` — input data locations
- `model_path` / `feature_path` — which trained artifacts inference loads
- `ModelConfig.models` — the hyperparameter grid searched for each algorithm

## Model Performance

Each training run evaluates 5 algorithms with 5-fold cross-validated grid search, scored internally on F1. The overall best model is selected by weighted F1/Precision/Recall/Accuracy on a held-out 30% test split. Metrics for every run are written to `outputs/<timestamp>/observations/`.

**Known limitation**: labels are encoded `spam=0`, `ham=1`. The per-model grid search uses `scoring='f1'`, whose default `pos_label=1` means hyperparameter tuning is implicitly optimized for ham-detection rather than spam-detection, even though the final cross-model comparison uses a class-weighted F1 score. This is inherited, unresolved behavior worth knowing about if you extend the training pipeline.

## License

Distributed under the MIT License.
