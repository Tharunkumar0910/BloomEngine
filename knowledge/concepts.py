import re
from typing import Optional
import config
from knowledge.domains import get_normalized_domains
from knowledge.topics import TOPIC_MAP

class Concept(str):
    def __new__(cls, text: str, canonical: str = None):
        obj = str.__new__(cls, text)
        obj._canonical = canonical
        return obj

    @property
    def text(self) -> str:
        return str(self)

    @property
    def canonical(self) -> str:
        if self._canonical is None:
            return normalize_concept(str(self))
        return self._canonical

# Dynamic compilation of CANONICAL_CONCEPTS
CANONICAL_CONCEPTS = {}

MANUAL_GROUPS = [
    ("breadth first search", ["bfs", "breadth first traversal", "breadth-first search"]),
    ("depth first search", ["dfs", "depth first traversal", "depth-first search"]),
    ("entity relationship model", ["entity relationship diagram", "er diagram", "erd", "er"]),
    ("primary key", ["pk"]),
    ("operating system", ["os"]),
    ("open systems interconnection", ["osi", "osi model"]),
    ("internet protocol version 4", ["ipv4"]),
    ("internet protocol version 6", ["ipv6"]),
    ("transmission control protocol", ["tcp"]),
    ("user datagram protocol", ["udp"]),
    ("domain name system", ["dns"]),
    ("structured query language", ["sql"]),
    ("hypertext transfer protocol", ["http"]),
]

for canonical, aliases in MANUAL_GROUPS:
    if canonical not in CANONICAL_CONCEPTS:
        CANONICAL_CONCEPTS[canonical] = {"aliases": set()}
    for alias in aliases:
        CANONICAL_CONCEPTS[canonical]["aliases"].add(alias.lower())

def is_already_alias(term: str) -> bool:
    t_lower = term.lower()
    for info in CANONICAL_CONCEPTS.values():
        if t_lower in info["aliases"]:
            return True
    return False

abbrev_map = getattr(config, "ABBREVIATION_MAP", {})
for abbrev, expansion in abbrev_map.items():
    abbrev_lower = abbrev.lower()
    exp_lower = expansion.lower()
    if exp_lower not in CANONICAL_CONCEPTS:
        CANONICAL_CONCEPTS[exp_lower] = {"aliases": set()}
    CANONICAL_CONCEPTS[exp_lower]["aliases"].add(abbrev_lower)

tech_dict = getattr(config, "TECH_ENTITY_DICTIONARY", [])
for entity in tech_dict:
    ent_lower = entity.lower()
    if ent_lower not in CANONICAL_CONCEPTS and not is_already_alias(ent_lower):
        CANONICAL_CONCEPTS[ent_lower] = {"aliases": set()}

domain_map = getattr(config, "DOMAIN_MAP", {})
for dom in domain_map.keys():
    dom_lower = dom.lower()
    if dom_lower not in CANONICAL_CONCEPTS and not is_already_alias(dom_lower):
        CANONICAL_CONCEPTS[dom_lower] = {"aliases": set()}

for dom, topics in TOPIC_MAP.items():
    for top in topics:
        top_lower = top.lower()
        if top_lower not in CANONICAL_CONCEPTS and not is_already_alias(top_lower):
            CANONICAL_CONCEPTS[top_lower] = {"aliases": set()}

for canonical in CANONICAL_CONCEPTS:
    CANONICAL_CONCEPTS[canonical]["aliases"].discard(canonical)
    CANONICAL_CONCEPTS[canonical]["aliases"] = sorted(list(CANONICAL_CONCEPTS[canonical]["aliases"]))

_REVERSE_LOOKUP = {}
for canonical, info in CANONICAL_CONCEPTS.items():
    _REVERSE_LOOKUP[canonical] = canonical
    for alias in info["aliases"]:
        _REVERSE_LOOKUP[alias] = canonical

def normalize_concept(text: str) -> str:
    if not text:
        return ""
    text_cleaned = text.strip().lower()
    if text_cleaned in _REVERSE_LOOKUP:
        return _REVERSE_LOOKUP[text_cleaned]
    try:
        from spacy_utils import expand_abbreviations
        expanded = expand_abbreviations(text_cleaned)
        if expanded in _REVERSE_LOOKUP:
            return _REVERSE_LOOKUP[expanded]
    except ImportError:
        pass
    return text_cleaned

