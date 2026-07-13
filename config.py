"""
BloomAI Configuration Module
This file contains all tunable parameters for the generation pipeline,
validation thresholds, and retry limits. It supports multiple modes for
benchmarking and comparison.
"""

DEBUG = False

# ---------------------------------------------------------------------------
# Domain keyword mapping used by infer_domain()
# ---------------------------------------------------------------------------
DOMAIN_MAP = {

    "database management systems": [
        "sql",
        "database",
        "normalization",
        "transaction",
        "acid",
        "index",
        "join",
        "nosql",
        "mongodb",
        "relational"
    ],

    "computer networks": [
        "tcp",
        "udp",
        "ip",
        "ipv4",
        "ipv6",
        "router",
        "switch",
        "network",
        "protocol",
        "osi",
        "http",
        "https",
        "dns"
    ],

    "operating systems": [
        "process",
        "thread",
        "cpu scheduling",
        "deadlock",
        "paging",
        "virtual memory",
        "kernel",
        "mutex",
        "semaphore"
    ],

    "machine learning": [
        "classification",
        "regression",
        "clustering",
        "decision tree",
        "random forest",
        "svm",
        "neural network",
        "training"
    ],

    "artificial intelligence": [
        "expert system",
        "knowledge representation",
        "search algorithm",
        "agent",
        "reasoning",
        "heuristic"
    ],

    "compiler design": [
        "lexer",
        "parser",
        "grammar",
        "syntax",
        "semantic analysis",
        "intermediate code"
    ],

    "computer graphics": [
        "dda",
        "bresenham",
        "polygon",
        "clipping",
        "transformation",
        "viewport"
    ],

    "cloud computing": [
        "virtualization",
        "docker",
        "kubernetes",
        "iaas",
        "paas",
        "saas",
        "vm"
    ],

    "big data analytics": [
        "hadoop",
        "spark",
        "mapreduce",
        "hdfs",
        "data warehouse"
    ],

    "internet of things": [
        "iot",
        "sensor",
        "actuator",
        "mqtt",
        "embedded"
    ],

    "software engineering": [
        "sdlc",
        "requirement",
        "testing",
        "uml",
        "maintenance",
        "agile"
    ],

    "computer architecture": [
        "pipeline",
        "cache",
        "instruction",
        "risc",
        "cisc",
        "alu"
    ],

    "computer organization": [
        "register",
        "memory",
        "bus",
        "control unit",
        "cpu"
    ],

    "digital electronics": [
        "flip flop",
        "logic gate",
        "boolean",
        "multiplexer",
        "decoder"
    ],

    "data structures": [
        "array",
        "linked list",
        "stack",
        "queue",
        "tree",
        "graph",
        "heap",
        "hash table"
    ],

    "design and analysis of algorithms": [
        "dynamic programming",
        "greedy",
        "divide and conquer",
        "complexity",
        "big o",
        "recurrence"
    ],

    "c programming": [
        "pointer",
        "structure",
        "malloc",
        "function",
        "recursion"
    ],

    "python programming": [
        "python",
        "list",
        "tuple",
        "dictionary",
        "decorator"
    ],

    "java programming": [
        "java",
        "jvm",
        "inheritance",
        "interface",
        "exception"
    ],

    "management information systems": [
        "mis",
        "information system",
        "business process",
        "erp",
        "crm"
    ]
}

