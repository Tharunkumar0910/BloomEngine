import pytest
from knowledge.concepts import _SUPPLEMENTS
from knowledge import DOMAIN_HIERARCHY

def test_all_supplements_are_merged():
    """
    Verify that every supplement in _SUPPLEMENTS is successfully merged into DOMAIN_HIERARCHY.
    Specifically, we check if the concepts of the supplements are present under the respective domain/subject/topic.
    """
    assert len(_SUPPLEMENTS) > 0, "No supplements found in knowledge/concepts.py"
    
    # We will map each supplement key to its destination in DOMAIN_HIERARCHY
    # based on the SUPPLEMENT_MAPPING logic.
    supplement_to_topic = {
        "breadth first search": ("Design and Analysis of Algorithms", "Graph Traversal and Routing", "Graph Algorithms"),
        "depth first search": ("Design and Analysis of Algorithms", "Graph Traversal and Routing", "Graph Algorithms"),
        "normalization": ("Database Management Systems", "Relational Database Design", "Normalization"),
        "deadlock": ("Operating Systems", "Resource Synchronization", "Deadlocks"),
        "tcp": ("Computer Networks", "Transport Layer Services", "Transport Protocols"),
        "paging": ("Operating Systems", "Memory Management", "Memory Management"),
        "sql": ("Database Management Systems", "Database Query Languages", "Sql"),
        "sorting": ("Design and Analysis of Algorithms", "Sorting and Searching Algorithms", "Sorting and Searching"),
        "er model": ("Database Management Systems", "Database Design", "Er Model"),
        "ipv4": ("Computer Networks", "Network Layer Addressing", "Ip Addressing")
    }
    
    for supp_key, (dom_display, sub_display, top_display) in supplement_to_topic.items():
        assert dom_display in DOMAIN_HIERARCHY, f"Domain {dom_display} not in hierarchy"
        assert sub_display in DOMAIN_HIERARCHY[dom_display], f"Subject {sub_display} not under {dom_display}"
        assert top_display in DOMAIN_HIERARCHY[dom_display][sub_display], f"Topic {top_display} not under {dom_display} -> {sub_display}"
        
        topic_meta = DOMAIN_HIERARCHY[dom_display][sub_display][top_display]
        supp_data = _SUPPLEMENTS[supp_key]
        
        # Check that concepts are present in hierarchy topic keywords
        import config
        for concept_name in supp_data.get("concepts", {}):
            concept_norm = concept_name.lower().strip()
            expansion = config.ABBREVIATION_MAP.get(concept_norm)
            
            found = False
            for kw in topic_meta["keywords"]:
                if concept_norm in kw or kw in concept_norm:
                    found = True
                    break
                if expansion and (expansion in kw or kw in expansion):
                    found = True
                    break
            assert found, f"Concept '{concept_name}' from supplement '{supp_key}' was not found in hierarchy under {dom_display} -> {sub_display} -> {top_display}"
            
        print(f"Verified supplement '{supp_key}' merged successfully into '{dom_display} -> {sub_display} -> {top_display}'")