def canonicalize_concept_list(concepts) -> list:
    result = set()
    for c in concepts:
        result.add(normalize_concept(str(c)))
    return sorted(list(result))

def are_equivalent(c1: str, c2: str) -> bool:
    return normalize_concept(c1) == normalize_concept(c2)

def get_equivalent_terms(c: str) -> list:
    canon = normalize_concept(c)
    if canon in CANONICAL_CONCEPTS:
        return sorted([canon] + CANONICAL_CONCEPTS[canon]["aliases"])
    return [canon]

def detect_duplicate_equivalent_terms(candidate_concepts) -> list:
    from collections import defaultdict
    canonical_to_surface = defaultdict(set)
    for c in candidate_concepts:
        canonical = c.canonical if hasattr(c, "canonical") else normalize_concept(str(c))
        canonical_to_surface[canonical].add(str(c))
        
    duplicates_found = []
    for canonical, surfaces in canonical_to_surface.items():
        if len(surfaces) > 1:
            duplicates_found.append((canonical, sorted(list(surfaces))))
            
    return duplicates_found

# ---------------------------------------------------------------------------
# Manual Supplements
# ---------------------------------------------------------------------------
_SUPPLEMENTS: dict = {
    "breadth first search": {
        "domain": "design and analysis of algorithms",
        "subject": "graph algorithms",
        "subtopic": "graph traversal",
        "concepts": {
            "bfs":           {"importance": 10, "aliases": ["breadth first search", "breadth-first search"], "category": "algorithm"},
            "queue":         {"importance": 9,  "aliases": ["fifo"],           "category": "data_structure"},
            "graph":         {"importance": 9,  "aliases": [],                 "category": "data_structure"},
            "traversal":     {"importance": 8,  "aliases": [],                 "category": "concept"},
            "shortest path": {"importance": 7,  "aliases": [],                 "category": "application"},
            "vertex":        {"importance": 6,  "aliases": ["node"],           "category": "concept"},
            "level order":   {"importance": 6,  "aliases": ["level-order"],    "category": "context"},
            "edge":          {"importance": 5,  "aliases": [],                 "category": "concept"},
            "visited":       {"importance": 4,  "aliases": [],                 "category": "concept"},
        },
        "graph": {
            "bfs":           {"queue": 1.0, "traversal": 0.95, "graph": 0.90, "level order": 0.85, "shortest path": 0.75},
            "queue":         {"fifo": 1.0,  "enqueue": 0.90,   "dequeue": 0.90},
            "traversal":     {"visited": 0.90, "vertex": 0.85, "edge": 0.75, "path": 0.70},
            "shortest path": {"bfs": 0.85, "unweighted": 0.70, "level order": 0.75},
        },
        "verbs": ["traverse", "search", "explore", "find", "visit"],
        "contexts": ["graph traversal", "connectivity", "level order traversal", "shortest path"],
        "related_topics": ["depth first search", "dijkstra", "graph algorithms"],
    },

    "depth first search": {
        "domain": "design and analysis of algorithms",
        "subject": "graph algorithms",
        "subtopic": "graph traversal",
        "concepts": {
            "dfs":           {"importance": 10, "aliases": ["depth first search", "depth-first search"], "category": "algorithm"},
            "stack":         {"importance": 9,  "aliases": ["lifo"],           "category": "data_structure"},
            "graph":         {"importance": 9,  "aliases": [],                 "category": "data_structure"},
            "backtracking":  {"importance": 8,  "aliases": ["backtrack"],      "category": "concept"},
            "recursion":     {"importance": 7,  "aliases": ["recursive"],      "category": "concept"},
            "vertex":        {"importance": 6,  "aliases": ["node"],           "category": "concept"},
            "edge":          {"importance": 5,  "aliases": [],                 "category": "concept"},
            "cycle":         {"importance": 5,  "aliases": [],                 "category": "application"},
        },
        "graph": {
            "dfs":       {"stack": 1.0, "backtracking": 0.95, "recursion": 0.90, "graph": 0.85},
            "stack":     {"lifo": 1.0,  "push": 0.85, "pop": 0.85},
            "backtracking": {"recursion": 0.90, "state space": 0.70},
        },
        "verbs": ["traverse", "search", "explore", "detect", "visit"],
        "contexts": ["cycle detection", "topological sort", "connected components"],
        "related_topics": ["breadth first search", "topological sort", "graph algorithms"],
    },

    "normalization": {
        "domain": "database management systems",
        "subject": "relational design",
        "subtopic": "schema normalization",
        "concepts": {
            "normalization":          {"importance": 10, "aliases": ["normalisation"],           "category": "concept"},
            "normal form":            {"importance": 9,  "aliases": ["1nf", "2nf", "3nf", "bcnf"], "category": "standard"},
            "functional dependency":  {"importance": 9,  "aliases": ["fd"],                     "category": "concept"},
            "redundancy":             {"importance": 8,  "aliases": ["redundant"],               "category": "concept"},
            "decomposition":          {"importance": 7,  "aliases": [],                          "category": "concept"},
            "anomaly":                {"importance": 7,  "aliases": ["update anomaly", "deletion anomaly"], "category": "concept"},
            "prime attribute":        {"importance": 6,  "aliases": [],                          "category": "concept"},
            "candidate key":          {"importance": 6,  "aliases": [],                          "category": "concept"},
        },
        "graph": {
            "normalization":         {"normal form": 1.0,  "functional dependency": 0.95, "redundancy": 0.90},
            "functional dependency": {"bcnf": 0.90,        "prime attribute": 0.85,       "determinant": 0.80},
            "redundancy":            {"anomaly": 0.90,     "decomposition": 0.80},
        },
        "verbs": ["normalize", "decompose", "eliminate", "reduce"],
        "contexts": ["schema design", "relational model", "database design"],
        "related_topics": ["er model", "sql", "transactions"],
    },

    "deadlock": {
        "domain": "operating systems",
        "subject": "process synchronization",
        "subtopic": "deadlock management",
        "concepts": {
            "deadlock":           {"importance": 10, "aliases": [],                          "category": "concept"},
            "circular wait":      {"importance": 9,  "aliases": [],                          "category": "concept"},
            "mutual exclusion":   {"importance": 9,  "aliases": [],                          "category": "concept"},
            "hold and wait":      {"importance": 8,  "aliases": [],                          "category": "concept"},
            "no preemption":      {"importance": 8,  "aliases": [],                          "category": "concept"},
            "resource":           {"importance": 7,  "aliases": ["resource allocation"],     "category": "concept"},
            "banker's algorithm": {"importance": 7,  "aliases": ["bankers algorithm"],       "category": "algorithm"},
            "safe state":         {"importance": 6,  "aliases": [],                          "category": "concept"},
        },
        "graph": {
            "deadlock":           {"circular wait": 1.0, "mutual exclusion": 0.95, "hold and wait": 0.95, "no preemption": 0.90},
            "banker's algorithm": {"safe state": 1.0, "resource": 0.90, "avoidance": 0.85},
            "circular wait":      {"resource": 0.85, "process": 0.75},
        },
        "verbs": ["detect", "prevent", "avoid", "recover", "resolve"],
        "contexts": ["process management", "resource allocation", "synchronization"],
        "related_topics": ["semaphore", "mutex", "process scheduling"],
    },

    "tcp": {
        "domain": "computer networks",
        "subject": "transport protocols",
        "subtopic": "reliable transmission",
        "concepts": {
            "tcp":                        {"importance": 10, "aliases": ["transmission control protocol"], "category": "protocol"},
            "three-way handshake":        {"importance": 9,  "aliases": ["3-way handshake"],              "category": "concept"},
            "flow control":               {"importance": 9,  "aliases": [],                               "category": "concept"},
            "congestion control":         {"importance": 8,  "aliases": [],                               "category": "concept"},
            "reliable delivery":          {"importance": 8,  "aliases": ["reliable transmission"],        "category": "concept"},
            "segment":                    {"importance": 7,  "aliases": [],                               "category": "concept"},
            "acknowledgement":            {"importance": 7,  "aliases": ["ack"],                          "category": "concept"},
            "window size":                {"importance": 6,  "aliases": [],                               "category": "concept"},
        },
        "graph": {
            "tcp":                 {"three-way handshake": 1.0, "flow control": 0.95, "reliable delivery": 0.90},
            "three-way handshake": {"syn": 0.90, "ack": 0.90, "connection": 0.85},
            "flow control":        {"window size": 0.90, "buffer": 0.80, "receiver": 0.75},
            "congestion control":  {"slow start": 0.85, "window size": 0.80},
        },
        "verbs": ["transmit", "establish", "control", "retransmit", "acknowledge"],
        "contexts": ["reliable communication", "connection-oriented", "error recovery"],
        "related_topics": ["udp", "ip", "socket", "network layer"],
    },

    "paging": {
        "domain": "operating systems",
        "subject": "memory management",
        "subtopic": "virtual memory",
        "concepts": {
            "paging":            {"importance": 10, "aliases": [],                    "category": "concept"},
            "page table":        {"importance": 9,  "aliases": [],                    "category": "data_structure"},
            "virtual memory":    {"importance": 9,  "aliases": [],                    "category": "concept"},
            "page fault":        {"importance": 8,  "aliases": [],                    "category": "concept"},
            "frame":             {"importance": 8,  "aliases": ["physical frame"],    "category": "concept"},
            "page replacement":  {"importance": 7,  "aliases": [],                    "category": "algorithm"},
            "tlb":               {"importance": 7,  "aliases": ["translation lookaside buffer"], "category": "hardware"},
            "thrashing":         {"importance": 6,  "aliases": [],                    "category": "concept"},
        },
        "graph": {
            "paging":          {"page table": 1.0, "virtual memory": 0.95, "page fault": 0.90, "frame": 0.85},
            "page replacement":{"lru": 0.90, "fifo": 0.85, "optimal": 0.80, "thrashing": 0.75},
            "page fault":      {"page replacement": 0.90, "frame": 0.85},
        },
        "verbs": ["allocate", "map", "replace", "load", "evict"],
        "contexts": ["memory allocation", "address translation", "virtual address space"],
        "related_topics": ["segmentation", "virtual memory", "memory hierarchy"],
    },

    "sql": {
        "domain": "database management systems",
        "subject": "query languages",
        "subtopic": "structured query language",
        "concepts": {
            "sql":        {"importance": 10, "aliases": ["structured query language"],    "category": "language"},
            "select":     {"importance": 9,  "aliases": ["query", "dql"],                "category": "concept"},
            "join":       {"importance": 9,  "aliases": ["inner join", "outer join"],    "category": "concept"},
            "where":      {"importance": 8,  "aliases": ["filter", "condition"],         "category": "concept"},
            "index":      {"importance": 7,  "aliases": ["indexing"],                    "category": "data_structure"},
            "view":       {"importance": 6,  "aliases": [],                              "category": "concept"},
            "ddl":        {"importance": 6,  "aliases": ["data definition language"],    "category": "concept"},
            "dml":        {"importance": 6,  "aliases": ["data manipulation language"],  "category": "concept"},
        },
        "graph": {
            "sql":    {"select": 1.0, "join": 0.95, "where": 0.90, "index": 0.80},
            "join":   {"inner join": 0.95, "outer join": 0.90, "natural join": 0.85, "cross join": 0.75},
            "select": {"where": 0.90, "from": 0.90, "group by": 0.80, "having": 0.75},
        },
        "verbs": ["query", "retrieve", "insert", "update", "delete", "join"],
        "contexts": ["relational database", "data retrieval", "database query"],
        "related_topics": ["normalization", "transactions", "indexing"],
    },

    "sorting": {
        "domain": "design and analysis of algorithms",
        "subject": "sorting and searching",
        "subtopic": "comparison sorting",
        "concepts": {
            "sorting":     {"importance": 10, "aliases": ["sort"],                     "category": "concept"},
            "quicksort":   {"importance": 9,  "aliases": ["quick sort"],               "category": "algorithm"},
            "mergesort":   {"importance": 9,  "aliases": ["merge sort"],               "category": "algorithm"},
            "heapsort":    {"importance": 8,  "aliases": ["heap sort"],                "category": "algorithm"},
            "time complexity": {"importance": 8, "aliases": ["complexity"],            "category": "concept"},
            "pivot":       {"importance": 7,  "aliases": [],                           "category": "concept"},
            "divide and conquer": {"importance": 7, "aliases": [],                     "category": "concept"},
            "stability":   {"importance": 6,  "aliases": ["stable sort"],              "category": "concept"},
        },
        "graph": {
            "quicksort":   {"pivot": 1.0, "divide and conquer": 0.90, "time complexity": 0.85},
            "mergesort":   {"divide and conquer": 1.0, "merge": 0.90, "time complexity": 0.85},
            "sorting":     {"quicksort": 0.90, "mergesort": 0.90, "heapsort": 0.85, "time complexity": 0.80},
        },
        "verbs": ["sort", "arrange", "order", "partition", "merge"],
        "contexts": ["algorithm analysis", "comparison-based", "in-place sorting"],
        "related_topics": ["searching", "heap", "algorithm analysis"],
    },

    "er model": {
        "domain": "database management systems",
        "subject": "database design",
        "subtopic": "entity relationship model",
        "concepts": {
            "er model":      {"importance": 10, "aliases": ["entity relationship model", "erd"],  "category": "concept"},
            "entity":        {"importance": 9,  "aliases": ["entity set"],                        "category": "concept"},
            "relationship":  {"importance": 9,  "aliases": ["relationship set"],                  "category": "concept"},
            "attribute":     {"importance": 8,  "aliases": [],                                    "category": "concept"},
            "cardinality":   {"importance": 8,  "aliases": ["cardinality ratio"],                 "category": "concept"},
            "primary key":   {"importance": 7,  "aliases": ["key attribute"],                     "category": "concept"},
            "weak entity":   {"importance": 6,  "aliases": [],                                    "category": "concept"},
        },
        "graph": {
            "er model":     {"entity": 1.0, "relationship": 1.0, "attribute": 0.90, "cardinality": 0.85},
            "entity":       {"primary key": 0.90, "attribute": 0.85, "weak entity": 0.75},
            "relationship": {"cardinality": 0.90, "participation": 0.80},
        },
        "verbs": ["model", "design", "represent", "map", "define"],
        "contexts": ["database design", "schema design", "conceptual modeling"],
        "related_topics": ["normalization", "sql", "relational model"],
    },

    "ipv4": {
        "domain": "computer networks",
        "subject": "ip addressing",
        "subtopic": "internet protocol version 4",
        "concepts": {
            "ipv4":       {"importance": 10, "aliases": ["internet protocol version 4", "ip address"], "category": "protocol"},
            "subnet":     {"importance": 9,  "aliases": ["subnetting", "subnet mask"],                 "category": "concept"},
            "cidr":       {"importance": 8,  "aliases": ["classless inter-domain routing"],            "category": "standard"},
            "routing":    {"importance": 8,  "aliases": ["routing table"],                             "category": "concept"},
            "nat":        {"importance": 7,  "aliases": ["network address translation"],               "category": "concept"},
            "packet":     {"importance": 7,  "aliases": ["datagram", "ip packet"],                     "category": "concept"},
            "header":     {"importance": 6,  "aliases": ["ip header"],                                 "category": "concept"},
        },
        "graph": {
            "ipv4":   {"subnet": 1.0, "routing": 0.90, "packet": 0.85, "nat": 0.80},
            "subnet": {"cidr": 0.90,  "subnet mask": 0.90, "network address": 0.80},
        },
        "verbs": ["address", "route", "fragment", "forward", "assign"],
        "contexts": ["network addressing", "packet routing", "ip fragmentation"],
        "related_topics": ["ipv6", "routing protocols", "tcp"],
    },
}

