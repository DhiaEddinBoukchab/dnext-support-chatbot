"""
Retrieval Traces Viewer: display full RAG pipeline details for conversations
Shows: input query, retrieved chunks with distances, metadata, and final answer
"""

import json
import logging
from typing import List
import pandas as pd
import gradio as gr

from models import RetrievalTrace

logger = logging.getLogger(__name__)


def build_retrieval_traces_df(traces: List[dict]) -> pd.DataFrame:
    """Convert retrieval traces (with conversation details) to a DataFrame for display"""
    if not traces:
        return pd.DataFrame(columns=['Trace ID', 'Conversation ID', 'User', 'Query', 'Chunks', 'Type', 'Answer Preview', 'Timestamp'])
    
    rows = []
    for trace in traces:
        # Handle both RetrievalTrace objects and dict objects
        trace_id = trace.get('retrieval_trace_id') if isinstance(trace, dict) else trace.retrieval_trace_id
        conv_id = trace.get('conversation_id') if isinstance(trace, dict) else trace.conversation_id
        query = trace.get('query_input') if isinstance(trace, dict) else trace.query_input
        chunks = trace.get('num_chunks_retrieved') if isinstance(trace, dict) else trace.num_chunks_retrieved
        answer = trace.get('final_answer') if isinstance(trace, dict) else trace.final_answer
        timestamp = trace.get('timestamp') if isinstance(trace, dict) else trace.timestamp
        user_email = trace.get('email', 'Unknown') if isinstance(trace, dict) else 'Unknown'
        conv_type = trace.get('conversation_type', 'TECHNICAL') if isinstance(trace, dict) else 'TECHNICAL'
        
        answer_preview = answer[:80] + "..." if len(answer) > 80 else answer
        query_preview = query[:80] + "..." if len(query) > 80 else query
        
        # Format timestamp
        if isinstance(timestamp, str):
            ts_str = timestamp[:19]  # Take first 19 chars for datetime
        else:
            ts_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
        
        rows.append({
            'Trace ID': trace_id,
            'Conversation ID': conv_id,
            'User': user_email,
            'Query': query_preview,
            'Chunks': chunks,
            'Type': conv_type,
            'Answer Preview': answer_preview,
            'Timestamp': ts_str,
        })
    
    return pd.DataFrame(rows)


def format_chunks_display(chunks_json: str) -> str:
    """Format retrieved chunks JSON into readable markdown with distance metrics"""
    try:
        chunks = json.loads(chunks_json)
    except json.JSONDecodeError:
        return "❌ Error parsing chunks data"
    
    if not chunks:
        return "No chunks retrieved"
    
    md = "## Retrieved Chunks (Ranked by Distance/Score)\n\n"
    
    # Check if chunks include distance/score info for hybrid search metrics
    for i, chunk in enumerate(chunks, 1):
        md += f"### Chunk {i}\n"
        md += f"**Document:** {chunk.get('document', 'Unknown')}\n"
        md += f"**Section:** {chunk.get('section', 'Unknown')}\n"
        
        # Show distance metric
        distance = chunk.get('distance')
        if distance is not None:
            # Distance ranges from 0 (perfect match) to 1 (no match)
            quality = "🟢 Excellent" if distance < 0.3 else "🟡 Good" if distance < 0.6 else "🔴 Fair"
            md += f"**Distance (Similarity):** {distance:.3f} {quality}\n"
        md += f"**Distance:** {chunk.get('distance', 'N/A')}\n"
        md += f"\n{chunk.get('text', 'N/A')}\n\n"
        md += "---\n\n"
    
    return md


