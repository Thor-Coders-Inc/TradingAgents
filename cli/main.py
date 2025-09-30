from typing import Optional, Any, Dict, Iterator
import datetime
import typer
from pathlib import Path
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule
from dataclasses import dataclass # NEW: Import dataclass

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
from cli.utils import *

console = Console()

app = typer.Typer(
    name="TradingAgents",
    help="TradingAgents CLI: Multi-Agents LLM Financial Trading Framework",
    add_completion=True,
)

AGENT_TEAMS_CONFIG = {
    "Analyst Team": [
        "Market Analyst",
        "Social Analyst",
        "News Analyst",
        "Fundamentals Analyst",
    ],
    "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
    "Trading Team": ["Trader"],
    "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
    "Portfolio Management": ["Portfolio Manager"],
}

# --- NEW: Event Dataclasses for Decoupling ---
@dataclass
class AgentStatusUpdate:
    agent_name: str
    status: str

@dataclass
class ReportGenerated:
    report_name: str
    content: str

@dataclass
class MessageLogged:
    message_type: str
    content: str

@dataclass
class ToolCallLogged:
    tool_name: str
    args: Dict[str, Any]

# Type alias for our events
AnalysisEvent = AgentStatusUpdate | ReportGenerated | MessageLogged | ToolCallLogged

# (MessageBuffer class and other