def _position_importance(idx: int, total: int) -> float:
    if total == 0:
        return 5.0
    norm = 1.0 - (idx / max(total - 1, 1))
    return round(3.0 + norm * 7.0, 1)

def _graph_centrality(concept: str, graph: dict) -> float:
    total_nodes = len(graph)
    if total_nodes == 0:
        return 0.0
    referencing = sum(1 for edges in graph.values() if concept in edges)
    return referencing / total_nodes

def _compute_importance(position_score: float, graph: dict, concept: str, manual_boost: float = 0.0) -> int:
    freq = 1.0
    centrality = _graph_centrality(concept, graph)
    raw = (
        config.IMPORTANCE_WEIGHT_POSITION   * position_score
        + config.IMPORTANCE_WEIGHT_FREQUENCY  * freq
        + config.IMPORTANCE_WEIGHT_CENTRALITY * centrality
        + config.IMPORTANCE_WEIGHT_MANUAL     * manual_boost
    )
    return max(1, min(10, round(raw)))

def _build_auto_entry(domain_key: str, subject_key: str, topic_key: str, keywords: list) -> dict:
    total = len(keywords)
    concepts: dict = {}
    for idx, kw in enumerate(keywords):
        pos_score = _position_importance(idx, total)
        imp = max(1, min(10, round(pos_score)))
        concepts[kw.lower()] = {"importance": imp, "aliases": [], "category": "concept"}

    return {
        "domain":   domain_key,
        "subject":  subject_key,
        "subtopic": topic_key,
        "concepts": concepts,
        "graph":    {},
        "verbs":    [],
        "contexts": [],
        "related_topics": [],
    }

