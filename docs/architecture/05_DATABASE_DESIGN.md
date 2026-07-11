---
title: Database Design
version: 1.0.0
status: Approved
owner: Sujoy Ghosh
authors:
  - Sujoy Ghosh
  - ChatGPT (Technical Design Partner)
created: 2026-07-11
last_updated: 2026-07-11
---

# Database Design

## 1. Purpose

This document defines the logical database design for Suvyon Version 1.0.

The database is responsible for securely storing user information, workspaces, conversations, uploaded files, AI interactions, and application metadata while ensuring data integrity, scalability, and workspace isolation.

---

# 2. Database Objectives

The database must provide:

- Data consistency
- High reliability
- Secure storage
- Workspace isolation
- Fast retrieval
- Scalability
- Extensibility
- Auditability

---

# 3. Database Technology

| Component | Technology |
|-----------|------------|
| Database Engine | PostgreSQL |
| Managed Platform | Supabase |
| ORM | SQLAlchemy |
| Migration Tool | Alembic |

PostgreSQL serves as the single source of truth for all persistent application data.

---

# 4. Design Principles

The database design follows these principles:

- Normalize business data.
- Minimize redundancy.
- Maintain referential integrity.
- Separate user data.
- Avoid vendor lock-in.
- Design for future scalability.
- Keep AI providers independent of stored data.

---

# 5. Core Entities

Version 1.0 includes the following primary entities:

- Users
- User Profiles
- Workspaces
- Conversations
- Messages
- Uploaded Files
- Document Chunks
- Embeddings Metadata
- AI Providers
- Tool Executions
- Email History
- User Settings

---

# 6. Entity Relationship Overview

```text
User
 │
 ├────────── User Profile
 │
 ├────────── Workspace
 │               │
 │               ├──────── Conversations
 │               │              │
 │               │              └──────── Messages
 │               │
 │               ├──────── Uploaded Files
 │               │              │
 │               │              └──────── Document Chunks
 │               │
 │               ├──────── Tool Executions
 │               │
 │               └──────── Email History
 │
 └────────── User Settings
```

---

# 7. Users

Stores authentication-related information.

Example attributes:

- User ID
- Email
- Password Hash
- Authentication Provider
- Account Status
- Created Timestamp
- Updated Timestamp

Each user has exactly one profile and one workspace.

---

# 8. User Profile

Stores non-authentication information.

Example attributes:

- Display Name
- Avatar
- Time Zone
- Preferred Language
- Theme Preference

Profile data remains independent from authentication data.

---

# 9. Workspace

Represents the private environment for each authenticated user.

Responsibilities include:

- Conversation ownership
- File ownership
- Knowledge ownership
- User preferences
- AI history

Every workspace belongs to exactly one user.

---

# 10. Conversations

Stores chat sessions.

Example attributes:

- Conversation ID
- Workspace ID
- Title
- Created Timestamp
- Updated Timestamp
- Archived Status

A conversation contains multiple messages.

---

# 11. Messages

Stores individual conversation messages.

Each message records:

- Sender
- Content
- Timestamp
- Message Type
- Model Used
- Response Metadata

Messages remain immutable after creation.

---

# 12. Uploaded Files

Stores metadata for user-uploaded files.

Example attributes:

- File ID
- Workspace ID
- File Name
- MIME Type
- Storage Path
- File Size
- Upload Timestamp
- Processing Status

Actual file contents are stored in object storage.

---

# 13. Document Chunks

Large documents are divided into searchable chunks.

Each chunk stores:

- Parent File
- Chunk Index
- Extracted Text
- Character Count
- Processing Metadata

Chunking improves Retrieval-Augmented Generation performance.

---

# 14. Embeddings Metadata

Stores metadata related to vector embeddings.

Example attributes:

- Chunk ID
- Embedding Provider
- Embedding Model
- Vector Identifier
- Creation Timestamp

Embedding vectors remain abstracted from business logic.

---

# 15. Tool Executions

Stores AI tool activity.

Example records include:

- Web Search
- Document Search
- Email Generation
- OCR
- Future Tool Integrations

Tool history improves debugging and observability.

---

# 16. Email History

Stores metadata for AI-assisted email operations.

Example attributes:

- Recipient
- Subject
- Status
- Sent Timestamp
- Related Conversation

Email bodies should not be permanently stored unless explicitly required.

---

# 17. User Settings

Stores user preferences.

Examples:

- Preferred AI Provider
- Preferred Theme
- Notification Settings
- Language
- Workspace Preferences

Settings are isolated per user.

---

# 18. Relationships

The database enforces:

- One User → One Workspace
- One Workspace → Many Conversations
- One Conversation → Many Messages
- One Workspace → Many Uploaded Files
- One Uploaded File → Many Document Chunks
- One Workspace → Many Tool Executions
- One Workspace → Many Emails

Referential integrity must be maintained using foreign keys.

---

# 19. Workspace Isolation

Every query executed by the application must be scoped to the authenticated user's workspace.

The system must never expose resources belonging to another workspace.

Workspace isolation is a mandatory security requirement.

---

# 20. Indexing Strategy

Indexes should be created for:

- User Email
- Workspace ID
- Conversation ID
- File ID
- Created Timestamp
- Updated Timestamp

Additional indexes may be introduced based on production usage patterns.

---

# 21. Soft Delete Policy

Business records should support soft deletion where appropriate.

Soft-deleted records:

- Remain recoverable
- Are excluded from normal queries
- Preserve historical integrity

Permanent deletion should occur only when explicitly requested or required.

---

# 22. Audit Fields

Every primary entity should include:

- Created At
- Updated At
- Created By (when applicable)
- Updated By (when applicable)

Audit fields improve traceability and debugging.

---

# 23. Security Considerations

The database must enforce:

- Strong authentication
- Authorization
- Workspace isolation
- Encrypted connections
- Parameterized queries
- Protection against SQL injection

Sensitive information must never be stored in plain text.

---

# 24. Future Expansion

The database is designed to support future features including:

- Team Workspaces
- Shared Knowledge Bases
- AI Memory
- Plugin Data
- Workflow Automation
- Agent Collaboration
- Enterprise Administration

These capabilities should be added without requiring significant redesign.

---

# 25. Database Goals

The database design aims to achieve:

- Reliability
- Performance
- Scalability
- Security
- Maintainability
- Extensibility
- Data Integrity

---

# 26. Conclusion

The Suvyon database design establishes a secure, normalized, and scalable foundation for Version 1.0.

By separating authentication, workspaces, conversations, knowledge, and AI-related data into well-defined entities, the platform ensures long-term maintainability, provider independence, and secure multi-user operation.