import pytest
from knowledge.concepts import (
    normalize_concept,
    are_equivalent,
    get_equivalent_terms,
    detect_duplicate_equivalent_terms,
    Concept
)

def test_concept_wrapper():
    """Verify that Concept wrapper class functions as string but stores normalization."""
    c = Concept("BFS")
    assert isinstance(c, str)
    assert c == "BFS"
    assert c.canonical == "breadth first search"

def test_normalize_concept():
    """Verify normalize_concept maps aliases to canonical forms and leaves unknown terms as-is."""
    assert normalize_concept("bfs") == "breadth first search"
    assert normalize_concept("BFS") == "breadth first search"
    assert normalize_concept("breadth first search") == "breadth first search"
    assert normalize_concept("dbms") == "database management system"
    assert normalize_concept("random unknown term") == "random unknown term"

def test_are_equivalent():
    """Verify that are_equivalent correctly evaluates equality of canonical terms."""
    assert are_equivalent("bfs", "Breadth First Search") is True
    assert are_equivalent("BFS", "bfs") is True
    assert are_equivalent("dbms", "database management system") is True
    assert are_equivalent("bfs", "dfs") is False
    assert are_equivalent("random term", "random term") is True

def test_get_equivalent_terms():
    """Verify that get_equivalent_terms returns all aliases/variations of a concept."""
    equiv = get_equivalent_terms("bfs")
    assert "bfs" in equiv
    assert "breadth first search" in equiv
    
    # Non-existent/unknown concept should return just itself
    equiv_unknown = get_equivalent_terms("unknown-concept")
    assert equiv_unknown == ["unknown-concept"]

def test_detect_duplicate_equivalent_terms():
    """Verify detection of duplicate aliases representing the same canonical concept."""
    # BFS and Breadth First Search are duplicates
    dups = detect_duplicate_equivalent_terms(["BFS", "Breadth First Search", "Dijkstra"])
    assert len(dups) == 1
    canonical, aliases = dups[0]
    assert canonical == "breadth first search"
    assert set(aliases) == {"BFS", "Breadth First Search"}

    # No duplicates
    dups_no = detect_duplicate_equivalent_terms(["BFS", "DFS", "Dijkstra"])
    assert len(dups_no) == 0
