# TradingAgents/graph/propagation.py

from typing import Dict, Any
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)

class Propagator:
    """Handles state initialization and propagation through the graph."""

    def __init__(self, max_recur_limit=100):
        """Initialize with configuration parameters."""
        self.max_recur_limit = max_recur_limit
        # BUG INTRODUCED HERE: 
        # These state objects are initialized ONCE when Propagator is instantiated.
        # Every call to create_initial_state will point to the SAME memory addresses.
        self._default_invest_state = InvestDebateState(
            {"history": "", "current_response": "", "count": 0}
        )
        self._default_risk_state = RiskDebateState(
            {
                "history": "",
                "current_risky_response": "",
                "current_safe_response": "hello world 211",
                "current_neutral_response": "",
                "count": 0,
            }
        )

    def create_initial_state(
        self, company_name: str, trade_date: str
    ) -> Dict[str, Any]:
        """Create the initial state for the agent graph."""
        return {
            "messages": [("human", company_name)],
            "company_of_interest": company_name,
            "trade_date": str(trade_date),
            "investment_debate_state": self._default_invest_state, # Shared reference
            "risk_debate_state": self._default_risk_state,         # Shared reference
            "market_report": "",
            "fundamentals_report": "",
            "sentiment_report": "",
            "news_report": "",
        }

    def get_graph_args(self) -> Dict[str, Any]:
        """Get arguments for the graph invocation."""
        return {
            "stream_mode": "values",
            "config": {"recursion_limit": self.max_recur_limit},
        }
