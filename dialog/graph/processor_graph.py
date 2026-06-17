"""CourseProcessorGraph — the single public API for the processing pipeline.

Inspired by TradingAgents' TradingAgentsGraph: owns LLM creation, config,
graph compilation, and the process() entry point. Consumers never touch
LangGraph directly.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from dialog.default_config import DEFAULT_CONFIG
from dialog.llm_clients import create_llm_client
from .propagation import Propagator
from .setup import GraphSetup

logger = logging.getLogger(__name__)


class CourseProcessorGraph:
    """Main orchestrator for the course processing pipeline."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        debug: bool = False,
    ):
        """Initialize the processing graph and components.

        Args:
            config: Configuration dictionary. If None, uses DEFAULT_CONFIG.
            debug: Whether to stream node-by-node output for debugging.
        """
        self.debug = debug
        self.config = config or DEFAULT_CONFIG

        # Initialize LLM via the client abstraction
        client = create_llm_client(
            provider=self.config.get("llm_provider", "openai"),
            model=self.config["ollama_model"],
            base_url=self.config.get("ollama_base_url"),
            mock=self.config.get("mock_llm", False),
            api_key=self.config.get("ollama_api_key", ""),
        )
        self.llm = client.get_llm()

        # Build the graph
        self.graph_setup = GraphSetup(self.llm)
        self.propagator = Propagator()

        workflow = self.graph_setup.setup_graph()
        self.graph = workflow.compile()

    def process(self, source_path: str) -> Dict[str, Any]:
        """Process a document through the full pipeline.

        This is the single public entry point — upload a file path,
        get back structured results.

        Args:
            source_path: Path to the PDF, TXT, or MD file.

        Returns:
            Final graph state dict with knowledge_map, question_bank,
            audit_flags, and review_status.
        """
        initial_state = self.propagator.create_initial_state(source_path)

        if self.debug:
            for chunk in self.graph.stream(initial_state, stream_mode="values"):
                logger.info("Graph step: %s", list(chunk.keys()))
            return chunk  # last chunk is the final state
        else:
            return self.graph.invoke(initial_state)
