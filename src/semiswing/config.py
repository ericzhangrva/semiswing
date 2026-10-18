"""Configuration loader and Pydantic validation models for SemiSwing."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class BacktestConfig(BaseModel):
    start_date: str = "2018-01-01"
    oos_start_date: str = "2022-01-01"
    ai_era_start: str = "2023-01-01"
    commission_bps: float = 2.0
    slippage_bps: float = 5.0


class WindowConfig(BaseModel):
    fixed: List[int] = Field(default_factory=lambda: [10, 20, 40])
    base: int = 20
    min: int = 10
    max: int = 60
    use_cpd: bool = False


class RegimeConfig(BaseModel):
    smh_ema: int = 200
    smh_ema_slow: int = 200
    smh_ema_fast: int = 50
    hysteresis_band_pct: float = 0.015  # 1.5% buffer above/below EMA200 (Schmitt trigger)
    vix_max: float = 28.0
    vix_max_entry: float = 28.0
    vix_kill_switch: float = 32.0
    vix_ts_max: float = 1.00
    vvix_max: float = 110.0
    premarket_gap_down_max: float = 0.015  # Cancel long execution if pre-market SMH gaps down > 1.5%



class BaselineConfig(BaseModel):
    slope_t_norm_min: float = 2.0
    slope_r2_min: float = 0.50
    rs_rank_min: float = 0.50
    ext_atr_min: float = 0.0
    ext_atr_max: float = 2.5
    earnings_buffer_days: int = 7
    min_price: float = 10.0
    min_dollar_vol_20d: float = 200_000_000.0


class LabelsConfig(BaseModel):
    tp_atr: float = 3.0
    sl_atr: float = 2.0
    horizon: int = 20


class ModelConfig(BaseModel):
    calibration: str = "percentile_rank"
    max_depth: int = 2
    num_leaves: int = 4
    min_child_samples: int = 60
    n_estimators: int = 100
    learning_rate: float = 0.03
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    embargo_days: int = 20
    n_splits: int = 5
    retrain_freq_days: int = 63
    min_sizing_scalar: float = 0.50
    max_sizing_scalar: float = 1.50



class GateConfig(BaseModel):
    p_min: float = 0.60
    p_high: float = 0.65
    p_exit: float = 0.45
    exit_confirm_runs: int = 2
    ev_min_r: float = 0.45


class DataHealthConfig(BaseModel):
    eod_tolerance: float = 0.005
    intraday_tolerance: float = 0.005
    iex_max_age_min: int = 3
    max_staleness_min: int = 5
    min_health: int = 80


class RiskConfig(BaseModel):
    paper_equity: float = 10_000.0
    risk_per_trade: float = 0.01
    risk_per_trade_medium: float = 0.005
    stop_atr: float = 2.0
    tp1_atr: float = 3.0
    tp1_fraction: float = 0.50
    breakeven_trigger_r: float = 1.0
    trail_atr: float = 2.5
    time_stop: int = 20
    early_time_stop_day: int = 10
    early_time_stop_min_r: float = 0.5
    backstop: float = 0.12
    max_pos_pct: float = 0.35
    max_positions: int = 3
    max_open_risk: float = 0.025
    max_corr_60d: float = 0.85
    max_correlated_names: int = 2
    dd_kill: float = 0.10
    cooldown_days: int = 10
    streak_stop_limit: int = 3


class AlertsConfig(BaseModel):
    channels: List[str] = Field(default_factory=lambda: ["sms_messages", "ntfy"])
    quiet_start: str = "17:00"
    quiet_end: str = "08:00"
    max_entry_per_ticker_day: int = 1
    retry_seconds: int = 60


class StrategySettings(BaseModel):
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    window: WindowConfig = Field(default_factory=WindowConfig)
    regime: RegimeConfig = Field(default_factory=RegimeConfig)
    baseline: BaselineConfig = Field(default_factory=BaselineConfig)
    labels: LabelsConfig = Field(default_factory=LabelsConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    gate: GateConfig = Field(default_factory=GateConfig)
    data: DataHealthConfig = Field(default_factory=DataHealthConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    alerts: AlertsConfig = Field(default_factory=AlertsConfig)


class UniverseSettings(BaseModel):
    tradeable_stocks: List[str]
    tradeable_etfs: List[str]
    training_only_stocks: List[str]
    context_tickers: List[str]
    fred_series: Dict[str, str]

    @property
    def all_tradeable(self) -> List[str]:
        return self.tradeable_stocks + self.tradeable_etfs

    @property
    def all_panel_stocks(self) -> List[str]:
        return self.tradeable_stocks + self.training_only_stocks

    @property
    def all_equity_and_context(self) -> List[str]:
        seen = []
        for t in self.tradeable_stocks + self.tradeable_etfs + self.training_only_stocks + self.context_tickers:
            if t not in seen:
                seen.append(t)
        return seen


class EventsSettings(BaseModel):
    fomc_dates: List[str]


class PortfolioPosition(BaseModel):
    ticker: str
    description: str = ""
    role: str = "swing"
    proxy_ticker: str = ""
    shares: float
    avg_cost: float
    last_price: float = 0.0
    current_value: float = 0.0
    entry_date: str = ""
    current_stop: float = 0.0
    tp1_hit: bool = False
    notes: str = ""


class PortfolioSettings(BaseModel):
    account_name: str = "SemiSwing Portfolio"
    snapshot_date: str = ""
    cash: float = 10_000.0
    positions: List[PortfolioPosition] = Field(default_factory=list)


def load_strategy_settings(path: Path | None = None) -> StrategySettings:
    p = path or (PROJECT_ROOT / "config" / "strategy.yaml")
    with open(p, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return StrategySettings(**raw)


def load_universe_settings(path: Path | None = None) -> UniverseSettings:
    p = path or (PROJECT_ROOT / "config" / "universe.yaml")
    with open(p, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return UniverseSettings(**raw)


def load_events_settings(path: Path | None = None) -> EventsSettings:
    p = path or (PROJECT_ROOT / "config" / "events.yaml")
    with open(p, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return EventsSettings(**raw)


def load_portfolio_settings(path: Path | None = None) -> PortfolioSettings:
    if path is None:
        all_portfolios = load_all_portfolio_settings()
        if all_portfolios:
            return next(iter(all_portfolios.values()))
    p = path or (PROJECT_ROOT / "config" / "portfolio.yaml")
    if not p.exists():
        return PortfolioSettings()
    with open(p, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return PortfolioSettings(**raw)


def _xor_crypt_bytes(data: bytes, passcode: str, salt: bytes, nonce: bytes) -> tuple[bytes, bytes]:
    import hashlib
    import hmac

    master_key = hashlib.pbkdf2_hmac("sha256", passcode.encode("utf-8"), salt, 150_000, dklen=64)
    enc_key = master_key[:32]
    mac_key = master_key[32:64]

    out = bytearray(len(data))
    num_blocks = (len(data) + 31) // 32
    for i in range(num_blocks):
        ks = hmac.digest(enc_key, nonce + i.to_bytes(4, "big"), "sha256")
        start = i * 32
        end = min(start + 32, len(data))
        for j in range(end - start):
            out[start + j] = data[start + j] ^ ks[j]
    out_bytes = bytes(out)
    tag = hmac.digest(mac_key, nonce + out_bytes, "sha256")
    return out_bytes, tag


def save_encrypted_portfolios_vault(passcode: Optional[str] = None) -> Path:
    """Encrypt `config/portfolios/private/*.yaml` into `config/portfolios/encrypted_portfolios.json` for safe cloud execution."""
    import base64
    import json
    import os
    import secrets

    effective_passcode = (passcode or os.environ.get("PORTFOLIO_PASSCODE", "")).strip()
    if not effective_passcode:
        raise ValueError(
            "PORTFOLIO_PASSCODE is required to encrypt private portfolios vault. "
            "Set it in your local .env or CI secrets."
        )

    raw_json = export_private_portfolios_json().encode("utf-8")
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(16)
    ct_bytes, tag = _xor_crypt_bytes(raw_json, effective_passcode, salt, nonce)

    vault_path = PROJECT_ROOT / "config" / "portfolios" / "encrypted_portfolios.json"
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    vault_obj = {
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "tag": base64.b64encode(tag).decode("ascii"),
        "ct": base64.b64encode(ct_bytes).decode("ascii"),
    }
    vault_path.write_text(json.dumps(vault_obj, indent=2), encoding="utf-8")
    return vault_path


def load_encrypted_portfolios_vault(passcode: Optional[str] = None) -> Dict[str, PortfolioSettings]:
    """Decrypt `config/portfolios/encrypted_portfolios.json` in memory (used by GitHub Actions at 9:00 AM ET)."""
    import base64
    import hashlib
    import hmac
    import json
    import os

    effective_passcode = (passcode or os.environ.get("PORTFOLIO_PASSCODE", "")).strip()
    if not effective_passcode:
        raise ValueError(
            "PORTFOLIO_PASSCODE is required to decrypt encrypted_portfolios.json. "
            "Set it in your local .env or CI secrets."
        )

    vault_path = PROJECT_ROOT / "config" / "portfolios" / "encrypted_portfolios.json"
    if not vault_path.exists():
        return {}
    vault_obj = json.loads(vault_path.read_text(encoding="utf-8"))
    salt = base64.b64decode(vault_obj["salt"])
    nonce = base64.b64decode(vault_obj["nonce"])
    tag = base64.b64decode(vault_obj["tag"])
    ct_bytes = base64.b64decode(vault_obj["ct"])

    master_key = hashlib.pbkdf2_hmac("sha256", effective_passcode.encode("utf-8"), salt, 150_000, dklen=64)
    mac_key = master_key[32:64]
    expected_tag = hmac.digest(mac_key, nonce + ct_bytes, "sha256")
    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("Invalid PORTFOLIO_PASSCODE for decrypting encrypted_portfolios.json")

    pt_bytes, _ = _xor_crypt_bytes(ct_bytes, effective_passcode, salt, nonce)
    raw_map = json.loads(pt_bytes.decode("utf-8"))
    portfolios: Dict[str, PortfolioSettings] = {}
    for k in sorted(raw_map.keys()):
        portfolios[k] = PortfolioSettings(**raw_map[k])
    return portfolios


def load_all_portfolio_settings() -> Dict[str, PortfolioSettings]:
    """
    Load all user portfolios in priority order:
    1. `PORTFOLIOS_SECRET_JSON` environment variable (if set).
    2. Local gitignored `config/portfolios/private/*.yaml` files (and auto-sync `encrypted_portfolios.json`).
    3. Encrypted cloud vault `config/portfolios/encrypted_portfolios.json` (used on GitHub Actions at 9AM).
    4. Fallback to `config/portfolio.yaml`.
    """
    import json
    import os

    passcode = os.environ.get("PORTFOLIO_PASSCODE", "").strip()
    secret_json = os.environ.get("PORTFOLIOS_SECRET_JSON", "").strip()
    if secret_json:
        raw_map = json.loads(secret_json)
        portfolios: Dict[str, PortfolioSettings] = {}
        for k in sorted(raw_map.keys()):
            portfolios[k] = PortfolioSettings(**raw_map[k])
        if portfolios:
            return portfolios

    private_dir = PROJECT_ROOT / "config" / "portfolios" / "private"
    if private_dir.exists():
        yaml_files = sorted(private_dir.glob("*.yaml"))
        if yaml_files:
            portfolios = {}
            for yf in yaml_files:
                with open(yf, "r", encoding="utf-8") as f:
                    raw = yaml.safe_load(f) or {}
                portfolios[yf.stem] = PortfolioSettings(**raw)
            if passcode:
                save_encrypted_portfolios_vault(passcode=passcode)
            return portfolios

    if passcode:
        vault_portfolios = load_encrypted_portfolios_vault(passcode=passcode)
        if vault_portfolios:
            return vault_portfolios

    fallback_path = PROJECT_ROOT / "config" / "portfolio.yaml"
    if fallback_path.exists():
        with open(fallback_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return {"main": PortfolioSettings(**raw)}
    return {"main": PortfolioSettings()}


def export_private_portfolios_json() -> str:
    """Serialize all `config/portfolios/private/*.yaml` portfolios into a compact JSON string."""
    import json

    private_dir = PROJECT_ROOT / "config" / "portfolios" / "private"
    payload: Dict[str, dict] = {}
    if private_dir.exists():
        for yf in sorted(private_dir.glob("*.yaml")):
            with open(yf, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            payload[yf.stem] = PortfolioSettings(**raw).model_dump()
    return json.dumps(payload, separators=(",", ":"))



