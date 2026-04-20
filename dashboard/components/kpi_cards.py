"""
KPI Card components for the CAC Dashboard.
"""
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.charts import get_variable_columns


def calculate_kpis(df, value_col, latest_week=None):
    cols = get_variable_columns(value_col)
    existing_cols = [c for c in cols if c in df.columns]

    if not existing_cols:
        return {"mean": None, "sd": None, "cv": None, "n_samples": 0, "pct_rotten": None}

    values = df[existing_cols].values.flatten()
    values = values[~np.isnan(values.astype(float))]

    if len(values) == 0:
        return {"mean": None, "sd": None, "cv": None, "n_samples": 0, "pct_rotten": None}

    mean_val = np.mean(values)
    sd_val = np.std(values, ddof=1)
    n_samples = len(values)
    cv = (sd_val / mean_val * 100) if mean_val != 0 else None

    pct_rotten = None
    if latest_week is not None and "rotten_total" in df.columns:
        latest_data = df[df["week"] == latest_week]
        if len(latest_data) > 0 and "total_chestnuts" in df.columns:
            total_chestnuts = latest_data["total_chestnuts"].sum()
            total_rotten = latest_data["rotten_total"].sum()
            if total_chestnuts > 0:
                pct_rotten = (total_rotten / total_chestnuts) * 100

    return {"mean": mean_val, "sd": sd_val, "cv": cv, "n_samples": n_samples, "pct_rotten": pct_rotten}


def create_kpi_card(title, value, unit="", color="primary"):
    if value is None:
        value_display = "N/A"
    elif isinstance(value, float):
        value_display = f"{value:.2f}{unit}"
    else:
        value_display = f"{value}{unit}"

    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-subtitle text-muted"),
            html.H4(value_display, className="card-text"),
        ]),
        color=color,
        inverse=(color == "primary"),
        className="mb-3",
    )


def create_kpi_row(df, value_col, latest_week=None):
    kpis = calculate_kpis(df, value_col, latest_week)

    mean_sd = f"{kpis['mean']:.2f} ± {kpis['sd']:.2f}" if kpis["mean"] is not None else "N/A"
    cv_display = f"{kpis['cv']:.1f}%" if kpis["cv"] is not None else "N/A"
    rotten_display = f"{kpis['pct_rotten']:.1f}%" if kpis["pct_rotten"] is not None else "N/A"

    return dbc.Row([
        dbc.Col(create_kpi_card("Mean ± SD", mean_sd, color="primary"), xs=12, sm=6, md=3),
        dbc.Col(create_kpi_card("CV%", cv_display, color="secondary"), xs=12, sm=6, md=3),
        dbc.Col(create_kpi_card("% Rotten (latest)", rotten_display, color="warning"), xs=12, sm=6, md=3),
        dbc.Col(create_kpi_card("N Samples", kpis["n_samples"], color="info"), xs=12, sm=6, md=3),
    ], className="mb-4")