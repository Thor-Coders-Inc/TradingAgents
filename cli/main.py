from typing import Optional
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

# These would be your actual project imports
# from tradingagents.graph.trading_graph import TradingAgentsGraph
# from tradingagents.default_config import DEFAULT_CONFIG
# from cli.models import AnalystType
# from cli.utils import *

# --- Mock Imports for Standalone Execution ---
class MockTradingAgentsGraph:
    def __init__(self, *args, **kwargs): self.propagator, self.graph = self, self
    def create_initial_state(self, *args): return {}
    def get_graph_args(self): return {}
    def stream(self, *args, **kwargs):
        mock_data = [
            {'messages': [{'content': 'Starting...'}]}, {'messages': [{'content': 'Fetching...', 'tool_calls': [{'name': 'get_data', 'args': {'ticker': 'SPY'}}]}]},
            {'messages': [{}], 'market_report': 'The market is bullish.'}, {'messages': [{}], 'sentiment_report': 'Social media sentiment is positive.'},
            {'messages': [{}], 'news_report': 'Recent news is favorable.'}, {'messages': [{}], 'fundamentals_report': 'Fundamentals are strong.'},
            {'messages': [{}], 'final_trade_decision': 'BUY SPY.'}
        ]
        yield from mock_data
    def process_signal(self, decision): return f"Processed: {decision}"
TradingAgentsGraph = MockTradingAgentsGraph
DEFAULT_CONFIG = {"results_dir": "./trading_results"}
class AnalystType: value = "market"
def select_analysts(): return [AnalystType()]
def select_research_depth(): return 2
def select_llm_provider(): return "mock_provider", "http://localhost:8000"
def select_shallow_thinking_agent(p): return "mock-shallow"
def select_deep_thinking_agent(p): return "mock-deep"
# --- End of Mock Imports ---


console = Console()

app = typer.Typer(
    name="TradingAgents",
    help="TradingAgents CLI: Multi-Agents LLM Financial Trading Framework",
    add_completion=True,
)

class MessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None
        self.agent_status = {
            "Market Analyst": "pending", "Social Analyst": "pending",
            "News Analyst": "pending", "Fundamentals Analyst": "pending",
            "Bull Researcher": "pending", "Bear Researcher": "pending",
            "Research Manager": "pending", "Trader": "pending",
            "Risky Analyst": "pending", "Neutral Analyst": "pending",
            "Safe Analyst": "pending", "Portfolio Manager": "pending",
        }
        self.current_agent = None
        self.report_sections = {
            "market_report": None, "sentiment_report": None, "news_report": None,
            "fundamentals_report": None, "investment_plan": None,
            "trader_investment_plan": None, "final_trade_decision": None,
        }

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        # ... (This function is unchanged) ...
        pass

    def _update_final_report(self):
        # ... (This function is unchanged) ...
        pass

message_buffer = MessageBuffer()

def create_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout

# --- NEW HELPER FUNCTION FOR TICKET 3 ---
def _create_status_cell(status: str) -> Text | Spinner:
    """Generates a rich renderable for an agent's status cell."""
    if status == "in_progress":
        return Spinner("dots", text="[blue]in_progress[/blue]", style="bold cyan")
    
    status_color = {
        "pending": "yellow",
        "completed": "green",
        "error": "red",
    }.get(status, "white")
    
    return Text(status, style=status_color)

def update_display(layout, spinner_text=None):
    layout["header"].update(
        Panel(
            "[bold green]Welcome to TradingAgents CLI[/bold green]\n"
            "[dim]© [Tauric Research](https://github.com/TauricResearch)[/dim]",
            title="Welcome to TradingAgents", border_style="green", padding=(1, 2), expand=True,
        )
    )

    progress_table = Table(
        show_header=True, header_style="bold magenta", show_footer=False,
        box=box.SIMPLE_HEAD, title=None, padding=(0, 2), expand=True,
    )
    progress_table.add_column("Team", style="cyan", justify="center", width=20)
    progress_table.add_column("Agent", style="green", justify="center", width=20)
    progress_table.add_column("Status", style="yellow", justify="center", width=20)

    # Hardcoded teams dictionary (as per original code)
    teams = {
        "Analyst Team": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
        "Portfolio Management": ["Portfolio Manager"],
    }

    # --- MODIFIED TO USE HELPER FUNCTION (TICKET 3) ---
    for team, agents in teams.items():
        for i, agent in enumerate(agents):
            team_name = team if i == 0 else ""
            status = message_buffer.agent_status[agent]
            
            # Use the new helper function to generate the status cell
            status_cell = _create_status_cell(status)
            
            progress_table.add_row(team_name, agent, status_cell)
        
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    layout["progress"].update(
        Panel(progress_table, title="Progress", border_style="cyan", padding=(1, 2))
    )

    # ... (rest of the update_display function is unchanged) ...
    # Messages panel showing recent messages and tool calls
    messages_table = Table(
        show_header=True, header_style="bold magenta", show_footer=False,
        expand=True, box=box.MINIMAL, show_lines=True, padding=(0, 1),
    )
    messages_table.add_column("Time", style="cyan", width=8, justify="center")
    messages_table.add_column("Type", style="green", width=10, justify="center")
    messages_table.add_column("Content", style="white", no_wrap=False, ratio=1)

    all_messages = []
    # (message and tool call handling logic is unchanged)
    for timestamp, tool_name, args in message_buffer.tool_calls:
        all_messages.append((timestamp, "Tool", f"{tool_name}: {args}"))
    for timestamp, msg_type, content in message_buffer.messages:
        all_messages.append((timestamp, msg_type, str(content)))
    all_messages.sort(key=lambda x: x[0])
    
    for timestamp, msg_type, content in all_messages[-12:]:
        messages_table.add_row(timestamp, msg_type, Text(content, overflow="fold"))
    
    layout["messages"].update(Panel(messages_table, title="Messages & Tools", border_style="blue", padding=(1, 2)))
    # (analysis panel and footer are unchanged)
    if message_buffer.current_report:
        layout["analysis"].update(Panel(Markdown(message_buffer.current_report), title="Current Report", border_style="green", padding=(1,2)))
    else:
        layout["analysis"].update(Panel("[italic]Waiting for report...[/italic]", title="Current Report", border_style="green", padding=(1,2)))