# ---------------------------------------------------------------------------
# Concept Synonym Dictionary  (Req. 1 — Stage 2 semantic matching)
# Each key maps to a list of acceptable synonyms. Matching any synonym
# counts as a successful keyword match for concept validation.
# ---------------------------------------------------------------------------
CONCEPT_SYNONYMS = {
    "database": ["db", "data store", "data storage", "rdbms"],
    "normalization": ["normalisation", "normal form", "normalizing", "1nf", "2nf", "3nf", "bcnf", "normal forms"],
    "authentication": ["login", "login verification", "auth", "sign-in", "signin"],
    "classification": ["categorization", "categorisation", "labeling", "labelling"],
    "index": ["indexing", "indexed", "b-tree index", "b+tree"],
    "encryption": ["cryptography", "cipher", "encrypted", "ciphertext", "decryption"],
    "transaction": ["commit", "rollback", "acid"],
    "redundancy": ["duplication", "redundant", "duplicate data"],
    "redundant": ["redundancy", "duplication", "duplicate data"],
    "query": ["sql query", "select", "dml", "dql"],
    "network": ["networking", "net", "communication"],
    "process": ["processes", "processing", "processor"],
    "thread": ["threading", "multithreading", "concurrent"],
    "deadlock": ["deadlocked", "circular wait", "starvation"],
    "scheduling": ["scheduler", "cpu scheduling", "round robin", "priority"],
    "regression": ["linear regression", "logistic regression", "prediction model"],
    "clustering": ["k-means", "cluster analysis", "unsupervised"],
    "neural network": ["deep learning", "ann", "artificial neural", "cnn", "rnn"],
    "firewall": ["packet filter", "network security", "perimeter security"],
    "hash": ["hashing", "hash function", "md5", "sha"],
    "btree": ["b-tree", "b+tree", "balanced tree", "binary search tree"],
    "tradeoff": ["trade-off", "trade offs", "tradeoffs", "comparison"],
    "commit": ["commit operation", "transaction commit", "acid"],
    "rollback": ["rollback operation", "undo", "abort"],
    "acid": ["atomicity", "consistency", "isolation", "durability", "atomicity consistency isolation durability"],
    "atomicity": ["acid"],
    "consistency": ["acid"],
    "isolation": ["acid"],
    "durability": ["acid"],
    "nosql": ["no-sql", "non-relational", "document store", "mongodb", "non relational"],
    "non-relational": ["nosql", "no-sql", "document store", "non relational"],
    "non relational": ["nosql", "no-sql", "document store", "non-relational"],
    "relational": ["rdbms", "relational model", "relational database", "sql"],
    "sql": ["relational", "sql query", "select"],
}

# ---------------------------------------------------------------------------
# Semantic Similarity Thresholds  (Req. 1 — Stage 3)
# ---------------------------------------------------------------------------
CONCEPT_SEMANTIC_THRESHOLD = 0.75   # cosine similarity floor to accept a match
DUPLICATE_SEMANTIC_THRESHOLD = 0.93  # cosine similarity ceiling to flag a duplicate
DUPLICATE_FINAL_ROUND_THRESHOLD = 0.97  # relaxed ceiling used in the final generation round

# ---------------------------------------------------------------------------
# Validation Engine Scores & Thresholds
# ---------------------------------------------------------------------------
PASS_THRESHOLD = 80.0
BLOOM_STAGE_SCORE = 35.0
CONCEPT_STAGE_SCORE = 25.0
ENTITY_SCORE = 15.0
SEMANTIC_SCORE = 10.0
NUMBER_SCORE = 5.0
DUPLICATE_SCORE = 5.0
GRAMMAR_SCORE = 5.0

MIN_CONTENT_WORDS = 2
ENTITY_PENALTY = 0.2
CONCEPT_COMPOUND_WEIGHT = 1.5
ENTITY_RELATED_THRESHOLD = 0.60

TECH_ENTITY_DICTIONARY = [
    "sql", "dbms", "mongodb", "postgresql", "redis", "kafka", "docker",
    "kubernetes", "tensorflow", "pytorch", "opencv", "numpy", "pandas",
    "react", "angular", "node.js", "flask", "django", "linux", "unix",
    "tcp", "udp", "ipv4", "ipv6", "http", "https", "rest api", "graphql",
    "aes", "rsa", "sha", "oauth", "jwt", "json", "xml", "html", "css",
    "javascript", "python", "java", "c++", "c#", ".net"
]