def _build_cache() -> dict:
    cache: dict = {}
    # 1. Auto-generate from TOPIC_MAP
    for domain_key, topics in TOPIC_MAP.items():
        for topic_key, keywords in topics.items():
            entry = _build_auto_entry(domain_key, domain_key, topic_key, keywords)
            cache[topic_key.lower()] = entry

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

    # 2. Apply manual supplements (merge with auto-generated)
    for supp_key, supplement in _SUPPLEMENTS.items():
        target_topic = supplement_mapping.get(supp_key.lower())
        if not target_topic:
            target_topic = supp_key.lower()

        existing = cache.get(target_topic, {})
        
        merged = {}
        merged["domain"] = supplement.get("domain", existing.get("domain", ""))
        merged["subject"] = supplement.get("subject", existing.get("subject", ""))
        merged["subtopic"] = target_topic
        
        # Merge concepts
        merged_concepts = {**existing.get("concepts", {})}
        for concept_name, concept_meta in supplement.get("concepts", {}).items():
            merged_concepts[concept_name.lower()] = concept_meta
        merged["concepts"] = merged_concepts
        
        # Merge graph
        merged_graph = {**existing.get("graph", {})}
        for src, edges in supplement.get("graph", {}).items():
            merged_graph[src.lower()] = {k.lower(): v for k, v in edges.items()}
        merged["graph"] = merged_graph
        
        # Merge other attributes
        merged["verbs"] = list(set(existing.get("verbs", []) + supplement.get("verbs", [])))
        merged["contexts"] = list(set(existing.get("contexts", []) + supplement.get("contexts", [])))
        merged["related_topics"] = list(set(existing.get("related_topics", []) + supplement.get("related_topics", [])))

        # Re-compute importance with graph centrality
        graph = merged.get("graph", {})
        if graph:
            for concept_key, concept_entry in merged.get("concepts", {}).items():
                pos_score = _position_importance(
                    list(merged["concepts"].keys()).index(concept_key),
                    len(merged["concepts"])
                )
                imp = _compute_importance(pos_score, graph, concept_key, manual_boost=1.0)
                concept_entry["importance"] = imp
        cache[target_topic] = merged
        if target_topic != supp_key.lower():
            cache[supp_key.lower()] = merged

    return cache