def get_user_selections():
    # ... (This function is unchanged) ...
    return { "ticker": "SPY", "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d"),
             "analysts": [AnalystType()], "research_depth": 2, "llm_provider": "mock_provider",
             "backend_url": "http://localhost:8000", "shallow_thinker": "mock-shallow",
             "deep_thinker": "mock-deep" }

def get_ticker():
    return typer.prompt("", default="SPY")

def get_analysis_date():
    return typer.prompt("", default=datetime.datetime.now().strftime("%Y-%m-%d"))

def display_complete_report(final_state):
    """Display the complete analysis report with team-based panels."""
    console.print("\n[bold green]Complete Analysis Report[/bold green]\n")

    # --- MODIFIED TO USE A LOOP (TICKET 3) ---
    analyst_reports = []
    
    # Configuration for analyst reports [('key_in_final_state', 'Panel Title')]
    ANALYST_REPORT_CONFIG = {
        "market_report": "Market Analyst",
        "sentiment_report": "Social Analyst",
        "news_report": "News Analyst",
        "fundamentals_report": "Fundamentals Analyst",
    }
    
    for report_key, panel_title in ANALYST_REPORT_CONFIG.items():
        if report_content := final_state.get(report_key):
            analyst_reports.append(
                Panel(
                    Markdown(report_content),
                    title=panel_title,
                    border_style="blue",
                    padding=(1, 2),
                )
            )

    if analyst_reports:
        console.print(
            Panel(
                Columns(analyst_reports, equal=True, expand=True),
                title="I. Analyst Team Reports",
                border_style="cyan",
                padding=(1, 2),
            )
        )

    # ... (rest of the display_complete_report function is unchanged) ...

def extract_content_string(content):
    # ... (This function is unchanged) ...
    if isinstance(content, str): return content
    if isinstance(content, list): return ' '.join(str(item) for item in content)
    return str(content)

def run_analysis():
    # This function uses the original if/elif logic, as Ticket 2 is excluded.
    selections = get_user_selections()

    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = selections["research_depth"]
    # ... (rest of config setup is unchanged)

    graph = TradingAgentsGraph([analyst.value for analyst in selections["analysts"]], config=config)
    
    layout = create_layout()
    with Live(layout, refresh_per_second=4) as live:
        # ... (initial setup and messages are unchanged) ...
        update_display(layout)
        
        init_agent_state = graph.propagator.create_initial_state(selections["ticker"], selections["analysis_date"])
        args = graph.propagator.get_graph_args()

        trace = []
        for chunk in graph.graph.stream(init_agent_state, **args):
            # This is the original, non-event-driven logic
            if len(chunk.get("messages", [])) > 0:
                last_message = chunk["messages"][-1]
                content = extract_content_string(last_message.get('content'))
                message_buffer.add_message("Reasoning", content)

                if tool_calls := last_message.get("tool_calls"):
                    for tc in tool_calls:
                        message_buffer.add_tool_call(tc.get("name"), tc.get("args"))
            
            # Original if/elif block for handling reports and status updates
            if "market_report" in chunk and chunk["market_report"]:
                message_buffer.update_report_section("market_report", chunk["market_report"])
                message_buffer.update_agent_status("Market Analyst", "completed")
                message_buffer.update_agent_status("Social Analyst", "in_progress")
            
            if "sentiment_report" in chunk and chunk["sentiment_report"]:
                 message_buffer.update_report_section("sentiment_report", chunk["sentiment_report"])
                 message_buffer.update_agent_status("Social Analyst", "completed")
                 message_buffer.update_agent_status("News Analyst", "in_progress")
            
            # ... and so on for the rest of the original logic ...

            update_display(layout)
            trace.append(chunk)

        # Finalization
        final_state = trace[-1] if trace else {}
        for agent in message_buffer.agent_status:
