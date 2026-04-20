"""
Callback functions for the CAC Dashboard.
"""
import pandas as pd
from dash import Input, Output, State, callback
from dash import dcc, html
import dash_bootstrap_components as dbc

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.filters import create_topbar_filters
from components.kpi_cards import create_kpi_row
from components.charts import (
    create_heatmap,
    create_temporal_line_chart,
    create_replicate_comparison_chart,
    create_rot_analysis_chart,
    create_macronutrient_chart,
    create_data_table,
    get_variable_columns,
)


def register_callbacks(app, df):
    """Register all callbacks with the Dash app."""

    @app.callback(
        [
            Output("filtered-data-store", "data"),
            Output("latest-week-display", "children"),
        ],
        [
            Input("chamber-selector", "value"),
            Input("gas-mix-selector", "value"),
            Input("space-type-selector", "value"),
            Input("week-range-slider", "value"),
            Input("group-selector", "value"),
        ],
    )
    def update_filtered_data(chambers, gas_mixes, space_types, week_range, group):
        """Filter the dataframe based on topbar selections."""
        filtered_df = df.copy()

        # Filter by chambers
        if chambers:
            filtered_df = filtered_df[filtered_df["chamber_label"].isin(chambers)]

        # Filter by gas mix
        if gas_mixes:
            filtered_df = filtered_df[filtered_df["gas_mix"].isin(gas_mixes)]

        # Filter by space type
        if space_types:
            filtered_df = filtered_df[filtered_df["space_type"].isin(space_types)]

        # Filter by week range
        if week_range and len(week_range) == 2:
            def extract_week(week_str):
                if isinstance(week_str, str) and week_str.startswith("S"):
                    return int(week_str[1:])
                return 0

            filtered_df["week_num"] = filtered_df["week"].apply(extract_week)
            filtered_df = filtered_df[
                (filtered_df["week_num"] >= week_range[0])
                & (filtered_df["week_num"] <= week_range[1])
            ]
            filtered_df = filtered_df.drop(columns=["week_num"])

        # Filter by group
        if group and group != "all":
            filtered_df = filtered_df[filtered_df["group"] == group]

        # Determine latest week in filtered data
        weeks = filtered_df["week"].unique()
        week_numbers = []
        for w in weeks:
            if isinstance(w, str) and w.startswith("S"):
                week_numbers.append(int(w[1:]))
        latest_week = f"S{max(week_numbers)}" if week_numbers else "N/A"

        return filtered_df.to_json(date_format="iso", orient="split"), latest_week

    @app.callback(
        Output("overview-kpi-row", "children"),
        [
            Input("filtered-data-store", "data"),
            Input("variable-selector", "value"),
            Input("latest-week-display", "children"),
        ],
    )
    def update_overview_kpis(filtered_json, value_col, latest_week):
        """Update KPI cards for Overview tab."""
        if not filtered_json:
            return html.Div("No data available")

        filtered_df = pd.read_json(filtered_json, orient="split")
        return create_kpi_row(filtered_df, value_col, latest_week)

    @app.callback(
        Output("overview-heatmap", "figure"),
        [
            Input("filtered-data-store", "data"),
            Input("variable-selector", "value"),
        ],
    )
    def update_overview_heatmap(filtered_json, value_col):
        """Update heatmap for Overview tab."""
        if not filtered_json:
            return create_heatmap(pd.DataFrame(), value_col)

        filtered_df = pd.read_json(filtered_json, orient="split")
        return create_heatmap(filtered_df, value_col)

    @app.callback(
        Output("temporal-kpi-row", "children"),
        [
            Input("filtered-data-store", "data"),
            Input("variable-selector", "value"),
            Input("latest-week-display", "children"),
        ],
    )
    def update_temporal_kpis(filtered_json, value_col, latest_week):
        """Update KPI cards for Temporal Evolution tab."""
        if not filtered_json:
            return html.Div("No data available")

        filtered_df = pd.read_json(filtered_json, orient="split")
        return create_kpi_row(filtered_df, value_col, latest_week)

    @app.callback(
        Output("temporal-line-chart", "figure"),
        [
            Input("filtered-data-store", "data"),
            Input("variable-selector", "value"),
            Input("error-type-selector", "value"),
            Input("boxplot-toggle", "value"),
        ],
    )
    def update_temporal_chart(filtered_json, value_col, error_type, boxplot_mode):
        """Update temporal evolution line chart."""
        if not filtered_json:
            return create_temporal_line_chart(pd.DataFrame(), value_col)

        filtered_df = pd.read_json(filtered_json, orient="split")
        show_boxplot = boxplot_mode == "boxplot"
        return create_temporal_line_chart(
            filtered_df, value_col, error_type=error_type, show_boxplot=show_boxplot
        )

    @app.callback(
        Output("replicate-comparison-chart", "figure"),
        [
            Input("filtered-data-store", "data"),
            Input("variable-selector", "value"),
        ],
    )
    def update_replicate_chart(filtered_json, value_col):
        """Update replicate comparison chart."""
        if not filtered_json:
            return create_replicate_comparison_chart(pd.DataFrame(), value_col)

        filtered_df = pd.read_json(filtered_json, orient="split")
        return create_replicate_comparison_chart(filtered_df, value_col)

    @app.callback(
        Output("rot-fungal-chart", "figure"),
        [
            Input("filtered-data-store", "data"),
        ],
    )
    def update_rot_fungal_chart(filtered_json):
        """Update rot fungal chart."""
        if not filtered_json:
            return create_rot_analysis_chart(pd.DataFrame(), "rotten_chestnuts_fungal")

        filtered_df = pd.read_json(filtered_json, orient="split")
        return create_rot_analysis_chart(filtered_df, "rotten_chestnuts_fungal")

    @app.callback(
        Output("rot-larva-chart", "figure"),
        [
            Input("filtered-data-store", "data"),
        ],
    )
    def update_rot_larva_chart(filtered_json):
        """Update rot larva chart."""
        if not filtered_json:
            return create_rot_analysis_chart(pd.DataFrame(), "rotten_chestnuts_larva")

        filtered_df = pd.read_json(filtered_json, orient="split")
        return create_rot_analysis_chart(filtered_df, "rotten_chestnuts_larva")

    @app.callback(
        Output("macronutrient-chart", "figure"),
        [
            Input("filtered-data-store", "data"),
            Input("variable-selector", "value"),
            Input("macronutrient-toggle", "value"),
        ],
    )
    def update_macronutrient_chart(filtered_json, value_col, show_individual):
        """Update macronutrient chart."""
        if not filtered_json:
            return create_macronutrient_chart(pd.DataFrame(), value_col)

        filtered_df = pd.read_json(filtered_json, orient="split")
        show_ind = show_individual == "individual"
        return create_macronutrient_chart(filtered_df, value_col, show_individual=show_ind)

    @app.callback(
        Output("data-table-container", "children"),
        [
            Input("filtered-data-store", "data"),
            Input("variable-selector", "value"),
        ],
    )
    def update_data_table(filtered_json, value_col):
        """Update data table and statistical summary."""
        if not filtered_json:
            return html.Div("No data available")

        filtered_df = pd.read_json(filtered_json, orient="split")
        summary, error = create_data_table(filtered_df, value_col)

        if error:
            return html.Div(error)

        # Create DataTable with export
        table = dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Statistical Summary by Chamber", className="card-subtitle mb-3"),
                    dbc.Table.from_dataframe(
                        summary,
                        striped=True,
                        bordered=True,
                        hover=True,
                        responsive=True,
                    ),
                ]
            ),
            className="mb-4",
        )

        return table

    @app.callback(
        Output("download-data", "data"),
        [
            Input("download-button", "n_clicks"),
            Input("filtered-data-store", "data"),
            Input("variable-selector", "value"),
        ],
        prevent_initial_call=True,
    )
    def download_csv(n_clicks, filtered_json, value_col):
        """Download filtered data as CSV."""
        if not n_clicks or not filtered_json:
            return None

        filtered_df = pd.read_json(filtered_json, orient="split")

        # Get relevant columns for the selected variable
        cols = get_variable_columns(value_col)
        existing_cols = [c for c in cols if c in filtered_df.columns]

        # Select key columns
        display_cols = ["sample_id", "chamber_label", "week", "gas_mix", "space_type"] + existing_cols
        display_cols = [c for c in display_cols if c in filtered_df.columns]

        export_df = filtered_df[display_cols]

        return dcc.send_data_frame(export_df.to_csv, "filtered_data.csv", index=False)
