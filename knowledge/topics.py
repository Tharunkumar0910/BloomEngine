TOPIC_MAP = {
    "database management systems": {
        "normalization": [
            "normalization", "normal form", "1nf", "2nf", "3nf", "bcnf", "redundancy", "functional dependency",
            "candidate key", "decomposition", "lossless decomposition", "dependency preservation", "partial dependency",
            "transitive dependency", "superkey", "foreign key", "primary key", "determinant", "multivalued dependency",
            "4nf", "5nf", "join dependency", "lossless join", "denormalization", "trivial dependency", "non-trivial dependency",
            "canonical cover", "minimal cover", "attribute closure", "armstrong axioms", "armstrong's axioms"
        ],
        "transactions": [
            "transaction", "acid", "commit", "rollback", "concurrency control", "isolation level", "serializability",
            "read uncommitted", "read committed", "repeatable read", "serializable", "dirty read", "non-repeatable read",
            "phantom read", "write-ahead logging", "wal", "savepoint", "two-phase commit", "2pc", "three-phase commit",
            "3pc", "compensating transaction", "distributed transaction", "dirty write", "lost update", "recovery log"
        ],
        "joins": [
            "join", "inner join", "outer join", "left join", "right join", "natural join", "cross join", "self join",
            "equijoin", "theta join", "semijoin", "antijoin", "hash join", "nested loop join", "merge join", "join condition",
            "cartesian product", "full outer join"
        ],
        "indexing": [
            "index", "indexing", "b-tree", "b+ tree", "hash index", "primary index", "secondary index", "clustered index",
            "non-clustered index", "dense index", "sparse index", "multilevel index", "composite index", "bitmap index",
            "spatial index", "covering index", "indexing overhead", "tree height", "b+tree", "btree", "isam"
        ],
        "sql": [
            "sql", "select", "insert", "update", "delete", "ddl", "dml", "query", "view", "structured query language",
            "alter", "drop", "truncate", "grant", "revoke", "having", "group by", "order by", "aggregate function",
            "subquery", "nested query", "correlated subquery", "union", "intersect", "except", "trigger", "stored procedure",
            "cte", "common table expression"
        ],
        "recovery": [
            "recovery", "log-based recovery", "checkpoint", "shadow paging", "crash recovery", "fuzzy checkpointing",
            "aries recovery", "undo", "redo", "write-ahead log", "log record", "idempotent", "media failure", "transaction rollback",
            "deferred update", "immediate update"
        ],
        "concurrency": [
            "concurrency", "lock", "two-phase locking", "2pl", "timestamp ordering", "deadlock", "shared lock", "exclusive lock",
            "intent lock", "lock conversion", "optimistic concurrency control", "occ", "multiversion concurrency control",
            "mvcc", "phantom problem", "cascading rollback", "strict 2pl", "rigorous 2pl", "thomas write rule", "deadlock detection"
        ],
        "er model": [
            "er model", "entity relationship", "entity relationship diagram", "erd", "attribute", "relationship",
            "cardinality", "participation constraint", "weak entityset", "weak entity", "strong entityset", "strong entity",
            "identifying relationship", "multivalued attribute", "composite attribute", "derived attribute", "specialization",
            "generalization", "aggregation", "key attribute", "degree of relationship"
        ]
    },
    "computer networks": {
        "osi model": [
            "osi model", "physical layer", "data link layer", "network layer", "transport layer", "session layer",
            "presentation layer", "application layer", "open systems interconnection", "pdu", "protocol data unit",
            "encapsulation", "decapsulation", "mac sublayer", "llc sublayer", "frame", "packet", "segment", "datagram",
            "osi", "open systems interconnection model"
        ],
        "routing protocols": [
            "routing", "router", "rip", "ospf", "bgp", "link state", "distance vector", "routing table", "next hop",
            "dijkstra", "bellman-ford", "path vector", "split horizon", "route poisoning", "autonomous system",
            "interior gateway protocol", "exterior gateway protocol", "igp", "egp", "flooding", "link state advertisement"
        ],
        "transport protocols": [
            "tcp", "udp", "handshake", "segment", "congestion control", "flow control", "port", "transmission control protocol",
            "user datagram protocol", "sliding window", "three-way handshake", "syn", "ack", "fin", "rst", "sequence number",
            "acknowledgement number", "window size", "checksum", "selective repeat", "go-back-n", "tcp handshake", "port number"
        ],
        "application protocols": [
            "http", "https", "dns", "ftp", "smtp", "dhcp", "hypertext transfer protocol", "domain name system",
            "file transfer protocol", "simple mail transfer protocol", "dynamic host configuration protocol", "ssh",
            "telnet", "imap", "pop3", "snmp", "mime", "dns resolution", "domain name resolution", "ftp commands"
        ],
        "ip addressing": [
            "ip", "ipv4", "ipv6", "subnet", "subnetting", "mask", "cidr", "classless inter-domain routing", "subnet mask",
            "broadcast address", "loopback address", "private ip", "public ip", "nat", "network address translation",
            "arp", "address resolution protocol", "icmp", "ping", "ip header", "ipv4 header", "ipv6 header"
        ]
    },
    "operating systems": {
        "process management": [
            "process", "thread", "scheduling", "round robin", "fcfs", "sjf", "pcb", "context switch", "process control block",
            "thread control block", "tcb", "preemptive scheduling", "non-preemptive", "gantt chart", "ready queue",
            "waiting state", "zombie process", "orphan process", "multithreading", "cpu burst", "io burst", "turnaround time",
            "waiting time", "response time", "multiprogramming", "cpu scheduler", "long-term scheduler", "short-term scheduler"
        ],
        "memory management": [
            "memory", "paging", "segmentation", "virtual memory", "page replacement", "lru", "fifo", "thrashing",
            "page fault", "page table", "tlb", "translation lookaside buffer", "physical address", "logical address",
            "internal fragmentation", "external fragmentation", "dirty bit", "swapping", "demand paging", "page table entry",
            "page fault rate", "address translation"
        ],
        "deadlocks": [
            "deadlock", "banker's algorithm", "mutual exclusion", "hold and wait", "no preemption", "circular wait",
            "safe state", "resource allocation graph", "deadlock detection", "deadlock recovery", "deadlock prevention",
            "deadlock avoidance", "coffman conditions", "starvation", "resource instances", "banker algorithm"
        ],
        "file systems": [
            "file system", "inode", "directory", "fat", "ntfs", "ext4", "allocation", "contiguous allocation",
            "linked allocation", "indexed allocation", "super block", "file descriptor", "hard link", "symbolic link",
            "mount point", "disk scheduling", "fcfs disk", "sstf", "scan", "c-scan", "look", "c-look", "elevator algorithm"
        ],
        "concurrency": [
            "semaphore", "mutex", "critical section", "race condition", "bounded buffer", "dining philosophers",
            "readers-writers", "sleeping barber", "test-and-set", "compare-and-swap", "spinlocks", "condition variable",
            "monitor", "inter-process communication", "ipc", "message passing", "shared memory", "priority inversion",
            "binary semaphore", "counting semaphore", "producer consumer"
        ]
    },
    "machine learning": {
        "supervised learning": [
            "supervised", "regression", "classification", "svm", "linear regression", "logistic regression", "random forest",
            "decision tree", "k-nearest neighbours", "knn", "k-nn", "nearest neighbor", "naive bayes", "bayes classifier",
            "gradient boosting", "xgboost", "support vector machine", "perceptron", "linear discriminant analysis", "lda",
            "ridge regression", "lasso regression", "ensemble learning", "bagging", "boosting", "decision boundary"
        ],
        "unsupervised learning": [
            "unsupervised", "clustering", "k-means", "pca", "dimensionality reduction", "dbscan", "association",
            "principal component analysis", "hierarchical clustering", "apriori", "anomaly detection", "t-sne",
            "autoencoder", "gaussian mixture model", "gmm", "singular value decomposition", "svd", "unsupervised learning"
        ],
        "neural networks": [
            "neural network", "deep learning", "cnn", "rnn", "activation function", "backpropagation", "gradient descent",
            "epoch", "convolutional neural network", "recurrent neural network", "lstm", "gru", "transformer", "feedforward",
            "weights", "biases", "loss function", "optimizer", "adam", "sgd", "relu", "sigmoid", "softmax", "vision transformer",
            "vit", "perceptron model"
        ],
        "model evaluation": [
            "evaluation", "accuracy", "precision", "recall", "f1-score", "roc", "auc", "cross-validation", "overfitting",
            "underfitting", "bias", "variance", "confusion matrix", "true positive", "false positive", "true negative",
            "false negative", "precision-recall curve", "hyperparameter tuning", "grid search", "random search",
            "model complexity", "model error", "feature engineering", "feature selection", "feature extraction"
        ]
    },
    "artificial intelligence": {
        "search algorithms": [
            "search", "heuristic", "dfs", "bfs", "astar", "a*", "minimax", "alpha-beta pruning", "breadth first search",
            "depth first search", "uninformed search", "informed search", "uniform cost search", "ucs", "greedy best-first",
            "hill climbing", "simulated annealing", "genetic algorithm", "constraint satisfaction problem", "csp",
            "backtracking search", "state space search", "breadth first traversal", "depth first traversal"
        ],
        "knowledge representation": [
            "knowledge representation", "ontology", "semantic web", "frames", "rules", "semantic network",
            "description logic", "rdf", "owl", "schema", "conceptual graph", "conceptual dependency", "assertion",
            "taxonomic hierarchy", "knowledge base", "knowledge graph"
        ],
        "logic and planning": [
            "logic", "propositional logic", "first-order logic", "resolution", "unification", "planning", "fol",
            "sat solver", "predicate calculus", "skolemization", "clause form", "conjunctive normal form", "cnf",
            "strips planning", "pddl", "partial order planning", "hierarchical task network", "logic programming"
        ],
        "expert systems": [
            "expert system", "inference engine", "forward chaining", "backward chaining", "rules-based",
            "rule-based expert system", "mycin", "dendral", "shell", "production rules", "conflict resolution",
            "knowledge base system", "expert systems architecture"
        ]
    },
    "compiler design": {
        "lexical analysis": [
            "lexer", "lexical", "token", "regex", "dfa", "nfa", "lexical analysis", "regular expression",
            "finite automata", "lexical error", "tokenization"
        ],
        "syntax analysis": [
            "parser", "syntax", "cfg", "context-free grammar", "ll parser", "lr parser", "ast", "syntax analysis",
            "abstract syntax tree", "derivation", "ambiguous grammar", "shift-reduce parser", "recursive descent"
        ],
        "semantic analysis": [
            "semantic analysis", "type checking", "symbol table", "attribute grammar", "type coercion",
            "semantic error", "static semantics", "type cast"
        ],
        "code optimization": [
            "optimization", "dead code", "loop unrolling", "common subexpression", "code optimization",
            "constant folding", "strength reduction", "register allocation", "loop optimization"
        ],
        "code generation": [
            "code generation", "compiler code", "intermediate code", "ir", "three-address code", "target code",
            "assembly generation", "intermediate representation", "code generator"
        ]
    },
    "computer graphics": {
        "rendering techniques": [
            "rendering", "ray tracing", "shading", "texture mapping", "rasterization", "illumination model",
            "shadow mapping", "ambient occlusion", "radiosity", "deferred rendering"
        ],
        "geometrical transformations": [
            "transformation", "translation", "rotation", "scaling", "homogeneous coordinates", "shearing",
            "affine transformation", "projection matrix", "view transformation"
        ],
        "shading and texturing": [
            "shading", "phong", "gouraud", "texture", "bump mapping", "specular highlight", "phong shading",
            "gouraud shading", "mipmapping", "procedural texturing"
        ],
        "rasterization": [
            "rasterization", "line drawing", "dda", "bresenham", "polygon filling", " Bresenham line algorithm",
            "scan-line conversion", "z-buffer", "hidden surface removal"
        ]
    },
    "cloud computing": {
        "service models": [
            "iaas", "paas", "saas", "cloud service", "serverless", "infrastructure as a service",
            "platform as a service", "software as a service", "fips", "public cloud", "private cloud"
        ],
        "virtualization and containers": [
            "virtualization", "hypervisor", "vm", "docker", "kubernetes", "container", "virtual machine",
            "containerization", "orchestration", "cgroups", "namespaces"
        ],
        "cloud providers": [
            "aws", "azure", "gcp", "s3", "ec2", "amazon web services", "google cloud platform",
            "cloud storage", "instance type", "cloud deployment"
        ],
        "microservices architecture": [
            "microservices", "api gateway", "service mesh", "load balancer", "microservices architecture",
            "event-driven architecture", "service discovery", "circuit breaker", "monolithic migration"
        ]
    },
    "big data analytics": {
        "distributed storage": [
            "hdfs", "gfs", "cassandra", "hadoop storage", "data lake", "hadoop distributed file system",
            "object storage", "nosql storage", "sharding database"
        ],
        "data processing frameworks": [
            "hadoop", "spark", "mapreduce", "rdd", "hive", "pig", "apache spark", "resilient distributed dataset",
            "yarn", "stream processing", "batch processing"
        ],
        "data warehousing": [
            "data warehouse", "etl", "olap", "star schema", "snowflake schema", "extract transform load",
            "data mart", "dimensional modeling", "online analytical processing"
        ],
        "nosql systems": [
            "nosql", "hbase", "cassandra", "document store", "key-value", "wide-column store", "graph database",
            "document database", "dynamodb"
        ]
    },
    "internet of things": {
        "embedded systems": [
            "embedded", "microcontroller", "arduino", "raspberry pi", "firmware", "embedded systems",
            "real-time system", "system on chip", "soc", "gpio"
        ],
        "protocols and communication": [
            "mqtt", "coap", "zigbee", "bluetooth", "lorawan", "iot protocols", "constrained application protocol",
            "message queuing telemetry transport", "ble", "rfid"
        ],
        "sensors and actuators": [
            "sensor", "actuator", "temperature sensor", "accelerometer", "analog to digital converter",
            "transducer", "digital sensor", "servomotor"
        ],
        "iot architectures": [
            "iot architecture", "edge computing", "fog computing", "smart home", "iot gateway",
            "publish-subscribe", "sensor network"
        ]
    },
    "software engineering": {
        "software development life cycle": [
            "sdlc", "waterfall", "agile", "scrum", "requirements engineering", "software development life cycle",
            "v-model", "spiral model", "xp", "extreme programming", "kanban", "sprint", "backlog", "functional requirements",
            "non-functional requirements", "feasibility study", "software development"
        ],
        "design patterns": [
            "design pattern", "singleton", "factory", "observer", "mvc", "architectural pattern", "model-view-controller",
            "decorator pattern", "strategy pattern", "adapter pattern", "facade pattern", "command pattern", "singleton pattern",
            "factory pattern", "behavioral pattern", "creational pattern", "structural pattern"
        ],
        "testing and qa": [
            "testing", "unit testing", "integration testing", "system testing", "qa", "black-box testing",
            "white-box testing", "regression testing", "acceptance testing", "beta testing", "alpha testing", "test case",
            "test coverage", "code coverage", "mutation testing", "defect density", "software testing", "defect", "bug"
        ],
        "system modeling": [
            "uml", "use case", "class diagram", "sequence diagram", "activity diagram", "unified modeling language",
            "state machine diagram", "component diagram", "deployment diagram", "class representation", "multiplicity",
            "generalization uml", "requirements specification", "srs", "software requirements specification"
        ]
    },
    "computer architecture": {
        "pipelining and hazards": [
            "pipeline", "pipelining", "hazard", "data hazard", "control hazard", "structural hazard", "forwarding",
            "pipeline registers", "stalling", "branch penalty", "instruction pipeline"
        ],
        "parallel architectures": [
            "parallel architecture", "simd", "mimd", "multicore", "smp", "numa", "symmetric multiprocessing",
            "non-uniform memory access", "flynn taxonomy", "vector processor"
        ],
        "memory systems": [
            "memory system", "cache coherence", "snooping", "directory protocol", "mesi", "mesi protocol",
            "write-through", "write-back", "cache miss", "cache hit"
        ],
        "instruction level parallelism": [
            "ilp", "branch prediction", "superscalar", "out-of-order execution", "tomasulo's algorithm",
            "tomasulo algorithm", "instruction level parallelism", "register renaming", "speculative execution"
        ]
    },
    "computer organization": {
        "instruction set architecture": [
            "instruction set", "isa", "op code", "addressing mode", "risc", "cisc", "instruction format",
            "reduced instruction set computer", "complex instruction set computer", "assembly language"
        ],
        "memory hierarchy": [
            "memory hierarchy", "cache", "ram", "rom", "virtual memory", "tlb", "associative", "associative memory",
            "main memory", "secondary storage"
        ],
        "i/o organization": [
            "i/o", "interrupt", "dma", "programmed i/o", "bus arbitration", "direct memory access",
            "interrupt handler", "i/o interface", "polling"
        ],
        "control unit design": [
            "control unit", "hardwired", "microprogrammed", "microinstruction", "hardwired control",
            "microprogrammed control", "control signals", "sequencing"
        ]
    },
    "digital electronics": {
        "boolean algebra": [
            "boolean", "karnaugh map", "k-map", "sop", "pos", "minimization", "boolean algebra",
            "boolean simplification", "sum of products", "product of sums", "consensus theorem"
        ],
        "combinational logic": [
            "combinational", "multiplexer", "mux", "demux", "decoder", "encoder", "adder", "subtractor",
            "combinational circuit", "half adder", "full adder", "ripple carry adder"
        ],
        "sequential logic": [
            "sequential", "flip flop", "sr", "jk", "d-type", "t-type", "latch", "register", "counter",
            "sequential circuit", "excitation table", "state table", "shift register", "synchronous counter"
        ],
        "logic gates": [
            "logic gate", "and gate", "or gate", "not gate", "nand gate", "nor gate", "xor gate",
            "universal gates", "gate propagation delay", "nand realization"
        ]
    },
    "data structures": {
        "linear structures": [
            "array", "linked list", "stack", "queue", "circular queue", "deque", "singly linked list",
            "doubly linked list", "circular linked list", "lifo", "fifo", "push", "pop", "enqueue", "dequeue"
        ],
        "non-linear structures": [
            "tree", "graph", "hash table", "hash map", "non-linear data structure", "graph representation"
        ],
        "trees": [
            "tree", "bst", "binary search tree", "avl tree", "red-black tree", "heap", "trie", "binary tree",
            "b-tree", "b+ tree", "segment tree", "suffix tree", "tree traversal", "inorder", "preorder",
            "postorder", "height-balanced tree", "self-balancing"
        ],
        "graphs": [
            "graph", "adjacency list", "adjacency matrix", "directed graph", "undirected graph", "weighted graph",
            "unweighted graph", "cycle", "dag", "directed acyclic graph", "vertex", "edge", "degree", "path",
            "connectivity", "graph traversal"
        ],
        "hashing": [
            "hashing", "hash function", "collision resolution", "chaining", "open addressing", "linear probing",
            "quadratic probing", "double hashing", "perfect hashing", "load factor", "hash code"
        ]
    },
    "design and analysis of algorithms": {
        "algorithm analysis": [
            "complexity", "time complexity", "space complexity", "big o", "asymptotic", "recurrence relation",
            "asymptotic analysis", "theta notation", "omega notation", "master theorem", "worst-case", "average-case",
            "best-case", "amortized analysis"
        ],
        "sorting and searching": [
            "sorting", "searching", "quicksort", "mergesort", "binary search", "heapsort", "bubble sort",
            "insertion sort", "selection sort", "radix sort", "counting sort", "linear search", "sorting algorithm",
            "comparison-based sorting"
        ],
        "graph algorithms": [
            "dijkstra", "kruskal", "prim", "bfs", "dfs", "bellman-ford", "floyd-warshall", "topological sort",
            "strongly connected components", "minimum spanning tree", "mst", "shortest path algorithm",
            "dijkstra's algorithm", "graph algorithms"
        ],
        "dynamic programming": [
            "dynamic programming", "memoization", "knapsack", "lcs", "floyd", "overlapping subproblems",
            "optimal substructure", "tabular method", "matrix chain multiplication", "longest common subsequence"
        ],
        "greedy algorithms": [
            "greedy", "huffman", "fractional knapsack", "job scheduling", "greedy choice property",
            "huffman coding", "activity selection"
        ]
    },
    "c programming": {
        "pointers and memory": [
            "pointer", "malloc", "free", "calloc", "realloc", "address", "reference", "pointer arithmetic",
            "dereference", "null pointer", "dangling pointer", "memory leak"
        ],
        "data types and structures": [
            "struct", "union", "typedef", "array in c", "string in c", "structure declaration",
            "bit fields", "enum", "type casting"
        ],
        "control flow": [
            "recursion", "loop", "switch case", "if else", "control flow", "break statement",
            "continue statement", "goto"
        ],
        "file i/o": [
            "file", "fopen", "fclose", "fprintf", "fscanf", "fread", "fwrite", "file descriptor in c",
            "fseek", "ftell", "rewind"
        ]
    },
    "python programming": {
        "syntax and structures": [
            "list comprehension", "tuple", "dictionary", "set", "slicing", "python syntax",
            "list comprehensions", "dict comprehension", "membership test"
        ],
        "advanced concepts": [
            "decorator", "generator", "yield", "lambda", "args", "kwargs", "python decorator",
            "context manager", "with statement", "lambda function"
        ],
        "object oriented": [
            "class", "inheritance", "dunder method", "init", "magic method", "polymorphism",
            "encapsulation", "method resolution order", "mro", "super method"
        ]
    },
    "java programming": {
        "object oriented": [
            "class", "object", "inheritance", "polymorphism", "encapsulation", "abstraction", "interface",
            "abstract class", "java oop", "method overriding", "method overloading", "access modifier"
        ],
        "advanced topics": [
            "jvm", "garbage collection", "exception handling", "multithreading in java", "generics",
            "java virtual machine", "classloader", "gc algorithms", "try-catch-finally", "runnable interface"
        ]
    },
    "management information systems": {
        "enterprise systems": [
            "erp", "crm", "scm", "enterprise resource planning", "customer relationship management",
            "supply chain management", "enterprise systems"
        ],
        "decision support systems": [
            "dss", "decision support", "executive support", "expert system in business",
            "decision support system", "group decision support"
        ],
        "it management": [
            "it governance", "cio", "outsourcing", "systems planning", "it service management",
            "cobit", "itil"
        ],
        "business intelligence": [
            "business intelligence", "data mining in business", "analytics", "data warehouse in business",
            "bi tools", "dashboarding"
        ]
    },
    "mobile computing": {
        "mobile development": [
            "android", "ios", "flutter", "react native", "mobile app", "sdk", "mobile development",
            "app lifecycle", "activity lifecycle", "swift", "kotlin"
        ],
        "wireless networks": [
            "wireless", "cellular", "5g", "lte", "gsm", "wifi", "handover", "wireless network",
            "mobile network", "frequency reuse"
        ],
        "location services": [
            "gps", "location-based service", "lbs", "geofencing", "triangulation", "assisted gps",
            "location services"
        ]
    },
    "natural language processing": {
        "text processing": [
            "tokenization", "stemming", "lemmatization", "stop words", "bag of words", "tfidf",
            "text processing", "corpus", "n-grams", "regex tokenization"
        ],
        "information extraction": [
            "ner", "named entity recognition", "pos tagging", "parsing", "part of speech tagging",
            "dependency parsing", "chunking"
        ],
        "language modeling": [
            "language model", "bert", "gpt", "transformer", "word2vec", "embeddings", "word embeddings",
            "attention mechanism", "neural language model"
        ]
    },
    "distributed systems": {
        "consensus protocols": [
            "consensus", "paxos", "raft", "byzantine fault tolerance", "distributed consensus",
            "byzantine agreement", "two-phase commit"
        ],
        "system scalability": [
            "cap theorem", "consistent hashing", "replication", "partitioning", "load balancing",
            "scalability", "horizontal scalability", "eventual consistency", "strong consistency"
        ],
        "rpc and middleware": [
            "rpc", "grpc", "message queue", "kafka", "zookeeper", "middleware", "remote procedure call",
            "distributed locking", "message broker"
        ]
    },
    "cyber security": {
        "cryptography": [
            "cryptography", "encryption", "decryption", "cipher", "aes", "des", "rsa", "sha", "md5",
            "symmetric encryption", "asymmetric encryption", "public key cryptography", "digital signature",
            "key management", "cryptographic key", "pki"
        ],
        "network security": [
            "firewall", "ids", "ips", "vpn", "ssl", "tls", "handshake security", "intrusion detection",
            "network security", "packet inspection", "zero trust", "zero-trust"
        ],
        "application security": [
            "sql injection", "xss", "cross-site scripting", "buffer overflow", "cross-site request forgery",
            "csrf", "sqli", "owasp", "input sanitization", "parameterized query", "session token"
        ],
        "threats and attacks": [
            "malware", "virus", "worm", "phishing", "dos", "ddos", "security implications", "exploit",
            "vulnerability", "attack vector"
        ]
    },
    "web technologies": {
        "frontend development": [
            "html", "css", "javascript", "js", "dom", "react", "angular", "vue", "frontend",
            "browser cookies", "local storage", "web application"
        ],
        "backend development": [
            "node.js", "express", "flask", "django", "server", "rest api", "backend", "web server"
        ],
        "web services": [
            "soap", "rest", "graphql", "json", "xml", "web service", "api endpoint", "http method"
        ],
        "web security": [
            "cookies", "session", "cors", "jwt", "csrf", "web security", "session tokens",
            "cross-origin resource sharing"
        ]
    },
    "data mining": {
        "pattern mining": [
            "association rule", "apriori", "frequent itemset", "fp-growth", "pattern mining",
            "support and confidence", "association rules"
        ],
        "clustering algorithms": [
            "clustering", "k-means", "dbscan", "hierarchical clustering", "cluster analysis",
            "distance metric", "silhouette score"
        ],
        "data preprocessing": [
            "normalization in data mining", "missing value", "noise reduction", "feature selection",
            "data preprocessing", "data cleaning", "imputation"
        ]
    },
    "parallel computing": {
        "programming models": [
            "cuda", "openmp", "mpi", "gpgpu", "threads", "parallel computing", "parallel programming",
            "message passing interface"
        ],
        "synchronization": [
            "race condition", "deadlock", "mutex", "critical section", "barrier", "concurrency synchronization",
            "locks and semaphores"
        ],
        "performance optimization": [
            "speedup", "amdahl's law", "load balance", "cache locality", "parallel speedup",
            "scalability limits"
        ]
    },
    "human computer interaction": {
        "usability evaluation": [
            "usability", "heuristics evaluation", "cognitive walkthrough", "user testing", "usability evaluation",
            "heuristic evaluation", "nielsen heuristics"
        ],
        "user experience design": [
            "ux", "wireframe", "prototype", "interaction design", "persona", "user experience",
            "information architecture"
        ]
    },
    "other computer science": {
        "general": [
            "computer science", "programming", "software", "development", "hardware", "technology",
            "system design", "complexity", "academic", "university", "scientific"
        ]
    }
}
