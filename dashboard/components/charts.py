"""
Chart components for the CAC Dashboard.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.colors import qualitative
import re

# Colorblind-safe palette (Okabe-Ito inspired)
COLOR_PALETTE = [
    "#0077BB",  # Blue
    "#33BBEE",  # Cyan
    "#009988",  # Teal
    "#EE7733",  # Orange
    "#CC3311",  # Red
    "#EE3377",  # Pink
    "#BBBBBB",  # Gray
    "#000000",  # Black
]

def sort_chamber_label(label):
    m = re.match(r'([a-z]+)(\d+)\.(\d+)', str(label))
    if m:
        return (m.group(1), int(m.group(2)), int(m.group(3)))
    return (label, 0, 0)

def extract_week_number(week_str):
    """Extract numeric week from string like 'S0', 'S13', etc."""
    if isinstance(week_str, str) and week_str.startswith("S"):
        return int(week_str[1:])
    return 0


def get_variable_columns(value_col):
    """
    Get the actual column names for a variable.
    Some variables have multiple replicate columns (e.g., ph_r1, ph_r2, ph_r3).
    """
    variable_map = {
        "ph": ["ph_r1", "ph_r2", "ph_r3"],
        "aw": ["aw_r1", "aw_r2", "aw_r3"],
        "moisture": ["moisture_r1", "moisture_r2", "moisture_r3"],
        "toughness": ["toughness_r1_kg", "toughness_r2_kg", "toughness_r3_kg", "toughness_r4_kg", "toughness_r5_kg"],
        "w_shear": ["w_shear_r1_kgmm", "w_shear_r2_kgmm", "w_shear_r3_kgmm", "w_shear_r4_kgmm", "w_shear_r5_kgmm"],
        "weight_loss_g": ["weight_loss_g"],
        "starch": ["starch_r1", "starch_r2", "starch_r3"],
        "fat": ["fat_r1", "fat_r2", "fat_r3"],
        "protein": ["protein_r1", "protein_r2", "protein_r3"],
        "ash": ["ash_r1", "ash_r2", "ash_r3"],
        "rotten_total": ["rotten_total"],
        "rotten_chestnuts_fungal": ["rotten_chestnuts_fungal"],
        "rotten_chestnuts_larva": ["rotten_chestnuts_larva"],
    }
    return variable_map.get(value_col, [value_col])


def melt_variable_data(df, value_col):
    """
    Melt replicate columns into long format for a given variable.
    Returns dataframe with columns: sample_id, chamber_label, week, gas_mix, space_type, group, variable_value
    """
    cols = get_variable_columns(value_col)
    existing_cols = [c for c in cols if c in df.columns]

    if not existing_cols:
        return pd.DataFrame()

    # Melt the replicate columns
    id_vars = ["sample_id", "chamber_label", "week", "gas_mix", "space_type", "group"]
    melt_df = df.melt(
        id_vars=id_vars,
        value_vars=existing_cols,
        var_name="replicate",
        value_name="value",
    )

    # Drop null values
    melt_df = melt_df[melt_df["value"].notna()]

    return melt_df


def create_heatmap(df, value_col):
    """
    Create heatmap: chamber_label × week, color = selected variable value.
    """
    melt_df = melt_variable_data(df, value_col)

    if melt_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)

    # Pivot for heatmap
    pivot_df = melt_df.pivot_table(
        index="chamber_label",
        columns="week",
        values="value",
        aggfunc="mean",
    )

    # Sort weeks properly
    week_order = sorted(pivot_df.columns, key=extract_week_number)
    pivot_df = pivot_df[week_order]

    # Sort chambers
    chamber_order = sorted(pivot_df.index, key=sort_chamber_label)
    pivot_df = pivot_df.loc[chamber_order]

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale="Viridis",
            hovertemplate="Chamber: %{y}<br>Week: %{x}<br>Value: %{z:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Heatmap: Chambers × Weeks",
        xaxis_title="Week",
        yaxis_title="Chamber",
        height=800,
    )

    return fig


def create_temporal_line_chart(df, value_col, error_type="sd", show_boxplot=False):
    """
    Create line chart with mean ± error band.

    Args:
        df: Filtered dataframe
        value_col: Variable column name
        error_type: 'sd' for standard deviation, 'ci' for 95% CI
        show_boxplot: If True, show boxplot of all chambers pooled per week
    """
    melt_df = melt_variable_data(df, value_col)

    if melt_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)

    if show_boxplot:
        # Boxplot mode: all 32 chambers pooled per week
        fig = px.box(
            melt_df,
            x="week",
            y="value",
            color="chamber_label",
            title="Distribution Across All Chambers (Pooled)",
            labels={"week": "Week", "value": value_col},
        )
        fig.update_layout(
            height=800,
            showlegend=False,
            xaxis_title="Week",
            yaxis_title=value_col,
        )
        # Sort weeks
        week_order = sorted(melt_df["week"].unique(), key=extract_week_number)
        fig.update_xaxes(categoryorder="array", categoryarray=week_order)
        return fig

    # Line chart mode: mean ± error band per chamber
    # Group by chamber and week
    grouped = melt_df.groupby(["chamber_label", "week"])["value"]

    agg_df = grouped.agg(["mean", "std", "count"]).reset_index()
    agg_df = agg_df[agg_df["count"] >= 1]  # Keep weeks with data

    if agg_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)

    # Calculate error
    if error_type == "ci":
        # 95% CI = 1.96 * SD / sqrt(n)
        agg_df["error"] = 1.96 * agg_df["std"] / np.sqrt(agg_df["count"].replace(0, np.nan))
    else:
        # SD
        agg_df["error"] = agg_df["std"].fillna(0)

    # Sort weeks
    agg_df["week_num"] = agg_df["week"].apply(extract_week_number)
    agg_df = agg_df.sort_values("week_num")

    chambers = sorted(agg_df["chamber_label"].unique(), key=sort_chamber_label)
    fig = go.Figure()

    for i, chamber in enumerate(chambers):
        chamber_data = agg_df[agg_df["chamber_label"] == chamber]
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

        # Main line
        fig.add_trace(
            go.Scatter(
                x=chamber_data["week"],
                y=chamber_data["mean"],
                name=chamber,
                mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=6),
                legendgroup=chamber,
                showlegend=True,
            )
        )

        # Error band (upper + lower)
        upper = chamber_data["mean"] + chamber_data["error"]
        lower = chamber_data["mean"] - chamber_data["error"]

        fig.add_trace(
            go.Scatter(
                x=pd.concat([chamber_data["week"], chamber_data["week"].iloc[::-1]]),
                y=pd.concat([upper, lower.iloc[::-1]]),
                fill="toself",
                fillcolor=color,
                opacity=0.2,
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                showlegend=False,
                legendgroup=chamber,
                name=f"{chamber} error",
            )
        )

    fig.update_layout(
        title="Temporal Evolution: Mean ± " + ("95% CI" if error_type == "ci" else "SD"),
        xaxis_title="Week",
        yaxis_title=value_col,
        height=800,
        legend_title="Chamber",
        hovermode="x unified",
    )

    # Sort x-axis
    week_order = sorted(agg_df["week"].unique(), key=extract_week_number)
    fig.update_xaxes(categoryorder="array", categoryarray=week_order)

    return fig


def create_replicate_comparison_chart(df, value_col):
    """
    Create chart comparing replicates by shared gas_mix.
    Shows two lines side by side for chambers with the same gas_mix.
    """
    melt_df = melt_variable_data(df, value_col)

    if melt_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)

    # Group by gas_mix and week
    grouped = melt_df.groupby(["gas_mix", "chamber_label", "week"])["value"].mean().reset_index()

    if grouped.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)

    # Sort weeks
    grouped["week_num"] = grouped["week"].apply(extract_week_number)
    grouped = grouped.sort_values(["gas_mix", "week_num"])

    fig = go.Figure()

    gas_mixes = grouped["gas_mix"].unique()

    for i, gas_mix in enumerate(gas_mixes):
        gm_data = grouped[grouped["gas_mix"] == gas_mix]
        chambers = gm_data["chamber_label"].unique()
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

        for j, chamber in enumerate(chambers):
            chamber_data = gm_data[gm_data["chamber_label"] == chamber]

            # Dash pattern for replicates
            dash = "solid" if j == 0 else "dash"

            fig.add_trace(
                go.Scatter(
                    x=chamber_data["week"],
                    y=chamber_data["value"],
                    name=f"{chamber} ({gas_mix})",
                    mode="lines+markers",
                    line=dict(color=color, width=2, dash=dash),
                    marker=dict(size=6),
                    showlegend=True,
                )
            )

    fig.update_layout(
        title="Replicate Comparison by Gas Mix",
        xaxis_title="Week",
        yaxis_title=value_col,
        height=800,
        legend_title="Chamber (Gas Mix)",
        hovermode="x unified",
    )

    week_order = sorted(grouped["week"].unique(), key=extract_week_number)
    fig.update_xaxes(categoryorder="array", categoryarray=week_order)

    return fig


def create_rot_analysis_chart(df, rot_col):
    """
    Create line + bar chart for rot variables.
    """
    # Filter to relevant columns
    rot_data = df[["chamber_label", "week", rot_col]].copy()
    rot_data = rot_data[rot_data[rot_col].notna()]

    if rot_data.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)

    # Sort weeks
    rot_data["week_num"] = rot_data["week"].apply(extract_week_number)
    rot_data = rot_data.sort_values("week_num")

    # Aggregate by week (sum for rot counts)
    weekly_rot = rot_data.groupby("week")[rot_col].sum().reset_index()

    # Also create per-chamber lines
    fig = go.Figure()

    chambers = sorted(rot_data["chamber_label"].unique(), key=sort_chamber_label)

    # Bar chart for weekly totals
    fig.add_trace(
        go.Bar(
            x=weekly_rot["week"],
            y=weekly_rot[rot_col],
            name="Weekly Total",
            marker_color="#666666",
            opacity=0.5,
            yaxis="y2",
        )
    )

    # Line charts per chamber
    for i, chamber in enumerate(chambers):
        chamber_data = rot_data[rot_data["chamber_label"] == chamber]
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

        fig.add_trace(
            go.Scatter(
                x=chamber_data["week"],
                y=chamber_data[rot_col],
                name=chamber,
                mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=6),
            )
        )

    fig.update_layout(
        title=f"Rot Analysis: {rot_col.replace('_', ' ').title()}",
        xaxis_title="Week",
        yaxis=dict(title="Count per Chamber", domain=[0, 1]),
        yaxis2=dict(title="Weekly Total (Sum all chambers)", overlaying="y", side="right"),
        height=800,
        legend_title="Chamber",
        barmode="overlay",
        legend=dict(x=1.12),
        margin=dict(r=120),
    )

    week_order = sorted(rot_data["week"].unique(), key=extract_week_number)
    fig.update_xaxes(categoryorder="array", categoryarray=week_order)

    return fig


def create_macronutrient_chart(df, value_col, show_individual=False):
    """
    Create grouped bar chart for macronutrients at T0/S13/S26 timepoints.
    """
    melt_df = melt_variable_data(df, value_col)

    if melt_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)

    # Identify macronutrient timepoints (weeks with data)
    weeks = melt_df["week"].unique()

    # Sort weeks
    week_order = sorted(weeks, key=extract_week_number)

    if show_individual:
        # Show individual replicates
        fig = px.bar(
            melt_df,
            x="week",
            y="value",
            color="chamber_label",
            barmode="group",
            title=f"{value_col.replace('_', ' ').title()} by Chamber and Week",
            labels={"week": "Week", "value": value_col},
        )
    else:
        # Show mean with error bars
        grouped = melt_df.groupby(["chamber_label", "week"])["value"].agg(["mean", "std", "count"]).reset_index()
        grouped["se"] = grouped["std"] / np.sqrt(grouped["count"])

        fig = go.Figure()

        chambers = grouped["chamber_label"].unique()

        for i, chamber in enumerate(chambers):
            chamber_data = grouped[grouped["chamber_label"] == chamber]
            color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

            fig.add_trace(
                go.Bar(
                    x=chamber_data["week"],
                    y=chamber_data["mean"],
                    name=chamber,
                    error_y=dict(type="data", symmetric=True, array=chamber_data["se"]),
                    marker_color=color,
                )
            )

    fig.update_layout(
        xaxis_title="Week",
        yaxis_title=value_col,
        height=800,
        legend_title="Chamber",
    )

    fig.update_xaxes(categoryorder="array", categoryarray=week_order)

    return fig


def create_data_table(df, value_col):
    """
    Create filtered data table with statistical summary.
    """
    melt_df = melt_variable_data(df, value_col)

    if melt_df.empty:
        return None, "No data available"

    # Statistical summary grouped by chamber_label
    summary = melt_df.groupby("chamber_label")["value"].agg(
        [
            ("n", "count"),
            ("mean", "mean"),
            ("sd", "std"),
            ("cv_pct", lambda x: x.std() / x.mean() * 100 if x.mean() != 0 else None),
            ("min", "min"),
            ("max", "max"),
            ("median", "median"),
        ]
    ).reset_index()

    # Format for display
    summary["cv_pct"] = summary["cv_pct"].round(2)
    summary["mean"] = summary["mean"].round(4)
    summary["sd"] = summary["sd"].round(4)
    summary["min"] = summary["min"].round(4)
    summary["max"] = summary["max"].round(4)
    summary["median"] = summary["median"].round(4)

    return summary, None
