from datetime import datetime, timedelta

import pandas as pd

from app import compute_risk_flags, STALE_DAYS_THRESHOLD


def _make_df(rows):
    return pd.DataFrame(rows)


def test_recent_login_is_not_stale():
    recent = (datetime.utcnow() - timedelta(days=5)).strftime("%Y-%m-%d")
    df = _make_df([
        {"username": "a", "department": "IT", "role": "Analyst", "status": "Active", "last_login": recent}
    ])
    result = compute_risk_flags(df)
    assert not result.loc[0, "is_stale"]


def test_old_login_is_stale():
    old = (datetime.utcnow() - timedelta(days=STALE_DAYS_THRESHOLD + 10)).strftime("%Y-%m-%d")
    df = _make_df([
        {"username": "a", "department": "IT", "role": "Analyst", "status": "Active", "last_login": old}
    ])
    result = compute_risk_flags(df)
    assert result.loc[0, "is_stale"]


def test_missing_login_is_treated_as_stale():
    df = _make_df([
        {"username": "a", "department": "IT", "role": "Analyst", "status": "Active", "last_login": None}
    ])
    result = compute_risk_flags(df)
    assert result.loc[0, "is_stale"]


def test_stale_admin_is_high_risk():
    old = (datetime.utcnow() - timedelta(days=STALE_DAYS_THRESHOLD + 10)).strftime("%Y-%m-%d")
    df = _make_df([
        {"username": "a", "department": "IT", "role": "Domain Admin", "status": "Active", "last_login": old}
    ])
    result = compute_risk_flags(df)
    assert result.loc[0, "risk_flag"]


def test_stale_non_admin_is_not_high_risk():
    old = (datetime.utcnow() - timedelta(days=STALE_DAYS_THRESHOLD + 10)).strftime("%Y-%m-%d")
    df = _make_df([
        {"username": "a", "department": "IT", "role": "Support Tech", "status": "Active", "last_login": old}
    ])
    result = compute_risk_flags(df)
    assert not result.loc[0, "risk_flag"]


def test_active_admin_is_not_high_risk():
    recent = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    df = _make_df([
        {"username": "a", "department": "IT", "role": "Domain Admin", "status": "Active", "last_login": recent}
    ])
    result = compute_risk_flags(df)
    assert not result.loc[0, "risk_flag"]
