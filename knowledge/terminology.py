from knowledge.concepts import normalize_concept

TECHNICAL_TERMINOLOGY = {
    "breadth first search": {
        "preferred": ["graph", "vertex", "queue", "traversal"],
        "supporting": ["adjacency list", "shortest path"],
        "weak": ["dataset", "element", "collection", "record"],
        "minimum_preferred": 2
    },
    "depth first search": {
        "preferred": ["graph", "vertex", "stack", "traversal"],
        "supporting": ["backtracking", "recursion", "cycle detection"],
        "weak": ["dataset", "element", "collection", "list"],
        "minimum_preferred": 2
    },
    "binary search": {
        "preferred": ["sorted array", "midpoint", "interval"],
        "supporting": ["divide and conquer", "search space"],
        "weak": ["list search", "linear lookup"],
        "minimum_preferred": 2
    },
    "merge sort": {
        "preferred": ["divide and conquer", "merge", "subarray"],
        "supporting": ["recursion", "stable sort", "auxiliary space"],
        "weak": ["order list", "sorting process"],
        "minimum_preferred": 2
    },
    "quick sort": {
        "preferred": ["pivot", "partition", "divide and conquer"],
        "supporting": ["unstable sort", "recursion", "in-place"],
        "weak": ["order list", "sorting process"],
        "minimum_preferred": 2
    },
    "dijkstra": {
        "preferred": ["shortest path", "priority queue", "relaxation"],
        "supporting": ["weighted graph", "greedy algorithm", "vertex", "edge"],
        "weak": ["distance path", "node list", "route planner"],
        "minimum_preferred": 2
    },
    "entity relationship model": {
        "preferred": ["entity", "attribute", "relationship"],
        "supporting": ["cardinality", "primary key", "foreign key", "diagram"],
        "weak": ["data box", "table lines", "link map"],
        "minimum_preferred": 2
    },
    "normalization": {
        "preferred": ["functional dependency", "decomposition", "anomaly"],
        "supporting": ["1nf", "2nf", "3nf", "bcnf", "redundancy"],
        "weak": ["dataset", "element", "item", "process"],
        "minimum_preferred": 2
    },
    "indexing": {
        "preferred": ["b tree", "database", "query"],
        "supporting": ["clustered", "non clustered", "index"],
        "weak": ["file system", "storage", "list"],
        "minimum_preferred": 2
    },
    "transactions": {
        "preferred": ["atomicity", "consistency", "isolation", "durability"],
        "supporting": ["transaction", "commit", "rollback", "concurrency"],
        "weak": ["database stability", "operation sequence", "run steps"],
        "minimum_preferred": 2
    },
    "cpu scheduling": {
        "preferred": ["turnaround time", "waiting time", "scheduler"],
        "supporting": ["gantt chart", "process", "preemptive", "quantum", "context switch"],
        "weak": ["task list", "job array", "timer", "system process"],
        "minimum_preferred": 2
    },
    "paging": {
        "preferred": ["page table", "frame", "page fault"],
        "supporting": ["tlb", "address translation", "physical memory", "logical address"],
        "weak": ["ram extension", "disk blocks", "memory slices"],
        "minimum_preferred": 2
    },
    "deadlock": {
        "preferred": ["mutex", "semaphore", "mutual exclusion"],
        "supporting": ["hold and wait", "circular wait", "no preemption", "banker's algorithm"],
        "weak": ["halt", "freeze", "stuck", "wait loop"],
        "minimum_preferred": 2
    },
    "open systems interconnection": {
        "preferred": ["protocol", "layer", "interface"],
        "supporting": ["physical", "data link", "network", "transport", "session", "presentation", "application"],
        "weak": ["system interface", "connection levels", "network model"],
        "minimum_preferred": 2
    },
    "transmission control protocol": {
        "preferred": ["handshake", "packet", "segment"],
        "supporting": ["port", "connection", "reliability", "ip"],
        "weak": ["internet rules", "web lines", "data channels"],
        "minimum_preferred": 2
    },
    "internet protocol version 4": {
        "preferred": ["subnet", "cidr", "addressing"],
        "supporting": ["ipv4", "ipv6", "mask", "gateway", "dhcp"],
        "weak": ["computer number", "net address", "network digits"],
        "minimum_preferred": 2
    },
    "domain name system": {
        "preferred": ["domain name", "resolution", "nameserver"],
        "supporting": ["ip address", "resolver", "cname", "record", "cache"],
        "weak": ["web looker", "name finder", "address site"],
        "minimum_preferred": 2
    },
    "lexical analysis": {
        "preferred": ["token", "lexer", "scanner"],
        "supporting": ["regular expression", "finite automata", "symbol table"],
        "weak": ["word reader", "text parser", "line splitter"],
        "minimum_preferred": 2
    },
    "syntax analysis": {
        "preferred": ["parser", "syntax tree", "context free grammar"],
        "supporting": ["cfg", "derivation", "ambiguity", "production rule"],
        "weak": ["sentence checker", "grammar rules", "text validator"],
        "minimum_preferred": 2
    }
}

def get_topic_terminology(topic: str) -> dict:
    if not topic:
        return None
    normalized = normalize_concept(topic)
    
    # Check if there is an exact match
    res = TECHNICAL_TERMINOLOGY.get(normalized)
    if res:
        return res
        
    local_aliases = {
        "process scheduling": "cpu scheduling",
        "tcp/ip": "transmission control protocol",
        "tcp": "transmission control protocol",
        "osi model": "open systems interconnection",
        "osi": "open systems interconnection",
        "er model": "entity relationship model",
        "erd": "entity relationship model",
        "er diagram": "entity relationship model",
        "dns": "domain name system",
        "ipv4": "internet protocol version 4"
    }
    alias = local_aliases.get(normalized)
    if alias:
        return TECHNICAL_TERMINOLOGY.get(alias)
    return None

def is_term_present_in_profile(term: str, cand_profile) -> bool:
    if not cand_profile:
        return False
    term_lower = term.lower()
    
    concepts = getattr(cand_profile, "concepts", []) or []
    for c in concepts:
        if term_lower in c.lower():
            return True
            
    entities = getattr(cand_profile, "technical_entities", []) or []
    for e in entities:
        if term_lower in e.lower():
            return True
            
    keywords = getattr(cand_profile, "keywords", []) or []
    for k in keywords:
        if term_lower == k.lower():
            return True
            
    noun_chunks = getattr(cand_profile, "noun_chunks", []) or []
    for nc in noun_chunks:
        if term_lower in nc.lower():
            return True
            
    norm_q = getattr(cand_profile, "normalized_question", "") or ""
    if term_lower in norm_q.lower():
        return True
        
    return False