CANONICAL_TO_RAW_TOPIC = {
    "acid properties": "transactions",
    "ai ethics": "expert systems",
    "arp": "ip addressing",
    "avl tree": "trees",
    "advanced tree structures": "trees",
    "agile methodology": "software development life cycle",
    "asymmetric cryptography": "cryptography",
    "authentication": "network security",
    "bias-variance tradeoff": "model evaluation",
    "binary search tree": "trees",
    "cpu scheduling": "process management",
    "cache data structures": "linear structures",
    "classification algorithms": "supervised learning",
    "computer vision": "search algorithms",
    "congestion control": "transport protocols",
    "consistency models": "consensus protocols",
    "convolutional neural networks": "neural networks",
    "cryptographic key management": "cryptography",
    "dhcp": "ip addressing",
    "data anomalies": "normalization",
    "database optimisation": "indexing",
    "database selection": "nosql systems",
    "database sharding": "system scalability",
    "deadlock": "deadlocks",
    "deadlock avoidance": "deadlocks",
    "deadlock detection": "deadlocks",
    "design patterns": "design patterns",
    "devops and ci/cd": "software development life cycle",
    "distributed synchronisation": "consensus protocols",
    "distributed transactions": "transactions",
    "ensemble methods": "supervised learning",
    "event-driven architecture": "microservices architecture",
    "expert systems": "expert systems",
    "feature engineering": "data preprocessing",
    "game tree search": "search algorithms",
    "gradient descent": "supervised learning",
    "graph algorithms": "graph algorithms",
    "graph representation": "graphs",
    "graph traversal": "graph algorithms",
    "hash tables": "hashing",
    "heaps": "trees",
    "ip addressing": "ip addressing",
    "indexing": "indexing",
    "intrusion detection": "threats and attacks",
    "knowledge representation": "knowledge representation",
    "learning paradigms": "supervised learning",
    "linear data structures": "linear structures",
    "memory management": "memory management",
    "microservices architecture": "microservices architecture",
    "multi-agent systems": "search algorithms",
    "network design": "network security",
    "network security architecture": "network security",
    "normalization": "normalization",
    "osi model": "osi model",
    "optimisation methods": "algorithm analysis",
    "page replacement": "memory management",
    "primary key": "normalization",
    "probabilistic classifiers": "supervised learning",
    "process synchronisation": "process management",
    "protocol design": "transport protocols",
    "query optimisation": "sql",
    "query processing": "sql",
    "real-time scheduling": "process management",
    "reinforcement learning": "unsupervised learning",
    "requirements engineering": "system modeling",
    "routing algorithms": "routing protocols",
    "routing protocols": "routing protocols",
    "sdn": "routing protocols",
    "solid principles": "design patterns",
    "sql injection": "web security",
    "schema design": "er model",
    "search algorithms": "search algorithms",
    "security architecture": "network security",
    "sequence models": "neural networks",
    "session management": "backend development",
    "software architecture": "design patterns",
    "software design principles": "design patterns",
    "software development methodology": "software development life cycle",
    "software quality": "testing and qa",
    "sorting algorithms": "sorting and searching",
    "stack and queue": "linear structures",
    "stored procedures": "sql",
    "subnetting": "ip addressing",
    "tcp connection": "transport protocols",
    "tls and pki": "cryptography",
    "testing strategies": "testing and qa",
    "transaction isolation": "transactions",
    "transport layer protocols": "transport protocols",
    "trie": "trees",
    "uml modelling": "system modeling",
    "version control": "software development life cycle",
    "virtual memory": "memory management"
}

