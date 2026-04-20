"""
Filter components for the CAC Dashboard topbar.
"""
import dash_bootstrap_components as dbc
from dash import dcc, html


def create_variable_dropdown(df):
    """Create dropdown for selecting physicochemical variables."""
    # Define variable groups
    physicochemical_vars = [
        # Weekly variables
        {"label": "pH", "value": "ph"},
        {"label": "Water Activity (aw)", "value": "aw"},
        {"label": "Moisture (%)", "value": "moisture"},
        {"label": "Toughness (kg)", "value": "toughness"},
        {"label": "Work of Shear (kg·mm)", "value": "w_shear"},
        {"label": "Weight Loss (g)", "value": "weight_loss_g"},
        # Macronutrients (measured at T0, S13, S26)
        {"label": "Starch (%)", "value": "starch"},
        {"label": "Fat (%)", "value": "fat"},
        {"label": "Protein (%)", "value": "protein"},
        {"label": "Ash (%)", "value": "ash"},
        # Rot variables
        {"label": "Rotten Total", "value": "rotten_total"},
        {"label": "Rotten - Fungal", "value": "rotten_chestnuts_fungal"},
        {"label": "Rotten - Larva", "value": "rotten_chestnuts_larva"},
    ]

    return dcc.Dropdown(
        id="variable-selector",
        options=physicochemical_vars,
        value="ph",
        clearable=False,
        style={"width": "200px", "display": "inline-block", "marginRight": "10px"},
    )


def create_chamber_dropdown(df):
    """Create multi-select dropdown for chamber labels."""
    chambers = sorted(df["chamber_label"].unique())

    return dcc.Dropdown(
        id="chamber-selector",
        options=[{"label": ch, "value": ch} for ch in chambers],
        value=chambers,  # Default: all chambers
        multi=True,
        clearable=True,
        style={"width": "250px", "display": "inline-block", "marginRight": "10px"},
        placeholder="Select chambers...",
    )


def create_gas_mix_dropdown(df):
    """Create multi-select dropdown for gas mix compositions."""
    gas_mixes = sorted(df["gas_mix"].dropna().unique())

    return dcc.Dropdown(
        id="gas-mix-selector",
        options=[{"label": gm, "value": gm} for gm in gas_mixes],
        value=gas_mixes,  # Default: all gas mixes
        multi=True,
        clearable=True,
        style={"width": "220px", "display": "inline-block", "marginRight": "10px"},
        placeholder="Select gas mix...",
    )


def create_space_type_dropdown(df):
    """Create multi-select dropdown for space types."""
    space_types = sorted(df["space_type"].dropna().unique())

    return dcc.Dropdown(
        id="space-type-selector",
        options=[{"label": st, "value": st} for st in space_types],
        value=space_types,  # Default: all space types
        multi=True,
        clearable=True,
        style={"width": "180px", "display": "inline-block", "marginRight": "10px"},
        placeholder="Select space type...",
    )


def create_week_range_slider(df):
    """Create range slider for week selection."""
    # Extract week number from week column (S0, S1, ... -> 0, 1, ...)
    weeks = df["week"].unique()
    week_numbers = []
    for w in weeks:
        if isinstance(w, str) and w.startswith("S"):
            week_numbers.append(int(w[1:]))
        else:
            week_numbers.append(0)

    min_week = min(week_numbers)
    max_week = max(week_numbers)

    return html.Div(
        dcc.RangeSlider(
            id="week-range-slider",
            min=min_week,
            max=max_week,
            value=[min_week, max_week],
            marks={i: f"S{i}" for i in range(min_week, max_week + 1, max(1, (max_week - min_week) // 10))},
            step=1,
            allowCross=False,
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        style={"width": "200px", "display": "inline-block", "marginRight": "10px"},
    )


def create_group_selector():
    """Create radio items for group selection (C, P, N, All)."""
    return dcc.RadioItems(
        id="group-selector",
        options=[
            {"label": "All", "value": "all"},
            {"label": "C (Controlled Atmosphere)", "value": "C"},
            {"label": "P (Positive Control)", "value": "P"},
            {"label": "N (Negative Control)", "value": "N"},
        ],
        value="all",
        inline=True,
        labelStyle={"marginRight": "15px"},
    )


def create_error_type_selector():
    """Create radio items for error type selection (SD vs CI)."""
    return dcc.RadioItems(
        id="error-type-selector",
        options=[
            {"label": "± SD", "value": "sd"},
            {"label": "95% CI", "value": "ci"},
        ],
        value="sd",
        inline=True,
        labelStyle={"marginRight": "15px"},
    )


def create_boxplot_toggle():
    """Create radio items for boxplot mode toggle."""
    return dcc.RadioItems(
        id="boxplot-toggle",
        options=[
            {"label": "Replicates", "value": "replicates"},
            {"label": "Boxplot (all chambers)", "value": "boxplot"},
        ],
        value="replicates",
        inline=True,
        labelStyle={"marginRight": "15px"},
    )


def create_macronutrient_toggle():
    """Create radio items for macronutrient display mode."""
    return dcc.RadioItems(
        id="macronutrient-toggle",
        options=[
            {"label": "Mean", "value": "mean"},
            {"label": "Individual Replicates", "value": "individual"},
        ],
        value="mean",
        inline=True,
        labelStyle={"marginRight": "15px"},
    )


def create_topbar_filters(df):
    """Create the complete topbar filter row."""
    return html.Div(
        [
            html.Div(
                [
                    html.Label("Variable:", style={"fontWeight": "bold", "marginRight": "5px"}),
                    create_variable_dropdown(df),
                    html.Label("Chambers:", style={"fontWeight": "bold", "marginRight": "5px"}),
                    create_chamber_dropdown(df),
                ],
                style={"marginBottom": "10px"},
            ),
            html.Div(
                [
                    html.Label("Gas Mix:", style={"fontWeight": "bold", "marginRight": "5px"}),
                    create_gas_mix_dropdown(df),
                    html.Label("Space Type:", style={"fontWeight": "bold", "marginRight": "5px"}),
                    create_space_type_dropdown(df),
                ],
                style={"marginBottom": "10px"},
            ),
            html.Div(
                [
                    html.Label("Week Range:", style={"fontWeight": "bold", "marginRight": "5px"}),
                    create_week_range_slider(df),
                    html.Label("Group:", style={"fontWeight": "bold", "marginRight": "5px"}),
                    create_group_selector(),
                ],
                style={"marginBottom": "10px"},
            ),
        ],
        style={
            "backgroundColor": "#f8f9fa",
            "padding": "15px",
            "borderRadius": "5px",
            "marginBottom": "20px",
            "border": "1px solid #dee2e6",
        },
    )