def build_retrieval_traces_tab():
    """🔬 Retrieval Traces tab components"""
    gr.Markdown("### Full RAG Pipeline Visibility")
    gr.Markdown(
        "View the complete retrieval pipeline for each conversation:\n"
        "- Input query\n"
        "- Retrieved chunks with similarity distances\n"
        "- Document and section metadata\n"
        "- Final AI response"
    )
    
    with gr.Group():
        gr.Markdown("#### Search Traces")
        with gr.Row():
            filter_mode = gr.Radio(
                choices=["View All", "By Session ID", "By User Email", "By Conversation ID"],
                value="View All",
                label="Filter Mode"
            )
        
        with gr.Row():
            session_id_input = gr.Textbox(
                label="Session ID",
                placeholder="Enter session ID",
                visible=False
            )
            user_email_input = gr.Textbox(
                label="User Email",
                placeholder="Enter user email",
                visible=False
            )
            conv_id_input = gr.Number(
                label="Conversation ID",
                precision=0,
                visible=False
            )
        
        search_btn = gr.Button("Search Traces")
    
    traces_table = gr.Dataframe(
        headers=['Trace ID', 'Conversation ID', 'User', 'Query', 'Chunks', 'Type', 'Answer Preview', 'Timestamp'],
        wrap=True,
        interactive=False,
    )
    
    gr.Markdown("### Detailed View - Full RAG Pipeline")
    with gr.Row():
        with gr.Column(scale=1):
            trace_id_input = gr.Number(label="Trace ID", precision=0, value=0)
        with gr.Column(scale=3):
            view_btn = gr.Button("View Full Details")
    
    # Conversation metadata
    with gr.Group():
        gr.Markdown("#### Conversation Metadata")
        with gr.Row():
            with gr.Column():
                conv_id_display = gr.Textbox(label="Conversation ID", interactive=False)
                user_display = gr.Textbox(label="User", interactive=False)
            with gr.Column():
                session_display = gr.Textbox(label="Session ID", interactive=False)
                conv_type_display = gr.Textbox(label="Type", interactive=False)
            with gr.Column():
                response_time_display = gr.Textbox(label="Response Time (ms)", interactive=False)
                timestamp_display = gr.Textbox(label="Timestamp", interactive=False)
    
    # Query and answer
    with gr.Row():
        with gr.Column():
            gr.Markdown("#### Input Query")
            query_display = gr.Textbox(label="Query", interactive=False, lines=4)
        
        with gr.Column():
            gr.Markdown("#### Final Answer (from LLM)")
            answer_display = gr.Textbox(label="Answer", interactive=False, lines=4)
    
    # Retrieved chunks with distances
    gr.Markdown("#### Retrieved Chunks with Similarity Distances")
    chunks_display = gr.Markdown("")
    
    return (filter_mode, session_id_input, user_email_input, conv_id_input,
            search_btn, traces_table, 
            trace_id_input, view_btn,
            conv_id_display, user_display, session_display, conv_type_display,
            response_time_display, timestamp_display,
            query_display, answer_display, chunks_display)


def create_traces_handlers(db):
    """Create event handlers for retrieval traces tab"""
    
    def search_traces(filter_mode, session_id, user_email, conv_id):
        """Search and display traces based on filter mode"""
        traces = []
        
        if filter_mode == "View All":
            traces = db.get_all_retrieval_traces(limit=100)
        elif filter_mode == "By Session ID":
            if not session_id or not session_id.strip():
                return pd.DataFrame(columns=['Trace ID', 'Conversation ID', 'User', 'Query', 'Chunks', 'Type', 'Answer Preview', 'Timestamp'])
            traces = db.get_retrieval_traces_by_session(session_id)
        elif filter_mode == "By User Email":
            if not user_email or not user_email.strip():
                return pd.DataFrame(columns=['Trace ID', 'Conversation ID', 'User', 'Query', 'Chunks', 'Type', 'Answer Preview', 'Timestamp'])
            # Get user by email
            user = db.get_user_by_email(user_email.strip())
            if not user:
                return pd.DataFrame(columns=['Trace ID', 'Conversation ID', 'User', 'Query', 'Chunks', 'Type', 'Answer Preview', 'Timestamp'])
            traces = db.get_retrieval_traces_by_user(user.user_id, limit=100)
        elif filter_mode == "By Conversation ID":
            if not conv_id or conv_id <= 0:
                return pd.DataFrame(columns=['Trace ID', 'Conversation ID', 'User', 'Query', 'Chunks', 'Type', 'Answer Preview', 'Timestamp'])
            trace_data = db.get_retrieval_trace_with_conversation(int(conv_id))
            if trace_data:
                traces = [trace_data]
        
        return build_retrieval_traces_df(traces)
    
    def view_trace_details(trace_id):
        """Display full details of a trace with all metadata"""
        if not trace_id or trace_id <= 0:
            empty_values = ("", "", "", "", "", "", "", "", "")
            return empty_values
        
        trace_data = db.get_retrieval_trace_with_conversation(int(trace_id))
        if not trace_data:
            empty_values = ("", "", "", "", "", "", "", "", "")
            return empty_values
        
        # Format all display fields
        conv_id_str = str(trace_data.get('conversation_id', ''))
        user_str = f"{trace_data.get('full_name', 'Unknown')} ({trace_data.get('email', 'Unknown')})"
        session_str = trace_data.get('session_id', '')
        type_str = trace_data.get('conversation_type', 'TECHNICAL')
        response_time_str = f"{trace_data.get('response_time_ms', 'N/A')} ms"
        timestamp_str = str(trace_data.get('timestamp', ''))[:19] if trace_data.get('timestamp') else ''
        
        query_str = trace_data.get('query_input', '')
        answer_str = trace_data.get('final_answer', '')
        chunks_md = format_chunks_display(trace_data.get('retrieved_chunks', '[]'))
        
        return (conv_id_str, user_str, session_str, type_str, response_time_str, 
                timestamp_str, query_str, answer_str, chunks_md)
    
    return search_traces, view_trace_details