class MappedDict(dict):
    def get(self, key, default=None):
        if isinstance(key, str):
            k_clean = key.lower().strip()
            mapped = CANONICAL_TO_RAW_TOPIC.get(k_clean, k_clean)
            return super().get(mapped, default)
        return super().get(key, default)

    def __getitem__(self, key):
        if isinstance(key, str):
            k_clean = key.lower().strip()
            mapped = CANONICAL_TO_RAW_TOPIC.get(k_clean, k_clean)
            return super().__getitem__(mapped)
        return super().__getitem__(key)

    def __contains__(self, key):
        if isinstance(key, str):
            k_clean = key.lower().strip()
            mapped = CANONICAL_TO_RAW_TOPIC.get(k_clean, k_clean)
            return super().__contains__(mapped)
        return super().__contains__(key)

# Build once at import time
_KNOWLEDGE_CACHE: dict = MappedDict(_build_cache())

# O(1) Indexes
_CONCEPT_TO_TOPIC:  dict = {}
_CONCEPT_TO_DOMAIN: dict = {}
_ALIAS_TO_CANONICAL: dict = {}

def _build_indexes() -> None:
    for topic_key, entry in _KNOWLEDGE_CACHE.items():
        domain_key = entry.get("domain", "")
        for concept_key, meta in entry.get("concepts", {}).items():
            if concept_key not in _CONCEPT_TO_TOPIC:
                _CONCEPT_TO_TOPIC[concept_key]  = topic_key
                _CONCEPT_TO_DOMAIN[concept_key] = domain_key
            for alias in meta.get("aliases", []):
                _ALIAS_TO_CANONICAL[alias.lower()] = concept_key

