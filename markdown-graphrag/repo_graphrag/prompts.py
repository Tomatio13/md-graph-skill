# ========================================
# Prompt for plan creation
# ========================================

PLAN_PROMPT_TEMPLATE = """
# Role
You are an excellent manager who creates an implementation plan from a modification request.
Create an accurate and error-free plan assuming that other LLMs/agents will execute the plan.

# Task
Rewrite the modification request into an "implementation plan" to be handed off to other LLMs/agents.
Include the following steps in the plan:
- Preparation
    1. Identify file paths of documents to be newly created or modified
    2. Investigate dependencies and impact range
- Design
- Implementation
    1. Create/modify documents

# Rules
Always include the following:
- Always include the paths of target documents to be modified.
- Perform the minimum changes necessary to fulfill the requested requirements.

# Modification Request:
{user_request}
"""

# ========================================
# Response message templates
# ========================================

PLAN_RESPONSE_TEMPLATE = """
# Task
An implementation plan has been created by referencing the storage based on the modification request.
Present the plan content to the user in an easy-to-understand manner, and ask for their decision on whether to autonomously execute documentation updates based on this plan.
If there are ambiguous or unclear parts in the plan, refer to the sample follow-up questions and continue the repository analysis flow.

Modification Request:
{user_request}

Implementation Plan:
{plan}

# Sample Follow-up Questions
- Summarize the main documented sections using storage `{storage_name}`
- Explain what this section says using storage `{storage_name}`
- Find the documentation that mentions the following topic using storage `{storage_name}`
    
# Note
In the following cases, the storage referenced for planning may not include the current implementation and may be outdated.
Only if applicable, inform the user that the storage may be outdated and recommend updating the storage.
- If the plan mentions that the storage differs from the state the user expects as current.
"""

QUERY_RESPONSE_TEMPLATE = """
# Task
An answer has been created by referencing the storage for the user's question.
If there are ambiguous or unclear parts in the answer, refer to the sample follow-up questions and continue the repository analysis flow.
If the answer states that it cannot respond precisely to the question, do not ask follow-up questions.

Question:
{user_query}

Answer:
{response}

# Sample Follow-up Questions
- Summarize the main documented sections using storage `{storage_name}`
- Explain what this section says using storage `{storage_name}`
- Find the documentation that mentions the following topic using storage `{storage_name}`

# Note
In the following cases, the storage referenced for the answer may not include the current implementation and may be outdated.
Only if applicable, inform the user that the storage may be outdated and recommend updating the storage.
- If the answer mentions that the storage differs from the state the user expects as current.
"""

GRAPH_STORAGE_RESULT_TEMPLATE = """
GraphRAG storage {action} completed.

Result:
- Read directory: {read_dir_path}
- {action} storage: {storage_dir_path}
"""

# ========================================
# Error message templates
# ========================================

STORAGE_NOT_FOUND_ERROR_TEMPLATE = "Error: GraphRAG storage not found.\nStorage name: {storage_name}"

GENERAL_ERROR_TEMPLATE = "An error occurred: {error}"
