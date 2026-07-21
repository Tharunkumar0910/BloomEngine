import pytest
from retry_context import get_retry_topic_context, get_retry_context_string
from prompt_templates import build_prompt

def test_get_retry_topic_context_basic():
    # Breadth First Search should return queue, graph, vertex, etc.
    concepts = get_retry_topic_context("Breadth First Search")
    assert isinstance(concepts, list)
    if concepts:
        assert len(concepts) >= 2
        assert len(concepts) <= 4
        # "breadth first search" or "bfs" should not be in the concepts
        assert "breadth first search" not in concepts
        assert "bfs" not in concepts
        # Generic words should be filtered
        assert "algorithm" not in concepts
        assert "system" not in concepts

def test_get_retry_topic_context_empty_or_invalid():
    assert get_retry_topic_context("") == []
    assert get_retry_topic_context("Nonexistent Topic 12345") == []

def test_get_retry_context_string_formatting():
    # If a topic returns concepts, we verify formatting constraints
    ctx_str = get_retry_context_string("Breadth First Search")
    if ctx_str:
        # Check lines limit
        lines = ctx_str.split("\n")
        assert len(lines) <= 6
        # Check positive guidance
        assert "Use these concepts if needed." in ctx_str
        assert "Do not introduce" not in ctx_str
        assert "Academic Context" in ctx_str

def test_build_prompt_with_context():
    # Test build_prompt structure with and without topic_context
    prompt_no_ctx = build_prompt(
        question="Explain BFS.",
        source_bloom="Understand",
        target_bloom="Analyze",
        domain="Algorithms",
        topic="Breadth First Search",
        topic_context=None
    )
    assert "Topic: Breadth First Search\n" in prompt_no_ctx
    
    ctx_str = "Academic Context\n\nqueue\ngraph traversal\n\nUse these concepts if needed."
    prompt_with_ctx = build_prompt(
        question="Explain BFS.",
        source_bloom="Understand",
        target_bloom="Analyze",
        domain="Algorithms",
        topic="Breadth First Search",
        topic_context=ctx_str
    )
    assert "Topic:\nBreadth First Search\n\nAcademic Context\n" in prompt_with_ctx