_build_indexes()

def get_topic_entry(topic: str) -> Optional[dict]:
    return _KNOWLEDGE_CACHE.get(topic.lower().strip())

def get_concept_weight(topic: str, concept: str) -> float:
    entry = _KNOWLEDGE_CACHE.get(topic.lower().strip())
    if not entry:
        return 0.0
    concept_lower = concept.lower().strip()
    graph = entry.get("graph", {})
    for _src, edges in graph.items():
        if concept_lower in edges:
            return float(edges[concept_lower])
    concept_meta = entry.get("concepts", {}).get(concept_lower)
    if concept_meta:
        return round(concept_meta["importance"] / 10.0, 2)
    return 0.0

def get_concept_graph(topic: str) -> dict:
    entry = _KNOWLEDGE_CACHE.get(topic.lower().strip())
    if not entry:
        return {}
    return entry.get("graph", {})

def get_concept_meta(topic: str, concept: str) -> Optional[dict]:
    entry = _KNOWLEDGE_CACHE.get(topic.lower().strip())
    if not entry:
        return None
    concept_lower = concept.lower().strip()
    meta = entry.get("concepts", {}).get(concept_lower)
    if meta:
        return meta
    canonical = _ALIAS_TO_CANONICAL.get(concept_lower)
    if canonical:
        return entry.get("concepts", {}).get(canonical)
    return None

