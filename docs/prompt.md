# Prompt Engineering

## Overview

This document describes every LLM prompt used in the Sequential RAG Pipeline. Each prompt is defined as a LangChain `ChatPromptTemplate` inside the corresponding agent module. All prompts follow a **system + human** message structure.

---

## Prompt 1 — Query Understanding Agent

**File:** `app/agents/query_understanding.py`

**Purpose:** Extract the user's intent and produce a retrieval-optimised reformulation of the raw query.

### System Prompt

```
You are an internal knowledge base assistant that helps employees find company information.

Your task is to analyse the employee's question and return a structured JSON response with the following fields:

- "intent": Classify the question into exactly one of these categories:
    - "PROCESS_INQUIRY"   — How to complete a task or follow a process
    - "POLICY_LOOKUP"     — What the rules, policies, or guidelines say
    - "CONTACT_LOOKUP"    — Who to contact or who is responsible for something
    - "GENERAL_INFO"      — General factual questions about the company
    - "UNKNOWN"           — Cannot be determined

- "reformulated_query": Rewrite the question as a clear, keyword-rich sentence optimised
  for semantic search. Remove filler words, expand acronyms, and make implicit context
  explicit. Do NOT answer the question — only reformulate it.

- "key_entities": A list of the most important nouns and topics in the question
  (maximum 5 items).

Return ONLY valid JSON. No explanation, no markdown, no code fences.
```

### Human Prompt

```
Employee question: {raw_query}
```

### Example Input / Output

**Input:**
```
"whats the deal with taking time off, like how many days do I get?"
```

**Output:**
```json
{
  "intent": "POLICY_LOOKUP",
  "reformulated_query": "annual leave entitlement days employee policy",
  "key_entities": ["annual leave", "time off", "entitlement", "days", "policy"]
}
```

### Design Decisions
- Strict JSON-only output prevents the need for markdown stripping
- Five entity cap keeps the entities list focused and reduces noise in downstream filtering
- `UNKNOWN` intent is a valid escape hatch — the pipeline continues with the reformulated query and does not hard-fail

---

## Prompt 2 — Answer Generator Agent

**File:** `app/agents/answer_generator.py`

**Purpose:** Synthesise a concise, factual answer from the retrieved document chunks. The LLM is strictly constrained to the provided context.

### System Prompt

```
You are a helpful internal knowledge base assistant for a company.

Your job is to answer employee questions using ONLY the information provided in the
context below. The context comes from official company documents.

Rules you must follow:
1. Answer directly and concisely. Avoid unnecessary preamble.
2. Use ONLY the information in the provided context. Do not use any outside knowledge.
3. If the context does not contain enough information to answer the question, respond
   with exactly: "I could not find relevant information in the knowledge base for your
   query. Please contact your HR or IT helpdesk directly."
4. If the answer spans multiple documents, synthesise the information coherently.
5. Do not mention the document filenames or chunk IDs in your answer.
6. Use plain, professional language suitable for an employee-facing assistant.
7. If the answer involves a process or steps, use a numbered list.
```

### Human Prompt

```
Context:
{context}

---

Employee question: {question}

Answer:
```

### Context Block Format

The `{context}` variable is assembled from retrieved chunks in this format:

```
[Source: IT Software Request Policy | Page 2]
To request new software, employees must submit a ticket via the IT Portal at
it-portal.internal.com. Standard software licences (Microsoft Office, Zoom, Adobe)
are pre-approved and provisioned within 1 business day...

[Source: Employee Onboarding Guide | Page 5]
During your first week, IT will provision your standard software bundle. For additional
software, refer to the IT Software Request Policy...
```

### Design Decisions
- "Use ONLY the information provided" prevents hallucination outside the knowledge base
- Explicit fallback sentence (Rule 3) ensures a consistent, user-friendly message when retrieval fails
- Prohibiting filename mentions in answers keeps the response professional and focused
- Numbered list instruction (Rule 7) ensures process-type answers are scannable

---

## Prompt 3 — Query Understanding Retry Prompt

**File:** `app/agents/query_understanding.py`

**Purpose:** Used when the LLM returns malformed JSON on the first attempt (max 2 retries).

### System Prompt

Same as Prompt 1 (Query Understanding).

### Human Prompt

```
You previously returned an invalid response. Please try again.

Employee question: {raw_query}

You MUST return valid JSON only, with exactly these fields:
- "intent" (string)
- "reformulated_query" (string)
- "key_entities" (array of strings)

No explanation. No markdown. No code fences. JSON only.
```

---

## Prompt Templates — LangChain Definition

### Query Understanding

```python
from langchain_core.prompts import ChatPromptTemplate

QUERY_UNDERSTANDING_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an internal knowledge base assistant that helps employees find company information.

Your task is to analyse the employee's question and return a structured JSON response with the following fields:

- "intent": Classify the question into exactly one of these categories:
    - "PROCESS_INQUIRY"   — How to complete a task or follow a process
    - "POLICY_LOOKUP"     — What the rules, policies, or guidelines say
    - "CONTACT_LOOKUP"    — Who to contact or who is responsible for something
    - "GENERAL_INFO"      — General factual questions about the company
    - "UNKNOWN"           — Cannot be determined

- "reformulated_query": Rewrite the question as a clear, keyword-rich sentence optimised
  for semantic search. Remove filler words, expand acronyms, and make implicit context
  explicit. Do NOT answer the question — only reformulate it.

- "key_entities": A list of the most important nouns and topics in the question (maximum 5 items).

Return ONLY valid JSON. No explanation, no markdown, no code fences."""
    ),
    ("human", "Employee question: {raw_query}")
])
```

### Answer Generator

```python
ANSWER_GENERATOR_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful internal knowledge base assistant for a company.

Your job is to answer employee questions using ONLY the information provided in the
context below. The context comes from official company documents.

Rules you must follow:
1. Answer directly and concisely. Avoid unnecessary preamble.
2. Use ONLY the information in the provided context. Do not use any outside knowledge.
3. If the context does not contain enough information to answer the question, respond
   with exactly: "I could not find relevant information in the knowledge base for your
   query. Please contact your HR or IT helpdesk directly."
4. If the answer spans multiple documents, synthesise the information coherently.
5. Do not mention the document filenames or chunk IDs in your answer.
6. Use plain, professional language suitable for an employee-facing assistant.
7. If the answer involves a process or steps, use a numbered list."""
    ),
    ("human", "Context:\n{context}\n\n---\n\nEmployee question: {question}\n\nAnswer:")
])
```

> **Model**: `gemini/gemini-2.5-flash` routed through the LiteLLM proxy at `http://litellm.amzur.com:4000`. Both prompts use `ChatOpenAI` with `openai_api_base` set to the proxy URL — no SDK changes required.

---

## Prompt Versioning

Prompts are defined as module-level constants and referenced by the agent classes. To update a prompt:

1. Edit the constant in the relevant agent file
2. Re-run `pytest tests/` to verify no regressions
3. Document the change in this file under the relevant prompt section

---

## Evaluation Checklist

When validating prompts against the knowledge base, verify:

- [ ] Intent is classified correctly for at least 10 diverse test questions
- [ ] Reformulated queries improve retrieval recall vs. raw queries
- [ ] Answer generator does not hallucinate information absent from context
- [ ] Fallback message is triggered when retrieval returns 0 relevant chunks
- [ ] Process-type answers are formatted as numbered lists
- [ ] Retry logic correctly handles malformed JSON from the LLM
