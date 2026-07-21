import os
import sys
import time

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath("."))

from app import load_models, MEMORY_STORE, process_batch_background, deberta_model, deberta_tokenizer

# Make sure models are loaded
load_models()

sample_questions = [
    "What is the function of a compiler in software engineering?",
    "Explain the difference between TCP and UDP protocols.",
    "Apply the concept of binary search to find an element in an array.",
    "Analyze the time complexity of quicksort in the worst case.",
    "Evaluate the security implications of using cleartext HTTP.",
    "Design a scalable microservices architecture for an e-commerce platform.",
    "Define database normalization and its key normal forms.",
    "Describe how garbage collection works in Java.",
    "Implement a queue using two stacks in Python.",
    "Differentiate between process and thread in operating systems.",
    "What is an OSI model and what are its seven layers?",
    "Explain the concept of virtual memory in modern OS.",
    "Calculate the shortest path using Dijkstra's algorithm.",
    "Analyze the trade-offs of SQL vs NoSQL databases.",
    "Evaluate the effectiveness of convolutional neural networks for image classification.",
    "Create a RESTful API endpoint using Flask and Python.",
    "Identify the primary key in a relational database table.",
    "Summarize the main principles of Agile software development.",
    "Demonstrate how to handle exceptions gracefully in C++.",
    "Contrast symmetric and asymmetric encryption techniques.",
    "Define ACID properties in transaction management.",
    "Explain the purpose of a load balancer in cloud computing.",
    "Apply dynamic programming to solve the 0/1 knapsack problem.",
    "Analyze the cause of deadlocks in multi-threaded programming.",
    "Evaluate the performance of LRU page replacement algorithm.",
    "Design a secure user authentication system using JWT.",
    "Recall the definition of a Big-O notation.",
    "Discuss the role of DNS in web navigation.",
    "Use recursion to traverse a binary search tree.",
    "Compare monolithic and microservices software architectures."
]

session_id = "test-profiling-session-123"
MEMORY_STORE[session_id] = {
    "session_id": session_id,
    "filename": "Test_Profiling_Batch.txt",
    "total_questions": len(sample_questions),
    "questions": sample_questions,
    "results": [],
    "status": "PENDING",
    "stop": False,
    "start_time": None,
    "completed_questions": 0,
}

print(f"Starting background batch profiling run for {len(sample_questions)} questions...")
process_batch_background(session_id)
print("Profiling run complete!")