def resolve_concept_alias(concept: str) -> str:
    return _ALIAS_TO_CANONICAL.get(concept.lower().strip(), concept.lower().strip())

def find_topic_for_concept(concept: str) -> Optional[str]:
    canonical = resolve_concept_alias(concept)
    return _CONCEPT_TO_TOPIC.get(canonical)

def find_domain_for_concept(concept: str) -> Optional[str]:
    canonical = resolve_concept_alias(concept)
    return _CONCEPT_TO_DOMAIN.get(canonical)

def get_related_topics(topic: str) -> list:
    entry = _KNOWLEDGE_CACHE.get(topic.lower().strip())
    if not entry:
        return []
    return entry.get("related_topics", [])

def cache_stats() -> dict:
    supplemented = [k for k in _SUPPLEMENTS if k in _KNOWLEDGE_CACHE]
    return {
        "entries":           len(_KNOWLEDGE_CACHE),
        "supplemented":      len(supplemented),
        "auto_generated":    len(_KNOWLEDGE_CACHE) - len(supplemented),
        "concept_index_size": len(_CONCEPT_TO_TOPIC),
        "alias_index_size":  len(_ALIAS_TO_CANONICAL),
        "version":           getattr(config, "KNOWLEDGE_VERSION", "2.0"),
    }


def compare_topics(source_profile, candidate_profile) -> str:
    """
    Compares the topics of source and candidate profiles.
    Returns:
    - 'same_topic'
    - 'related_topic'
    - 'same_domain'
    - 'different_domain'
    """
    if not source_profile or not candidate_profile:
        return "different_domain"
        
    src_topic = getattr(source_profile, "topic", "") or ""
    cand_topic = getattr(candidate_profile, "topic", "") or ""
    
    src_topic_clean = src_topic.strip().lower()
    cand_topic_clean = cand_topic.strip().lower()
    
    if src_topic_clean == cand_topic_clean:
        return "same_topic"
        
    related_to_src = [t.strip().lower() for t in get_related_topics(src_topic)]
    related_to_cand = [t.strip().lower() for t in get_related_topics(cand_topic)]
    
    if cand_topic_clean in related_to_src or src_topic_clean in related_to_cand:
        return "related_topic"
        
    src_domain = getattr(source_profile, "domain", "") or ""
    cand_domain = getattr(candidate_profile, "domain", "") or ""
    
    if src_domain.strip().lower() == cand_domain.strip().lower():
        return "same_domain"
        
    return "different_domain"

