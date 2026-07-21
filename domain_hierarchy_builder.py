"""
domain_hierarchy_builder.py
===========================
Dynamically builds DOMAIN_HIERARCHY and optimized indexes at startup
by combining DOMAIN_MAP, TOPIC_MAP, _SUPPLEMENTS, TECH_ENTITY_DICTIONARY,
and ABBREVIATION_MAP. Runs exactly once during import.
"""

from typing import Dict, List, Tuple, Set, Any
from collections import defaultdict

# Mapping of all topics in TOPIC_MAP to their corresponding Subjects
TOPIC_TO_SUBJECT = {
    # database management systems
    "normalization": "Relational Database Design",
    "transactions": "Transaction Processing",
    "joins": "Relational Query Operations",
    "indexing": "Storage and Indexing",
    "sql": "Database Query Languages",
    "recovery": "System Recovery",
    "concurrency": "Concurrency Control",
    "er model": "Database Design",

    # computer networks
    "osi model": "Network Architecture",
    "routing protocols": "Routing and Forwarding",
    "transport protocols": "Transport Layer Services",
    "application protocols": "Application Services",
    "ip addressing": "Network Layer Addressing",

    # operating systems
    "process management": "Process and Thread Management",
    "memory management": "Memory Management",
    "deadlocks": "Resource Synchronization",
    "file systems": "Storage and File Systems",
    "concurrency": "Resource Synchronization",

    # machine learning
    "supervised learning": "Supervised Learning Models",
    "unsupervised learning": "Unsupervised Learning Models",
    "neural networks": "Deep Learning Architectures",
    "model evaluation": "Model Assessment",

    # artificial intelligence
    "search algorithms": "Problem Solving Search",
    "knowledge representation": "Knowledge Representation",
    "logic and planning": "Reasoning and Planning",
    "expert systems": "Applied AI Systems",

    # compiler design
    "lexical analysis": "Lexical Analysis",
    "syntax analysis": "Syntax Analysis and Parsing",
    "semantic analysis": "Type Checking and Semantics",
    "code optimization": "Compiler Optimization",
    "code generation": "Target Code Generation",

    # computer graphics
    "rendering techniques": "Image Synthesis",
    "geometrical transformations": "Geometric Modeling",
    "shading and texturing": "Illumination and Appearance",
    "rasterization": "Rasterization Algorithms",

    # cloud computing
    "service models": "Cloud Infrastructure",
    "virtualization and containers": "Virtualization Technologies",
    "cloud providers": "Cloud Systems",
    "microservices architecture": "Distributed Services",

    # big data analytics
    "distributed storage": "Distributed Data Storage",
    "data processing frameworks": "Distributed Processing",
    "data warehousing": "Enterprise Data Warehouses",
    "nosql systems": "Non-Relational Databases",

    # internet of things
    "embedded systems": "IoT Hardware Systems",
    "protocols and communication": "IoT Protocols",
    "sensors and actuators": "IoT Device Interaction",
    "iot architectures": "IoT Systems Architecture",

    # software engineering
    "software development life cycle": "Software SDLC",
    "design patterns": "Software Architecture and Design",
    "testing and qa": "Software Verification",
    "system modeling": "Software Requirements and UML",

    # computer architecture
    "pipelining and hazards": "Processor Pipeline",
    "parallel architectures": "Parallel Computer Architecture",
    "memory systems": "Memory Hierarchy Coherence",
    "instruction level parallelism": "Instruction Level Parallelism",

    # computer organization
    "instruction set architecture": "ISA Design",
    "memory hierarchy": "Processor Memory Design",
    "i/o organization": "Input/Output Systems",
    "control unit design": "CPU Control Design",

    # digital electronics
    "boolean algebra": "Combinational Logic Design",
    "combinational logic": "Combinational Logic Design",
    "sequential logic": "Sequential Logic Design",
    "logic gates": "Logic Gate Components",

    # data structures
    "linear structures": "Linear Data Structures",
    "non-linear structures": "Non-Linear Data Structures",
    "trees": "Advanced Tree Structures",
    "graphs": "Graph Representations",
    "hashing": "Hashing Techniques",

    # design and analysis of algorithms
    "algorithm analysis": "Algorithm Analysis",
    "sorting and searching": "Sorting and Searching Algorithms",
    "graph algorithms": "Graph Traversal and Routing",
    "dynamic programming": "Dynamic Programming Solutions",
    "greedy algorithms": "Greedy Heuristic Solutions",

    # c programming
    "pointers and memory": "Memory Management in C",
    "data types and structures": "Structured Types in C",
    "control flow": "Control Flow in C",
    "file i/o": "Input Output in C",

    # python programming
    "syntax and structures": "Python Core",
    "advanced concepts": "Python Advanced Features",
    "object oriented": "Object Oriented Python",

    # java programming
    "object oriented": "Java Object Oriented Design",
    "advanced topics": "Java Virtual Machine",

    # management information systems
    "enterprise systems": "Enterprise Software",
    "decision support systems": "Decision Support Software",
    "it management": "IT Service Governance",
    "business intelligence": "Business Intelligence and Data",

    # mobile computing
    "mobile development": "Mobile Application Design",
    "wireless networks": "Wireless Networking Protocols",
    "location services": "Location and Geofencing",

    # natural language processing
    "text processing": "Text Processing Techniques",
    "information extraction": "NER and POS Tagging",
    "language modeling": "Transformer Models",

    # distributed systems
    "consensus protocols": "Distributed Consensus",
    "system scalability": "Distributed Hashing and CAP",
    "rpc and middleware": "Distributed Middleware",

    # cyber security
    "cryptography": "Cryptographical Algorithms",
    "network security": "Network Firewalls and VPNs",
    "application security": "Web Vulnerabilities",
    "threats and attacks": "Malicious Software",

    # web technologies
    "frontend development": "Frontend Frameworks",
    "backend development": "Backend Services",
    "web services": "Web Protocols",
    "web security": "Web Tokens and Sessions",

    # data mining
    "pattern mining": "Association Rule Mining",
    "clustering algorithms": "Clustering Techniques",
    "data preprocessing": "Data Cleaning",

    # parallel computing
    "programming models": "Parallel Models",
    "synchronization": "Concurrency Race Conditions",
    "performance optimization": "Parallel Benchmarking",

    # human computer interaction
    "usability evaluation": "HCI Heuristics",
    "user experience design": "UX Wireframing",

    # other computer science
    "general": "General Computer Science"
}

