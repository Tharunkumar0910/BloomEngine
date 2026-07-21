import config

# Normalized domain mapping and subject mapping
NORMALIZED_DOMAIN_MAP = {}
DOMAIN_SUBJECT_MAP = {}

for domain, value in config.DOMAIN_MAP.items():
    domain_lower = domain.lower()
    merged_keywords = []
    subject_map = {}

    # New hierarchical format
    if isinstance(value, dict):
        for subject, keywords in value.items():
            subject_map[subject] = [
                keyword.lower()
                for keyword in keywords
            ]
            merged_keywords.extend(keywords)
    # Old flat format
    else:
        merged_keywords = value

    DOMAIN_SUBJECT_MAP[domain_lower] = subject_map
    NORMALIZED_DOMAIN_MAP[domain_lower] = sorted(
        set(keyword.lower() for keyword in merged_keywords)
    )

# Extend with the missing domains to match the full list of 27 domains
EXTENDED_DOMAINS = {
    "mobile computing": [
        "android", "ios", "cellular", "5g", "lte", "gsm", "gps", "mobile app", "wireless", "mobile architecture"
    ],
    "natural language processing": [
        "nlp", "tokenization", "stemming", "lemmatization", "pos tagging", "ner", "bert", "gpt", "word2vec", "embeddings", "transformer", "sentiment analysis", "parsing"
    ],
    "distributed systems": [
        "consensus", "paxos", "raft", "cap theorem", "consistent hashing", "replication", "partitioning", "rpc", "kafka", "zookeeper", "distributed lock"
    ],
    "cyber security": [
        "security", "cryptography", "encryption", "decryption", "cipher", "aes", "des", "rsa", "sha", "malware", "virus", "firewall", "ids", "ips", "buffer overflow", "sql injection", "xss", "phishing", "authentication", "authorization"
    ],
    "web technologies": [
        "html", "css", "javascript", "js", "dom", "ajax", "react", "angular", "vue", "node.js", "express", "rest api", "soap", "json", "xml", "cookies", "session"
    ],
    "data mining": [
        "data mining", "association rule", "apriori", "frequent pattern", "clustering", "classification", "data preprocessing", "k-means", "dbscan", "outlier detection"
    ],
    "parallel computing": [
        "parallel computing", "cuda", "openmp", "mpi", "concurrency", "multithreading", "race condition", "gpgpu", "shared memory", "distributed memory", "speedup"
    ],
    "human computer interaction": [
        "hci", "human computer interaction", "usability", "user experience", "ux", "ui", "wireframe", "prototype", "interaction design", "heuristics evaluation", "persona"
    ],
    "other computer science": [
        "computer science", "programming", "software", "development", "hardware", "technology", "system", "algorithm", "data"
    ]
}

for domain, keywords in EXTENDED_DOMAINS.items():
    domain_lower = domain.lower()
    if domain_lower not in NORMALIZED_DOMAIN_MAP:
        NORMALIZED_DOMAIN_MAP[domain_lower] = [kw.lower() for kw in keywords]

def get_normalized_domains():
    return NORMALIZED_DOMAIN_MAP

def get_domain_subjects(domain: str):
    return DOMAIN_SUBJECT_MAP.get(domain.lower(), {})

def get_subject_keywords(domain: str, subject: str):
    subjects = DOMAIN_SUBJECT_MAP.get(domain.lower(), {})
    return subjects.get(subject, [])
