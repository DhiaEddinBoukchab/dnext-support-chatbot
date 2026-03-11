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


def build_retrieval_traces_df(traces: List[RetrievalTrace]) -> pd.DataFrame:
    """Convert retrieval traces to a DataFrame for display"""
    if not traces:
        return pd.DataFrame(columns=['ID', 'Query', 'Chunks', 'Answer Preview', 'Retrieved', 'Timestamp'])
    
    rows = []
    for trace in traces:
        answer_preview = trace.final_answer[:100] + "..." if len(trace.final_answer) > 100 else trace.final_answer
        rows.append({
            'ID': trace.retrieval_trace_id,
            'Query': trace.query_input[:80] + "..." if len(trace.query_input) > 80 else trace.query_input,
            'Chunks': trace.num_chunks_retrieved,
            'Answer Preview': answer_preview,
            'Timestamp': trace.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return pd.DataFrame(rows)


def format_chunks_display(chunks_json: str) -> str:
    """Format retrieved chunks JSON into readable markdown"""
    try:
        chunks = json.loads(chunks_json)
    except json.JSONDecodeError:
        return "❌ Error parsing chunks data"
    
    if not chunks:
        return "No chunks retrieved"
    
    md = "## Retrieved Chunks\n\n"
    for i, chunk in enumerate(chunks, 1):
        md += f"### Chunk {i}\n"
        md += f"**Document:** {chunk.get('document', 'Unknown')}\n"
        md += f"**Section:** {chunk.get('section', 'Unknown')}\n"
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
    
    with gr.Row():
        session_id_input = gr.Textbox(label="Session ID", placeholder="Enter session ID to view traces")
        search_btn = gr.Button("Search Traces")
    
    traces_table = gr.Dataframe(
        headers=['ID', 'Query', 'Chunks', 'Answer Preview', 'Timestamp'],
        wrap=True,
    )
    
    gr.Markdown("### Detailed View")
    trace_id_input = gr.Number(label="Trace ID", precision=0)
    view_btn = gr.Button("View Full Details")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("#### Input Query")
            query_display = gr.Textbox(label="Query", interactive=False, lines=3)
        
        with gr.Column():
            gr.Markdown("#### Final Answer")
            answer_display = gr.Textbox(label="Answer", interactive=False, lines=3)
    
    chunks_display = gr.Markdown("")
    
    return (session_id_input, search_btn, traces_table, 
            trace_id_input, view_btn,
            query_display, answer_display, chunks_display)


def create_traces_handlers(db):
    """Create event handlers for retrieval traces tab"""
    
    def search_traces_by_session(session_id):
        """Search and display traces for a session"""
        if not session_id or not session_id.strip():
            return pd.DataFrame(columns=['ID', 'Query', 'Chunks', 'Answer Preview', 'Timestamp'])
        
        traces = db.get_retrieval_traces_by_session(session_id)
        return build_retrieval_traces_df(traces)
    
    def view_trace_details(trace_id):
        """Display full details of a trace"""
        if not trace_id:
            return "", "", ""
        
        # Get conversation to find trace
        conv = db.get_conversation_by_id(int(trace_id))
        if not conv:
            return "❌ Conversation not found", "", ""
        
        trace = db.get_retrieval_trace_by_conversation(conv.conversation_id)
        if not trace:
            return "❌ No retrieval trace found for this conversation", "", ""
        
        chunks_md = format_chunks_display(trace.retrieved_chunks)
        return trace.query_input, trace.final_answer, chunks_md
    
    return search_traces_by_session, view_trace_details