def capitalize_words(s: str) -> str:
    """Helper to cleanly capitalize terms, e.g., 'artificial intelligence' -> 'Artificial Intelligence'"""
    # Don't capitalize small words like 'and', 'of', 'in', 'or', 'for' unless it's the first word
    words = s.split()
    capitalized = []
    for i, w in enumerate(words):
        if i > 0 and w.lower() in ("and", "of", "in", "or", "for", "to", "by", "with", "the", "a", "an"):
            capitalized.append(w.lower())
        else:
            capitalized.append(w.capitalize())
    return " ".join(capitalized)

def build_domain_hierarchy(
    domain_map: Dict[str, List[str]],
    topic_map: Dict[str, Dict[str, List[str]]],
    supplements: Dict[str, Dict[str, Any]],
    entity_dict: List[str],
    abbrev_map: Dict[str, str]
) -> Tuple[Dict[str, Any], Dict[str, str], Dict[str, Set[str]], Dict[Tuple[str, str], Set[str]], Dict[str, List[Tuple[str, str, str]]], Dict[str, List[Tuple[str, str, str]]], Dict[str, List[Tuple[str, str, str]]], Dict[str, List[Tuple[str, str, str]]], Dict[str, List[Tuple[str, str, str]]]]:
    """
    Constructs the DOMAIN_HIERARCHY and build index structures.
    """
    import re
    import unicodedata
    
    def normalize_term(text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        for abbrev, expansion in abbrev_map.items():
            text = re.sub(rf"\b{re.escape(abbrev)}\b", expansion, text)
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    hierarchy: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
    
    # Track display names for capitalization preservation
    domain_display_map: Dict[str, str] = {}
    subject_display_map: Dict[Tuple[str, str], str] = {}
    topic_display_map: Dict[Tuple[str, str, str], str] = {}
    
    # Fast lookups for category matching
    entities_set = {e.lower() for e in entity_dict}
    
    # Initialize all domains from topic_map
    for dom_key, topics in topic_map.items():
        dom_display = capitalize_words(dom_key)
        domain_display_map[dom_key.lower()] = dom_display
        hierarchy[dom_display] = {}
        
        for top_key, keywords in topics.items():
            # Determine subject
            sub_key = TOPIC_TO_SUBJECT.get(top_key.lower(), "General Computer Science")
            sub_display = capitalize_words(sub_key)
            subject_display_map[(dom_key.lower(), sub_key.lower())] = sub_display
            
            if sub_display not in hierarchy[dom_display]:
                hierarchy[dom_display][sub_display] = {}
                
            top_display = capitalize_words(top_key)
            topic_display_map[(dom_key.lower(), sub_key.lower(), top_key.lower())] = top_display
            
            # Setup topic entry
            topic_entry = {
                "keywords": {},
                "aliases": {},
                "entities": {},
                "verbs": {}
            }
            
            # Map manual supplement key to TOPIC_MAP topic key
            supplement_mapping = {
                "breadth first search": "graph algorithms",
                "depth first search": "graph algorithms",
                "normalization": "normalization",
                "deadlock": "deadlocks",
                "tcp": "transport protocols",
                "paging": "memory management",
                "sql": "sql",
                "sorting": "sorting and searching",
                "er model": "er model",
                "ipv4": "ip addressing"
            }
            
            # Find all supplements that map to this top_key
            matched_supps = []
            for supp_key, target_top in supplement_mapping.items():
                if target_top == top_key.lower():
                    supp = supplements.get(supp_key)
                    if supp and supp.get("domain", "").lower() == dom_key.lower():
                        matched_supps.append(supp)
                        
            # 1. Load from matching supplements if any
            if matched_supps:
                for supp in matched_supps:
                    # Load concepts as keywords with importance
                    concepts = supp.get("concepts", {})
                    for concept_name, concept_meta in concepts.items():
                        importance = concept_meta.get("importance", 5)
                        topic_entry["keywords"][normalize_term(concept_name)] = importance
                        
                        # Add concept aliases
                        for alias in concept_meta.get("aliases", []):
                            topic_entry["aliases"][normalize_term(alias)] = max(1, importance - 1)
                            
                    # Add verbs
                    for verb in supp.get("verbs", []):
                        topic_entry["verbs"][normalize_term(verb)] = 5
                        
                    # Add contexts as keywords (importance 7)
                    for ctx in supp.get("contexts", []):
                        topic_entry["keywords"][normalize_term(ctx)] = 7
            
            # 2. Merge / fallback to positional weights from topic_map keywords list
            for idx, kw in enumerate(keywords):
                kw_lower = kw.lower()
                kw_norm = normalize_term(kw_lower)
                if kw_norm not in topic_entry["keywords"]:
                    # Linear decay from 10 to 6
                    weight = 10 if idx == 0 else max(6, 10 - idx)
                    topic_entry["keywords"][kw_norm] = weight
                
                # Add abbreviation aliases if not already in aliases
                for abbrev, full in abbrev_map.items():
                    if kw_lower == full.lower():
                        ab_norm = normalize_term(abbrev)
                        if ab_norm not in topic_entry["aliases"]:
                            topic_entry["aliases"][ab_norm] = topic_entry["keywords"][kw_norm]
                    elif kw_lower == abbrev.lower():
                        fl_norm = normalize_term(full)
                        if fl_norm not in topic_entry["aliases"]:
                            topic_entry["aliases"][fl_norm] = topic_entry["keywords"][kw_norm]
                            
            # Classify keywords into entities
            for kw in list(topic_entry["keywords"].keys()):
                if kw in entities_set:
                    topic_entry["entities"][kw] = topic_entry["keywords"][kw]
                    
            # Classify aliases into entities
            for al in list(topic_entry["aliases"].keys()):
                if al in entities_set:
                    topic_entry["entities"][al] = topic_entry["aliases"][al]
                    
            # Automatically classify verbs
            for verb in list(topic_entry["keywords"].keys()):
                if verb in ("traverse", "sort", "search", "design", "implement", "analyze", "evaluate", "create", "query", "run", "allocate"):
                    topic_entry["verbs"][verb] = topic_entry["keywords"][verb]
            
            hierarchy[dom_display][sub_display][top_display] = topic_entry

    # Build optimized flat indexes for fast O(1) lookups
    domain_index: Dict[str, str] = {normalize_term(d): d for d in hierarchy}
    subject_index: Dict[str, Set[str]] = defaultdict(set)
    topic_index: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
    
    # Matching dictionaries: mapping -> list of (domain, subject, topic) tuples
    alias_idx: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    entity_idx: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    phrase_idx: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    keyword_idx: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    verb_idx: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    
    for dom_name, subjects in hierarchy.items():
        dom_norm = normalize_term(dom_name)
        for sub_name, topics in subjects.items():
            sub_norm = normalize_term(sub_name)
            subject_index[dom_norm].add(sub_name)
            
            for top_name, meta in topics.items():
                top_norm = normalize_term(top_name)
                topic_index[(dom_norm, sub_norm)].add(top_name)
                
                target = (dom_name, sub_name, top_name)
                
                # Index keywords & phrases
                for kw, weight in meta["keywords"].items():
                    if " " in kw:
                        phrase_idx[kw].append(target)
                    else:
                        keyword_idx[kw].append(target)
                        
                # Index aliases
                for al, weight in meta["aliases"].items():
                    if " " in al:
                        phrase_idx[al].append(target)
                    else:
                        alias_idx[al].append(target)
                        
                # Index entities
                for ent, weight in meta["entities"].items():
                    if " " in ent:
                        phrase_idx[ent].append(target)
                    else:
                        entity_idx[ent].append(target)
                        
                # Index verbs
                for v, weight in meta["verbs"].items():
                    if " " in v:
                        phrase_idx[v].append(target)
                    else:
                        verb_idx[v].append(target)
                        
    # Convert subject and topic sets to sorted lists for deterministic indexing
    subject_idx_final = {k: sorted(list(v)) for k, v in subject_index.items()}
    topic_idx_final = {k: sorted(list(v)) for k, v in topic_index.items()}
    
    return (
        hierarchy,
        domain_index,
        subject_idx_final,
        topic_idx_final,
        dict(alias_idx),
        dict(entity_idx),
        dict(phrase_idx),
        dict(keyword_idx),
        dict(verb_idx)
    )
