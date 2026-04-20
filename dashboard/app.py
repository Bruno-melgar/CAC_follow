"""
CAC Dashboard - Plotly Dash application for chestnut controlled atmosphere chamber visualization.
"""
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import os

# Import components and callbacks
from components.filters import (
    create_topbar_filters,
    create_error_type_selector,
    create_boxplot_toggle,
    create_macronutrient_toggle,
)
from components.kpi_cards import create_kpi_row
from callbacks.callbacks import register_callbacks


# Load data at startup
# Use relative path for Render compatibility
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "cac_clean.csv")
df = pd.read_csv(DATA_PATH)

# Ensure week is treated as ordered categorical
week_order = [f"S{i}" for i in range(27)]  # S0 to S26
df["week"] = pd.Categorical(df["week"], categories=week_order, ordered=True)


# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)
app.title = "CAC Dashboard - Chestnut Storage Experiment"

# Define the layout
app.layout = dbc.Container(
    [
        # Hidden store for filtered data
        dcc.Store(id="filtered-data-store", data=None),

        # Download component
        dcc.Download(id="download-data"),

        # Header
        html.Div(
            [
                html.H1("CAC Dashboard", className="mb-1"),
                html.P(
                    "Chestnut Controlled Atmosphere Chamber Experiment Visualization",
                    className="mb-0",
                ),
            ],
            className="dashboard-header",
        ),

        # Topbar filters
        create_topbar_filters(df),

        # Tabs
        dbc.Tabs(
            [
                # Tab 1: Overview
                dbc.Tab(
                    [
                        html.Div(id="overview-kpi-row", className="mt-4"),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Chamber × Week Heatmap", className="card-subtitle mb-3"),
                                    dcc.Graph(id="overview-heatmap"),
                                ]
                            ),
                            className="chart-container",
                        ),
                    ],
                    label="Overview",
                    tab_id="tab-overview",
                ),

                # Tab 2: Temporal Evolution
                dbc.Tab(
                    [
                        html.Div(id="temporal-kpi-row", className="mt-4"),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.Label("Error Type: ", style={"fontWeight": "bold", "marginRight": "10px"}),
                                            create_error_type_selector(),
                                            html.Label("Display Mode: ", style={"fontWeight": "bold", "marginRight": "10px", "marginLeft": "20px"}),
                                            create_boxplot_toggle(),
                                        ],
                                        style={"marginBottom": "15px"},
                                    ),
                                    dcc.Graph(id="temporal-line-chart"),
                                ]
                            ),
                            className="chart-container",
                        ),
                    ],
                    label="Temporal Evolution",
                    tab_id="tab-temporal",
                ),

                # Tab 3: Replicate Comparison
                dbc.Tab(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Replicate Comparison by Gas Mix", className="card-subtitle mb-3"),
                                    html.P(
                                        "Chambers sharing the same gas_mix composition are shown with the same color. "
                                        "Solid lines = first replicate, dashed lines = second replicate.",
                                        className="text-muted mb-3",
                                    ),
                                    dcc.Graph(id="replicate-comparison-chart"),
                                ]
                            ),
                            className="chart-container",
                        ),
                    ],
                    label="Replicate Comparison",
                    tab_id="tab-replicate",
                ),

                # Tab 4: Rot Analysis
                dbc.Tab(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Fungal Rot", className="card-subtitle mb-3"),
                                                dcc.Graph(id="rot-fungal-chart"),
                                            ]
                                        ),
                                        className="chart-container",
                                    ),
                                    xs=12,
                                    md=6,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Larva Rot", className="card-subtitle mb-3"),
                                                dcc.Graph(id="rot-larva-chart"),
                                            ]
                                        ),
                                        className="chart-container",
                                    ),
                                    xs=12,
                                    md=6,
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    label="Rot Analysis",
                    tab_id="tab-rot",
                ),

                # Tab 5: Macronutrients
                dbc.Tab(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.Label("Display: ", style={"fontWeight": "bold", "marginRight": "10px"}),
                                            create_macronutrient_toggle(),
                                        ],
                                        style={"marginBottom": "15px"},
                                    ),
                                    html.H5("Macronutrient Analysis (T0, S13, S26)", className="card-subtitle mb-3"),
                                    html.P(
                                        "Macronutrients (starch, fat, protein, ash) are measured only at specific timepoints.",
                                        className="text-muted mb-3",
                                    ),
                                    dcc.Graph(id="macronutrient-chart"),
                                ]
                            ),
                            className="chart-container",
                        ),
                    ],
                    label="Macronutrients",
                    tab_id="tab-macro",
                ),

                # Tab 6: Data Table
                dbc.Tab(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button(
                                        "Download Filtered Data (CSV)",
                                        id="download-button",
                                        color="primary",
                                        className="mb-3",
                                    ),
                                    xs=12,
                                    md=3,
                                ),
                            ],
                            className="mb-3",
                        ),
                        html.Div(id="data-table-container"),
                    ],
                    label="Data Table",
                    tab_id="tab-data",
                ),
            ],
            id="dashboard-tabs",
            active_tab="tab-overview",
        ),

        # Latest week display (hidden but used by callbacks)
        html.Div(
            [
                html.Label("Latest Week: ", style={"fontWeight": "bold"}),
                html.Span(id="latest-week-display"),
            ],
            style={"display": "none"},
        ),

        # Footer
        html.Footer(
            [
                html.P(
                    "CAC Dashboard | Chestnut Controlled Atmosphere Storage Experiment",
                    className="text-center text-muted",
                ),
            ],
            className="dashboard-footer",
        ),
    ],
    fluid=True,
    className="py-4",
)


# Register callbacks
register_callbacks(app, df)


# Expose server for WSGI (gunicorn/Render)
server = app.server

# Run the app
if __name__ == "__main__":
    # Use environment variables for Render compatibility
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