# ---------------------------------------------------------------------------
# Bloom Verb Profiles  (Req. 3 — replaces hardcoded forbidden-word sets)
# Each profile defines:
#   allowed_start_verbs  — acceptable first-word verbs (None = any allowed)
#   forbidden_start_verbs — verbs that must NOT appear as the first word
#   forbidden_body_verbs  — verbs that must NOT appear anywhere in the question
#   evaluate_indicators   — words that indicate the wrong cognitive level
# ---------------------------------------------------------------------------
BLOOM_PROFILES = {
    "Remember": {
        "allowed_start_verbs": {
            "define", "list", "state", "recall", "name", "identify",
            "mention", "label", "what", "which",
        },
        "forbidden_start_verbs": set(),
        "forbidden_body_verbs": set(),
        "evaluate_indicators": set(),
    },
    "Understand": {
        "allowed_start_verbs": None,  # Any start verb acceptable
        "forbidden_start_verbs": {
            "apply", "implement", "execute", "demonstrate", "use",
        },
        "forbidden_body_verbs": {
            "design", "develop", "create", "evaluate", "analyze",
            "enhance", "enhances", "enhanced", "enhancing",
            "optimize", "optimizes", "optimized", "optimizing",
            "deploy", "deploys", "deployed", "deploying",
            "executes", "executed", "executing",
            "implements", "implemented", "implementing",
        },
        "evaluate_indicators": set(),
    },
    "Apply": {
        "allowed_start_verbs": None,
        "forbidden_start_verbs": {
            "evaluate", "assess", "critique", "judge", "justify",
            "design", "develop", "create", "formulate",
        },
        "forbidden_body_verbs": {
            "design", "develop", "create", "evaluate", "assess",
            "critique", "formulate", "propose",
        },
        "evaluate_indicators": set(),
    },
    "Analyze": {
        "allowed_start_verbs": None,
        "forbidden_start_verbs": {
            "evaluate", "assess", "judge", "justify", "recommend",
        },
        "forbidden_body_verbs": {
            "design", "develop", "create", "evaluate", "assess", "critique",
        },
        "evaluate_indicators": {
            "suitable", "appropriate", "best", "optimal",
            "recommend", "recommended",
        },
    },
    "Evaluate": {
        "allowed_start_verbs": None,
        "forbidden_start_verbs": {
            "design", "develop", "construct", "formulate", "propose", "create",
        },
        "forbidden_body_verbs": {
            "design", "develop", "create", "construct",
            "formulate", "propose", "architect", "build",
        },
        "evaluate_indicators": set(),
    },
    "Create": {
        "allowed_start_verbs": None,
        "forbidden_start_verbs": {
            "evaluate", "assess", "critique", "judge", "justify", "describe",
        },
        "forbidden_body_verbs": {
            "evaluate", "assess", "critique", "judge",
        },
        "evaluate_indicators": set(),
    },
}

# ---------------------------------------------------------------------------
# Generation Mode — Mode E (Multi-Candidate Ranking) is the sole active mode.
# ---------------------------------------------------------------------------
MODES = {
    "Mode E (Multi-Candidate Ranking)": {
        "mode_name": "Mode E (Multi-Candidate Ranking)",
        # Generation Parameters
        "num_beams": 8,
        "repetition_penalty": 2.5,
        "no_repeat_ngram_size": 4,
        "length_penalty": 1.2,
        # Mode E uses sampling; max_new_tokens capped at 40 for efficiency
        "max_new_tokens": 40,
        # Validation Thresholds
        "minimum_confidence": 90.0,
        "minimum_confidence_by_bloom": {
            "Remember": 90.0,
            "Understand": 90.0,
            "Apply": 90.0,
            "Analyze": 89.0,
            "Evaluate": 88.0,
            "Create": 87.0,
        },
        "duplicate_threshold_recent": 0.85,
        "duplicate_threshold_session": 0.95,
        "concept_threshold_short": 1,
        "concept_threshold_long": 2,
        # Retry Limits (per Bloom level)
        "create_attempts": 10,
        "evaluate_attempts": 8,
        "analyze_attempts": 8,
        "apply_attempts": 6,
        "understand_attempts": 5,
        "remember_attempts": 5,
        # Behavior Flags
        "progressive_concept_reinforcement": True,
        "session_history_length": 10,
        # Mode E — Multi-Candidate Sampling Parameters
        "num_return_sequences": 3,
        "max_generation_rounds": 4,
        "candidate_selection": "ranking",
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.95,
    },
}

