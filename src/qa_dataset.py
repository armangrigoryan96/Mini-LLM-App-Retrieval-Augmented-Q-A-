"""
QA Evaluation Dataset

Hand-crafted questions and reference answers for evaluating
the RAG system performance.
"""

qa_dataset = [
    {
        "id": 1,
        "question": "How do I create a simple index on a single column in PostgreSQL?",
        "reference_answer": "Use the CREATE INDEX command with the syntax: CREATE INDEX index_name ON table_name (column_name);",
        "category": "DDL",
        "relevant_docs": ["sql-create-index"]
    },
    {
        "id": 2,
        "question": "What is the difference between TRUNCATE and DELETE in PostgreSQL?",
        "reference_answer": "TRUNCATE removes all rows from a table quickly without scanning the table, cannot be rolled back in some cases, and resets sequences. DELETE scans and removes rows one by one, can have a WHERE clause, can be rolled back, and doesn't reset sequences.",
        "category": "DML",
        "relevant_docs": ["sql-truncate", "sql-delete"]
    },
    {
        "id": 3,
        "question": "How do I grant SELECT privileges on a table to a user?",
        "reference_answer": "Use the GRANT command: GRANT SELECT ON table_name TO user_name;",
        "category": "Security",
        "relevant_docs": ["sql-grant"]
    },
    {
        "id": 4,
        "question": "What is MVCC in PostgreSQL?",
        "reference_answer": "MVCC (Multi-Version Concurrency Control) is PostgreSQL's method of handling concurrent transactions. It allows multiple transactions to access the same data simultaneously without blocking by maintaining multiple versions of rows.",
        "category": "Concepts",
        "relevant_docs": ["mvcc"]
    },
    {
        "id": 5,
        "question": "How do I start a transaction in PostgreSQL?",
        "reference_answer": "Use the BEGIN command to start a transaction block. You can also use START TRANSACTION.",
        "category": "Transactions",
        "relevant_docs": ["sql-begin"]
    },
    {
        "id": 6,
        "question": "What is the purpose of the EXPLAIN command?",
        "reference_answer": "EXPLAIN shows the execution plan for a SQL statement, displaying how tables will be scanned, which indexes will be used, and estimated costs. It helps analyze and optimize query performance.",
        "category": "Performance",
        "relevant_docs": ["sql-explain"]
    },
    {
        "id": 7,
        "question": "How do I add a new column to an existing table?",
        "reference_answer": "Use ALTER TABLE with ADD COLUMN: ALTER TABLE table_name ADD COLUMN column_name data_type;",
        "category": "DDL",
        "relevant_docs": ["sql-alter-table"]
    },
    {
        "id": 8,
        "question": "What is the difference between a view and a materialized view?",
        "reference_answer": "A regular view is a virtual table that executes its query each time it's accessed. A materialized view stores the query results physically and must be refreshed to update the data, but provides faster access for complex queries.",
        "category": "Views",
        "relevant_docs": ["sql-create-view", "sql-refresh-materialized-view"]
    },
    {
        "id": 9,
        "question": "How do I roll back a transaction in PostgreSQL?",
        "reference_answer": "Use the ROLLBACK command to abort the current transaction and discard all changes made within it.",
        "category": "Transactions",
        "relevant_docs": ["sql-rollback"]
    },
    {
        "id": 10,
        "question": "What is a partial index in PostgreSQL?",
        "reference_answer": "A partial index is an index built over a subset of a table, defined by a conditional expression in the WHERE clause. It's useful for indexing only the rows that are frequently queried, saving space and improving performance.",
        "category": "Indexes",
        "relevant_docs": ["indexes-partial"]
    },
    {
        "id": 11,
        "question": "How do I update multiple columns in a single UPDATE statement?",
        "reference_answer": "Use the UPDATE command with comma-separated column assignments: UPDATE table_name SET column1 = value1, column2 = value2 WHERE condition;",
        "category": "DML",
        "relevant_docs": ["sql-update"]
    },
    {
        "id": 12,
        "question": "What is the purpose of VACUUM in PostgreSQL?",
        "reference_answer": "VACUUM reclaims storage occupied by dead tuples (deleted or obsoleted rows), preventing table bloat and maintaining database performance. It's essential for proper database maintenance in PostgreSQL.",
        "category": "Maintenance",
        "relevant_docs": ["sql-vacuum"]
    },
    {
        "id": 13,
        "question": "How do I create a database in PostgreSQL?",
        "reference_answer": "Use the CREATE DATABASE command: CREATE DATABASE database_name;",
        "category": "DDL",
        "relevant_docs": ["sql-create-database"]
    },
    {
        "id": 14,
        "question": "What are constraints in PostgreSQL tables?",
        "reference_answer": "Constraints are rules enforced on table columns to maintain data integrity. Common constraints include PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, and CHECK constraints.",
        "category": "DDL",
        "relevant_docs": ["ddl-constraints"]
    },
    {
        "id": 15,
        "question": "How do I insert multiple rows in a single INSERT statement?",
        "reference_answer": "Use INSERT with multiple value sets: INSERT INTO table_name (col1, col2) VALUES (val1, val2), (val3, val4), (val5, val6);",
        "category": "DML",
        "relevant_docs": ["sql-insert"]
    },
    {
        "id": 16,
        "question": "What is a savepoint in PostgreSQL transactions?",
        "reference_answer": "A savepoint is a special mark within a transaction that allows you to roll back to that point without aborting the entire transaction. It's useful for implementing complex transaction logic with partial rollbacks.",
        "category": "Transactions",
        "relevant_docs": ["sql-savepoint"]
    },
    {
        "id": 17,
        "question": "How do I drop an index in PostgreSQL?",
        "reference_answer": "Use the DROP INDEX command: DROP INDEX index_name;",
        "category": "DDL",
        "relevant_docs": ["sql-drop-index"]
    },
    {
        "id": 18,
        "question": "What does the ANALYZE command do?",
        "reference_answer": "ANALYZE collects statistics about the contents of tables in the database. These statistics are used by the query planner to determine the most efficient execution plans for queries.",
        "category": "Maintenance",
        "relevant_docs": ["sql-analyze"]
    },
    {
        "id": 19,
        "question": "How do I revoke privileges from a user in PostgreSQL?",
        "reference_answer": "Use the REVOKE command: REVOKE privilege_type ON object_name FROM user_name;",
        "category": "Security",
        "relevant_docs": ["sql-revoke"]
    },
    {
        "id": 20,
        "question": "What is the MERGE command used for?",
        "reference_answer": "MERGE (also known as UPSERT) conditionally inserts, updates, or deletes rows based on whether a match is found. It's useful for synchronizing tables or implementing 'insert or update' logic in a single statement.",
        "category": "DML",
        "relevant_docs": ["sql-merge"]
    }
]
