"""Triple-barrier labeling, sample uniqueness weights, and purged k-fold cross-validation."""

from __future__ import annotations

from typing import Iterator, Tuple

import numpy as np
import pandas as pd

from semiswing.config import LabelsConfig


def compute_triple_barrier_labels(panel: pd.DataFrame, cfg: LabelsConfig) -> pd.DataFrame:
    """
    For each (ticker, date) bar t_0:
    - Upper barrier: C_0 + tp_atr * ATR_0 (+1.5R)
    - Lower barrier: C_0 - sl_atr * ATR_0 (-1.0R)
    - Vertical barrier: t_0 + horizon trading days (20d)
    Label = 1 if upper barrier is reached before lower barrier within horizon, else 0.
    Also records t_end (the date the barrier was touched or vertical expiry) for purging/uniqueness.
    """
    out_frames = []
    horizon = cfg.horizon
    tp_mult = cfg.tp_atr
    sl_mult = cfg.sl_atr

    for ticker, df_t in panel.groupby("ticker", sort=False):
        df = df_t.sort_values("date").copy().reset_index(drop=True)
        n = len(df)
        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        atrs = df["atr"].values
        dates = df["date"].values

        labels = np.full(n, np.nan, dtype=np.float64)
        realized_r = np.full(n, np.nan, dtype=np.float64)
        t_end_idx = np.arange(n, dtype=int)

        for i in range(n - 1):
            c0 = closes[i]
            atr0 = atrs[i]
            if np.isnan(c0) or np.isnan(atr0) or atr0 <= 0:
                continue

            upper = c0 + tp_mult * atr0
            lower = c0 - sl_mult * atr0
            risk_unit = sl_mult * atr0
            max_j = min(n - 1, i + horizon)

            hit_label = 0.0
            end_j = max_j
            r_mult = (closes[max_j] - c0) / risk_unit

            for j in range(i + 1, max_j + 1):
                hit_dn = lows[j] <= lower
                hit_up = highs[j] >= upper
                if hit_dn and hit_up:
                    # Conservative tie-break: assume stop hit first
                    hit_label = 0.0
                    end_j = j
                    r_mult = -1.0
                    break
                elif hit_dn:
                    hit_label = 0.0
                    end_j = j
                    r_mult = -1.0
                    break
                elif hit_up:
                    hit_label = 1.0
                    end_j = j
                    r_mult = tp_mult / sl_mult
                    break

            labels[i] = hit_label
            realized_r[i] = r_mult
            t_end_idx[i] = end_j

        # Last `horizon` bars don't have full 20d lookahead unless a barrier already hit;
        # To prevent any partial-window leakage in training, mask the final `horizon` bars if not resolved early
        for i in range(max(0, n - horizon), n):
            if t_end_idx[i] >= n - 1:
                labels[i] = np.nan

        df["tb_label"] = labels
        df["tb_realized_r"] = realized_r
        df["tb_end_date"] = dates[t_end_idx]
        df["tb_span_bars"] = np.maximum(1, t_end_idx - np.arange(n))
        # Uniqueness weight: inversely proportional to average span overlap
        df["sample_weight"] = 1.0 / np.clip(df["tb_span_bars"], 1.0, float(horizon))
        out_frames.append(df)

    if not out_frames:
        return panel
    return pd.concat(out_frames, ignore_index=True).sort_values(["date", "ticker"]).reset_index(drop=True)


class PurgedEmbargoKFold:
    """
    Purged K-Fold cross-validator across time with an embargo period (Lopez de Prado).
    Splits by unique dates so all tickers on date t stay in the same fold, and purges
    any training observation whose label horizon overlaps the test fold or embargo window.
    """

    def __init__(self, n_splits: int = 5, embargo_days: int = 20):
        self.n_splits = n_splits
        self.embargo_days = embargo_days

    def split(self, df: pd.DataFrame) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        unique_dates = np.sort(df["date"].unique())
        fold_Dates = np.array_split(unique_dates, self.n_splits)
        dates_col = df["date"].values
        end_dates_col = df["tb_end_date"].values

        for fold_idx in range(self.n_splits):
            test_d = fold_Dates[fold_idx]
            if len(test_d) == 0:
                continue
            t_start = test_d[0]
            t_end = test_d[-1]
            # Embargo end date
            embargo_pos = min(len(unique_dates) - 1, np.searchsorted(unique_dates, t_end) + self.embargo_days)
            t_embargo_end = unique_dates[embargo_pos]

            test_mask = (dates_col >= t_start) & (dates_col <= t_end)
            # Purge any training sample that starts in [t_start, t_embargo_end] OR whose tb_end_date >= t_start
            overlap_before = (dates_col < t_start) & (end_dates_col >= t_start)
            in_test_or_embargo = (dates_col >= t_start) & (dates_col <= t_embargo_end)
            train_mask = ~(overlap_before | in_test_or_embargo)

            train_indices = np.where(train_mask)[0]
            test_indices = np.where(test_mask)[0]
            if len(train_indices) > 0 and len(test_indices) > 0:
                yield train_indices, test_indices
