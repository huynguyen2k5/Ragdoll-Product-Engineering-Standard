"""Durable, project-scoped local history engine."""

from .identity import get_project, list_projects, register_project
from .maintenance import get_index_status, rebuild_index
from .retrieval import compile_evidence, comprehensive_search, focused_search, forensic_search
from .store import (
    append_event,
    iter_conversation_events,
    list_conversations,
    purge_project,
    read_conversation,
    start_conversation,
    verify_conversation,
)

__all__ = [
    "append_event",
    "compile_evidence",
    "comprehensive_search",
    "focused_search",
    "forensic_search",
    "get_index_status",
    "get_project",
    "iter_conversation_events",
    "list_conversations",
    "list_projects",
    "purge_project",
    "read_conversation",
    "rebuild_index",
    "register_project",
    "start_conversation",
    "verify_conversation",
]