# Active mode — permanently set to Mode E
ACTIVE_MODE = "Mode E (Multi-Candidate Ranking)"

# ---------------------------------------------------------------------------
# Centralized Lists, Maps, Penalties and Thresholds
# ---------------------------------------------------------------------------
ABBREVIATION_MAP = {
    "dbms": "database management system",
    "rdbms": "relational database management system",
    "sql": "structured query language",
    "tcp": "transmission control protocol",
    "udp": "user datagram protocol",
    "bcnf": "boyce-codd normal form",
    "3nf": "third normal form",
    "2nf": "second normal form",
    "1nf": "first normal form",
    "osi": "open systems interconnection",
    "http": "hypertext transfer protocol",
    "https": "hypertext transfer protocol secure",
    "api": "application programming interface",
    "json": "javascript object notation",
    "xml": "extensible markup language",
    "ipv4": "internet protocol version 4",
    "ipv6": "internet protocol version 6"
}

CONCEPT_IGNORE_WORDS = {
    "question", "difference", "comparison", "example", "program", "code", "concept", "theory", "following", 
    "purpose", "term", "role", "process", "system", "type", "method", "class", "function", "value", 
    "implementation", "scenario", "problem", "solution", "need", "reason", "step", "way"
}

ENTITY_IGNORE_WORDS = {
    "what", "how", "why", "write", "design", "explain", "describe", "discuss", "evaluate", "compare", 
    "list", "define", "question", "program", "code", "database", "data", "concept", "example", 
    "following", "difference", "comparison"
}

REPETITION_IGNORE_WORDS = {
    "a", "an", "the", "to", "in", "for", "on", "of", "with", "between",
    "it", "its", "their", "them", "this", "that", "these", "those",
    "and", "or", "by", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "how", "why", "what",
    "where", "when", "who", "which", "about", "at", "from", "into",
    "through", "during", "including", "until", "against", "among",
    "throughout", "despite", "towards", "upon", "concerning", "up",
    "over", "after", "whether", "more", "less", "can", "could", "should",
    "would", "will", "shall", "may", "might", "must", "whose", "whom"
}

NUM_CANDIDATES_BY_BLOOM = {
    "Remember": 2,
    "Understand": 2,
    "Apply": 3,
    "Analyze": 4,
    "Evaluate": 5,
    "Create": 6
}

BLOOM_VERB_PENALTY = 2.0
CONCEPT_PHRASE_SIMILARITY_THRESHOLD = 0.82

DUPLICATE_IGNORE_BLOOM_VERBS = {
    "define", "list", "state", "recall", "name", "explain", "describe", "summarize", 
    "interpret", "discuss", "apply", "implement", "use", "execute", "demonstrate", 
    "analyze", "compare", "differentiate", "investigate", "examine", "evaluate", 
    "assess", "critique", "justify", "judge", "design", "develop", "construct", 
    "formulate", "propose", "what", "how", "why"
}

ALL_BLOOM_VERBS = {
    "define", "list", "state", "recall", "name", "identify", "mention",
    "label", "what", "which", "explain", "describe", "summarize",
    "interpret", "discuss", "apply", "implement", "execute", "demonstrate",
    "use", "analyze", "compare", "differentiate", "examine", "investigate",
    "evaluate", "assess", "critique", "justify", "judge", "recommend",
    "design", "develop", "construct", "formulate", "propose", "create"
}

NUMBER_PATTERNS = [
    r'\bIPV\d+\b',
    r'\bAES-\d+\b',
    r'\bSHA-\d+\b',
    r'\b802\.\d+[A-Z]?\b',
    r'\b\d+-BIT\b',
    r'\b\d+\s*(?:GHZ|MHZ|HZ|MBPS|KBPS|GBPS|KB|MB|GB|TB)\b'
]

# Grammar validator legitimate repeated words
GRAMMAR_LEGIT_REPEATS = {
    "learning", "network", "system", "data", "peer", "node", "model", "server"
}

# Entity validator similarity threshold
ENTITY_SIMILARITY_THRESHOLD = 0.90



