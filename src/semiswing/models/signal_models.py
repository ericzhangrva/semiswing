"""Baseline rule strategy, Walk-Forward Gradient Boosted Trees + Platt calibration, Confidence Gate, and feature attribution."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

from semiswing.config import StrategySettings
from semiswing.features.build import FEATURE_COLUMNS
from semiswing.labels.triple_barrier import PurgedEmbargoKFold

try:
    import lightgbm as lgb

    _HAS_LGBM = True
except Exception:
    lgb = None
    _HAS_LGBM = False


def evaluate_baseline_signals(
    panel: pd.DataFrame,
    strategy: StrategySettings,
    use_fixed_20d: bool = False,
    health_score: float = 100.0,
    allowed_tickers: set[str] | tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """
    Evaluate deterministic Baseline Rule Strategy (§5.2 of instruction.md).
    If use_fixed_20d=True, uses fixed 20d OLS slope_t_norm_20d and slope_r2_20d
    instead of adaptive window L_t to benchmark adaptive vs fixed windows.
    If allowed_tickers is provided, cross-sectional rs_rank is computed strictly within that subset.
    """
    df = panel.copy()
    bcfg = strategy.baseline

    if allowed_tickers is not None:
        allowed_set = set(allowed_tickers)
        sub_mask = df["ticker"].isin(allowed_set)
        df["rs_rank"] = 0.0
        df.loc[sub_mask, "rs_rank"] = (
            df.loc[sub_mask].groupby("date")["resid_mom_20"].rank(pct=True, na_option="keep")
        ).fillna(0.5)

    slope_col = "slope_t_norm_20d" if use_fixed_20d else "slope_t_norm"
    r2_col = "slope_r2_20d" if use_fixed_20d else "slope_r2"

    liq_ok = (df["close"] >= bcfg.min_price) & (df["dollar_vol_20d"] >= bcfg.min_dollar_vol_20d)
    health_ok = health_score >= strategy.data.min_health

    cond = (
        (df["is_tradeable_universe"] == 1)
        & liq_ok
        & health_ok
        & (df["regime_on"] == 1)
        & (df[slope_col] >= bcfg.slope_t_norm_min)
        & (df[r2_col] >= bcfg.slope_r2_min)
        & (df["slope_accel"] > 0.0)
        & (df["ema20_slope"] > 0.0)
        & (df["rs_rank"] >= bcfg.rs_rank_min)
        & (df["ext_atr"] >= bcfg.ext_atr_min)
        & (df["ext_atr"] <= bcfg.ext_atr_max)
        & (df["days_to_earnings"] > bcfg.earnings_buffer_days)
        & (df["fomc_next_day"] == 0)
    )

    df["baseline_signal"] = cond.astype(int)
    df["baseline_score"] = np.where(cond, df[slope_col] * df["rs_rank"], 0.0)
    df["baseline_tier"] = np.where(cond, "HIGH", "NONE")
    df["baseline_prob"] = np.where(cond, 0.65, 0.50)
    return df


def _build_monotone_constraints(feature_cols: List[str]) -> List[int]:
    """Enforce positive monotone constraints on trend conviction and relative momentum."""
    pos_features = {"slope_t_norm", "slope_t_norm_20d", "resid_mom_20", "rs_rank"}
    return [1 if c in pos_features else 0 for c in feature_cols]


class PlattCalibratedGBM:
    """
    Shallow Histogram Gradient Boosted Trees classifier (LightGBM architecture) with
    2-parameter Platt scaling (sigmoid calibration) fitted on purged out-of-fold log-odds
    predictions to prevent small-sample overfitting.
    """

    def __init__(self, strategy: StrategySettings, feature_cols: List[str] | None = None):
        self.strategy = strategy
        self.feature_cols = feature_cols or FEATURE_COLUMNS
        self.models: List[object] = []
        self.platt: LogisticRegression | None = None
        self.oof_brier_raw: float = np.nan
        self.oof_brier_cal: float = np.nan
        self.feature_means: np.ndarray | None = None
        self.feature_stds: np.ndarray | None = None

    def _make_estimator(self, seed: int = 42) -> object:
        mcfg = self.strategy.model
        mono = _build_monotone_constraints(self.feature_cols)
        if _HAS_LGBM:
            return lgb.LGBMClassifier(
                objective="binary",
                max_depth=mcfg.max_depth,
                num_leaves=mcfg.num_leaves,
                min_child_samples=mcfg.min_child_samples,
                n_estimators=mcfg.n_estimators,
                learning_rate=mcfg.learning_rate,
                subsample=mcfg.subsample,
                subsample_freq=1,
                colsample_bytree=mcfg.colsample_bytree,
                monotone_constraints=mono,
                random_state=seed,
                n_jobs=1,
                verbose=-1,
            )
        return HistGradientBoostingClassifier(
            max_depth=mcfg.max_depth,
            max_leaf_nodes=mcfg.num_leaves,
            min_samples_leaf=mcfg.min_child_samples,
            max_iter=mcfg.n_estimators,
            learning_rate=mcfg.learning_rate,
            monotonic_cst=mono,
            l2_regularization=1.0,
            early_stopping=False,
            random_state=seed,
        )

    def fit(self, train_df: pd.DataFrame) -> "PlattCalibratedGBM":
        clean = train_df.dropna(subset=["tb_label"] + self.feature_cols).copy().reset_index(drop=True)
        if len(clean) < 120 or clean["tb_label"].nunique() < 2:
            self.models = []
            self.platt = None
            return self

        X = clean[self.feature_cols].values.astype(np.float64)
        y = clean["tb_label"].values.astype(int)
        w = clean["sample_weight"].values.astype(np.float64)

        self.feature_means = np.nanmean(X, axis=0)
        self.feature_stds = np.where(np.nanstd(X, axis=0) > 1e-8, np.nanstd(X, axis=0), 1.0)

        cv = PurgedEmbargoKFold(
            n_splits=self.strategy.model.n_splits,
            embargo_days=self.strategy.model.embargo_days,
        )
        oof_raw = np.full(len(clean), np.nan, dtype=np.float64)
        self.models = []

        for fold_i, (tr_idx, val_idx) in enumerate(cv.split(clean)):
            if len(np.unique(y[tr_idx])) < 2:
                continue
            clf = self._make_estimator(seed=42 + fold_i)
            clf.fit(X[tr_idx], y[tr_idx], sample_weight=w[tr_idx])
            oof_raw[val_idx] = clf.predict_proba(X[val_idx])[:, 1]
            self.models.append(clf)

        full_clf = self._make_estimator(seed=100)
        full_clf.fit(X, y, sample_weight=w)
        self.models.append(full_clf)

        valid_oof = ~np.isnan(oof_raw)
        if valid_oof.sum() >= 30 and len(np.unique(y[valid_oof])) == 2:
            raw_p = np.clip(oof_raw[valid_oof], 1e-4, 1.0 - 1e-4)
            self.oof_brier_raw = float(brier_score_loss(y[valid_oof], raw_p))
            logits = np.log(raw_p / (1.0 - raw_p)).reshape(-1, 1)
            platt = LogisticRegression(C=1.0, solver="lbfgs")
            platt.fit(logits, y[valid_oof], sample_weight=w[valid_oof])
            if platt.coef_[0][0] > 0:
                self.platt = platt
                cal_p = 0.70 * platt.predict_proba(logits)[:, 1] + 0.30 * raw_p
                self.oof_brier_cal = float(brier_score_loss(y[valid_oof], cal_p))
            else:
                self.oof_brier_cal = self.oof_brier_raw

        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        if not self.models:
            return np.full(len(df), 0.50, dtype=np.float64)

        X = df[self.feature_cols].fillna(0.0).values.astype(np.float64)
        raw_preds = np.mean([m.predict_proba(X)[:, 1] for m in self.models], axis=0)
        raw_p = np.clip(raw_preds, 1e-4, 1.0 - 1e-4)

        if self.platt is not None:
            logits = np.log(raw_p / (1.0 - raw_p)).reshape(-1, 1)
            cal_p = self.platt.predict_proba(logits)[:, 1]
            return 0.70 * cal_p + 0.30 * raw_p
        return raw_p

    def explain_row(self, row_df: pd.DataFrame, top_k: int = 5) -> str:
        """
        Compute exact single-feature marginal log-odds / probability contributions
        by comparing the row against the training mean for each feature (exact 1D marginal SHAP proxy).
        """
        if not self.models or row_df.empty or self.feature_means is None:
            return "slope_t_norm, resid_mom_20, rs_rank"

        X_row = row_df[self.feature_cols].fillna(0.0).values.astype(np.float64)[0]
        base_p = float(self.predict_proba(row_df)[0])

        # Build batch matrix where row k replaces feature k with its training mean
        n_feat = len(self.feature_cols)
        perturbed = np.tile(X_row, (n_feat, 1))
        for k in range(n_feat):
            perturbed[k, k] = self.feature_means[k]

        pert_df = pd.DataFrame(perturbed, columns=self.feature_cols)
        pert_probs = self.predict_proba(pert_df)
        contribs = base_p - pert_probs

        order = np.argsort(np.abs(contribs))[::-1][:top_k]
        parts = []
        for idx in order:
            col = self.feature_cols[idx]
            fval = float(X_row[idx])
            cval = float(contribs[idx])
            parts.append(f"{col}={fval:.2f} ({cval:+.3f})")
        return " | ".join(parts)


def run_walkforward_ml_predictions(
    panel: pd.DataFrame,
    strategy: StrategySettings,
    health_score: float = 100.0,
) -> Tuple[pd.DataFrame, PlattCalibratedGBM | None, Dict[str, float]]:
    """
    Expanding-window Walk-Forward training and out-of-sample scoring from oos_start_date (2022-01-01).
    Retrains every 63 trading days using ONLY historical observations whose triple-barrier
    end date (`tb_end_date`) is strictly before the test block start.
    """
    df = panel.sort_values(["date", "ticker"]).copy().reset_index(drop=True)
    df["ml_prob"] = 0.50
    df["ml_ev_r"] = -0.05
    df["ml_signal"] = 0
    df["ml_tier"] = "NONE"
    df["ml_score"] = 0.0
    df["ml_shap"] = ""

    oos_start = pd.to_datetime(strategy.backtest.oos_start_date)
    all_dates = np.sort(df["date"].unique())
    oos_dates = all_dates[all_dates >= oos_start]
    if len(oos_dates) == 0:
        return df, None, {}

    block_size = max(1, int(strategy.model.retrain_freq_days))
    last_model: PlattCalibratedGBM | None = None
    block_models: List[Tuple[pd.Series, PlattCalibratedGBM]] = []
    brier_raw_list = []
    brier_cal_list = []

    for start_idx in range(0, len(oos_dates), block_size):
        block_dates = oos_dates[start_idx : start_idx + block_size]
        t_block_start = block_dates[0]
        t_block_end = block_dates[-1]

        train_mask = (
            (df["is_etf"] == 0)
            & (df["regime_on"] == 1)
            & (df["ema20_slope"] > -0.5)
            & (df["date"] < t_block_start)
            & (df["tb_end_date"] < t_block_start)
            & (~df["tb_label"].isna())
        )
        train_df = df.loc[train_mask]

        model = PlattCalibratedGBM(strategy=strategy)
        model.fit(train_df)
        last_model = model
        if not np.isnan(model.oof_brier_raw):
            brier_raw_list.append(model.oof_brier_raw)
            brier_cal_list.append(model.oof_brier_cal)

        test_mask = (df["date"] >= t_block_start) & (df["date"] <= t_block_end)
        if test_mask.sum() == 0:
            continue
        probs = model.predict_proba(df.loc[test_mask])
        df.loc[test_mask, "ml_prob"] = probs
        block_models.append((test_mask, model))

    reward_r = strategy.labels.tp_atr / strategy.labels.sl_atr  # 3.75 / 2.50 = 1.5R
    costs_r = 0.05
    df["ml_ev_r"] = df["ml_prob"] * reward_r - (1.0 - df["ml_prob"]) * 1.0 - costs_r

    bcfg = strategy.baseline
    gcfg = strategy.gate
    liq_ok = (df["close"] >= bcfg.min_price) & (df["dollar_vol_20d"] >= bcfg.min_dollar_vol_20d)
    health_ok = health_score >= strategy.data.min_health

    qualifies = (
        (df["date"] >= oos_start)
        & (df["is_tradeable_universe"] == 1)
        & liq_ok
        & health_ok
        & (df["regime_on"] == 1)
        & (df["ml_prob"] >= gcfg.p_min)
        & (df["ml_ev_r"] >= gcfg.ev_min_r)
        & (df["slope_t_norm"] >= 1.2)
        & (df["ema20_slope"] > 0.0)
        & (df["rs_rank"] >= 0.80)
        & (df["ext_atr"] >= bcfg.ext_atr_min)
        & (df["ext_atr"] <= bcfg.ext_atr_max)
        & (df["days_to_earnings"] > bcfg.earnings_buffer_days)
        & (df["fomc_next_day"] == 0)
    )

    df["ml_signal"] = qualifies.astype(int)
    df["ml_tier"] = np.where(
        qualifies & (df["ml_prob"] >= gcfg.p_high),
        "HIGH",
        np.where(qualifies, "MEDIUM", "NONE"),
    )
    df["ml_score"] = np.where(qualifies, df["ml_prob"] * (df["rs_rank"] ** 2) * np.maximum(df["resid_mom_60"], 0.05), 0.0)

    # Compute strictly point-in-time marginal SHAP attributions using each block's trained model
    smh_dts = df.loc[df["ticker"] == "SMH", "date"]
    latest_dt = smh_dts.max() if not smh_dts.empty else all_dates[-1]
    explain_mask = qualifies | ((df["date"] == latest_dt) & (df["is_tradeable_universe"] == 1))
    for test_mask, blk_model in block_models:
        sig_indices = df.index[test_mask & explain_mask].tolist()
        for idx in sig_indices:
            df.loc[idx, "ml_shap"] = blk_model.explain_row(df.loc[[idx]])

    cal_stats = {
        "brier_raw": round(float(np.mean(brier_raw_list)), 4) if brier_raw_list else np.nan,
        "brier_calibrated": round(float(np.mean(brier_cal_list)), 4) if brier_cal_list else np.nan,
    }
    return df, last_model, cal_stats
