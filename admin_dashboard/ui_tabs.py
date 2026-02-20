"""
UI tab builders: each function returns the Gradio components for one tab.
Called by ui_builder.py to compose the full dashboard layout.
"""

import pandas as pd
import gradio as gr


def build_stats_tab():
    """📊 Statistics tab components."""
    stats_display    = gr.Markdown("")
    stats_timeseries = gr.LinePlot(
        value=pd.DataFrame({"date": [], "conversations": []}),
        x="date", y="conversations",
        title="Conversations per day (last 14 days)",
    )
    refresh_btn = gr.Button("🔄 Refresh Statistics")
    return stats_display, stats_timeseries, refresh_btn


def build_users_tab():
    """👥 Users tab components."""
    users_table = gr.Dataframe(
        headers=['ID', 'Email', 'Name', 'Status', 'Total Queries', 'Created', 'Last Login'],
        wrap=True,
    )
    refresh_btn = gr.Button("🔄 Refresh Users")

    gr.Markdown("### User Management")
    with gr.Row():
        user_id_input     = gr.Number(label="User ID", precision=0)
        user_status_input = gr.Dropdown(
            choices=["active", "inactive", "blocked"], label="New Status"
        )
    update_btn    = gr.Button("Update Status")
    status_msg    = gr.Markdown("")
    return users_table, refresh_btn, user_id_input, user_status_input, update_btn, status_msg


def build_user_details_tab():
    """🔍 User Details tab components."""
    detail_user_id = gr.Number(label="User ID", precision=0)
    get_btn        = gr.Button("Get Details")
    details_md     = gr.Markdown("")
    gr.Markdown("### User's Conversation History")
    convs_table = gr.Dataframe(
        headers=['ID', 'User ID', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)'],
        wrap=True,
    )
    return detail_user_id, get_btn, details_md, convs_table


def build_live_monitor_tab():
    """📡 Live Monitor tab components."""
    gr.Markdown(
        "Real-time view of the latest conversations. "
        "Enable auto-refresh to monitor activity while the chatbot is running."
    )
    live_table   = gr.Dataframe(
        headers=['ID', 'User', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)'],
        wrap=True,
    )
    last_refresh = gr.Markdown("")
    gallery      = gr.Gallery(label="Recent images", columns=4, rows=1, height="auto")
    with gr.Row():
        auto_toggle  = gr.Checkbox(value=True, label="Auto-refresh every 5 seconds")
        refresh_btn  = gr.Button("Refresh now")
    timer = gr.Timer(value=5.0, active=True)
    return live_table, last_refresh, gallery, auto_toggle, refresh_btn, timer


def build_conversations_tab():
    """💬 Conversations & Export tab components."""
    gr.Markdown("Filter and export conversations for offline analysis.")
    with gr.Row():
        filter_email = gr.Textbox(label="User email contains",       placeholder="user@domain.com (optional)")
        filter_from  = gr.Textbox(label="From date (YYYY-MM-DD)",    placeholder="2026-01-01 (optional)")
        filter_to    = gr.Textbox(label="To date (YYYY-MM-DD)",      placeholder="2026-12-31 (optional)")
        filter_type  = gr.Dropdown(choices=["", "TECHNICAL", "CASUAL"], label="Conversation type", value="")
    with gr.Row():
        apply_btn  = gr.Button("Apply filters")
        export_btn = gr.Button("Export to CSV")
    convs_table   = gr.Dataframe(
        headers=['ID', 'User', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)'],
        wrap=True,
    )
    export_status = gr.Markdown("")
    export_file   = gr.File(label="Download CSV", interactive=False)
    return filter_email, filter_from, filter_to, filter_type, apply_btn, export_btn, convs_table, export_status, export_file