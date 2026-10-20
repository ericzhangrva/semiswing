"""Configuration loader and Pydantic validation models for SemiSwing."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

TICKER_ALIASES: Dict[str, str] = {
    "PSTG": "P",  # Pure Storage, Inc. -> Everpure, Inc. (transitioned from PSTG to P on 2026-04-17)
}


def resolve_ticker(ticker: str) -> str:
    """Resolve historical or re-branded ticker symbols to their active tradeable symbol."""
    return TICKER_ALIASES.get(ticker.upper(), ticker.upper())


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
    vix_max_entry: float = 22.0
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
    dynamic_pit_reconstitution: bool = True
    pit_min_price: float = 15.0
    pit_min_history_days: int = 60
    pit_min_dollar_vol_60d: float = 150_000_000.0
    pit_top_n: int | None = None
    pit_atr_window: int = 20
    pit_volume_window: int = 60

    @property
    def all_tradeable(self) -> List[str]:
        return [resolve_ticker(t) for t in self.tradeable_stocks + self.tradeable_etfs]

    @property
    def all_panel_stocks(self) -> List[str]:
        return [resolve_ticker(t) for t in self.tradeable_stocks + self.training_only_stocks]

    @property
    def all_equity_and_context(self) -> List[str]:
        seen = []
        for t in self.tradeable_stocks + self.tradeable_etfs + self.training_only_stocks + self.context_tickers:
            resolved = resolve_ticker(t)
            if resolved not in seen:
                seen.append(resolved)
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


FAMILY_PORTFOLIO_KEYS: tuple[str, ...] = ("alissa", "eric", "fei_cb", "fei_se_401k")
ISABEL_PORTFOLIO_KEYS: tuple[str, ...] = ("isabel",)


def _encrypt_vault_payload(raw_json: str, passcode: str, target_path: Path) -> Path:
    """Encrypt JSON string with PBKDF2-HMAC-SHA256 and AES-CTR/HMAC-SHA256, write to disk."""
    import base64
    import json
    import secrets

    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(16)
    ct_bytes, tag = _xor_crypt_bytes(raw_json.encode("utf-8"), passcode, salt, nonce)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    vault_obj = {
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "tag": base64.b64encode(tag).decode("ascii"),
        "ct": base64.b64encode(ct_bytes).decode("ascii"),
    }
    target_path.write_text(json.dumps(vault_obj, indent=2), encoding="utf-8")
    return target_path


def _decrypt_vault_payload(target_path: Path, passcode: str) -> Dict[str, PortfolioSettings]:
    """Decrypt encrypted vault JSON into Dict[str, PortfolioSettings]."""
    import base64
    import hashlib
    import hmac
    import json

    if not target_path.exists():
        return {}
    vault_obj = json.loads(target_path.read_text(encoding="utf-8"))
    salt = base64.b64decode(vault_obj["salt"])
    nonce = base64.b64decode(vault_obj["nonce"])
    tag = base64.b64decode(vault_obj["tag"])
    ct_bytes = base64.b64decode(vault_obj["ct"])

    master_key = hashlib.pbkdf2_hmac("sha256", passcode.encode("utf-8"), salt, 150_000, dklen=64)
    mac_key = master_key[32:64]
    expected_tag = hmac.digest(mac_key, nonce + ct_bytes, "sha256")
    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError(f"Invalid passcode for decrypting {target_path.name}")

    pt_bytes, _ = _xor_crypt_bytes(ct_bytes, passcode, salt, nonce)
    raw_map = json.loads(pt_bytes.decode("utf-8"))
    portfolios: Dict[str, PortfolioSettings] = {}
    for k in sorted(raw_map.keys()):
        portfolios[k] = PortfolioSettings(**raw_map[k])
    return portfolios


def export_private_portfolios_json(group: Optional[str] = None) -> str:
    """Serialize private portfolios into a compact JSON string (filtered by group if specified)."""
    import json

    private_dir = PROJECT_ROOT / "config" / "portfolios" / "private"
    payload: Dict[str, dict] = {}
    if private_dir.exists():
        for yf in sorted(private_dir.glob("*.yaml")):
            stem = yf.stem
            if group == "family" and stem not in FAMILY_PORTFOLIO_KEYS:
                continue
            if group == "isabel" and stem not in ISABEL_PORTFOLIO_KEYS:
                continue
            with open(yf, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            payload[stem] = PortfolioSettings(**raw).model_dump()
    return json.dumps(payload, separators=(",", ":"))


def save_encrypted_portfolios_vault(passcode: Optional[str] = None) -> List[Path]:
    """
    Encrypt private portfolios into separate vaults:
    - `encrypted_family.json` via FAMILY_PORTFOLIO_PASSCODE env var
    - `encrypted_isabel.json` via ISABEL_PORTFOLIO_PASSCODE env var
    - `encrypted_portfolios.json` legacy/fallback vault
    """
    import os

    family_pass = (os.environ.get("FAMILY_PORTFOLIO_PASSCODE", "") or passcode or os.environ.get("PORTFOLIO_PASSCODE", "")).strip()
    isabel_pass = (os.environ.get("ISABEL_PORTFOLIO_PASSCODE", "") or passcode or os.environ.get("PORTFOLIO_PASSCODE", "")).strip()
    legacy_pass = (passcode or os.environ.get("PORTFOLIO_PASSCODE", "") or family_pass).strip()

    saved = []
    vault_dir = PROJECT_ROOT / "config" / "portfolios"

    if family_pass:
        fam_json = export_private_portfolios_json(group="family")
        p = _encrypt_vault_payload(fam_json, family_pass, vault_dir / "encrypted_family.json")
        saved.append(p)

    if isabel_pass:
        isa_json = export_private_portfolios_json(group="isabel")
        p = _encrypt_vault_payload(isa_json, isabel_pass, vault_dir / "encrypted_isabel.json")
        saved.append(p)

    if legacy_pass:
        all_json = export_private_portfolios_json()
        p = _encrypt_vault_payload(all_json, legacy_pass, vault_dir / "encrypted_portfolios.json")
        saved.append(p)

    return saved


def load_family_portfolio_settings() -> Dict[str, PortfolioSettings]:
    """Load Family accounts (Eric, Alissa, Fei CB, Fei SE 401K)."""
    import os

    private_dir = PROJECT_ROOT / "config" / "portfolios" / "private"
    if private_dir.exists():
        family = {}
        for k in FAMILY_PORTFOLIO_KEYS:
            yf = private_dir / f"{k}.yaml"
            if yf.exists():
                with open(yf, "r", encoding="utf-8") as f:
                    raw = yaml.safe_load(f) or {}
                family[k] = PortfolioSettings(**raw)
        if family:
            return family

    fam_pass = (os.environ.get("FAMILY_PORTFOLIO_PASSCODE", "") or os.environ.get("PORTFOLIO_PASSCODE", "")).strip()
    if fam_pass:
        fam_vault = PROJECT_ROOT / "config" / "portfolios" / "encrypted_family.json"
        if fam_vault.exists():
            return _decrypt_vault_payload(fam_vault, fam_pass)
        legacy_vault = PROJECT_ROOT / "config" / "portfolios" / "encrypted_portfolios.json"
        if legacy_vault.exists():
            all_p = _decrypt_vault_payload(legacy_vault, fam_pass)
            return {k: v for k, v in all_p.items() if k in FAMILY_PORTFOLIO_KEYS}

    return {}


def load_isabel_portfolio_settings() -> Dict[str, PortfolioSettings]:
    """Load Isabel portfolio (Roth IRA, 401K, HSA)."""
    import os

    private_dir = PROJECT_ROOT / "config" / "portfolios" / "private"
    yf = private_dir / "isabel.yaml"
    if yf.exists():
        with open(yf, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return {"isabel": PortfolioSettings(**raw)}

    isa_pass = (os.environ.get("ISABEL_PORTFOLIO_PASSCODE", "") or os.environ.get("PORTFOLIO_PASSCODE", "")).strip()
    if isa_pass:
        isa_vault = PROJECT_ROOT / "config" / "portfolios" / "encrypted_isabel.json"
        if isa_vault.exists():
            return _decrypt_vault_payload(isa_vault, isa_pass)
        legacy_vault = PROJECT_ROOT / "config" / "portfolios" / "encrypted_portfolios.json"
        if legacy_vault.exists():
            all_p = _decrypt_vault_payload(legacy_vault, isa_pass)
            return {k: v for k, v in all_p.items() if k in ISABEL_PORTFOLIO_KEYS}

    return {}


def load_all_portfolio_settings() -> Dict[str, PortfolioSettings]:
    """Load all portfolios combining Family and Isabel."""
    family = load_family_portfolio_settings()
    isabel = load_isabel_portfolio_settings()
    combined = {**family, **isabel}
    if combined:
        return combined

    fallback_path = PROJECT_ROOT / "config" / "portfolio.yaml"
    if fallback_path.exists():
        with open(fallback_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return {"main": PortfolioSettings(**raw)}
    return {"main": PortfolioSettings()}



