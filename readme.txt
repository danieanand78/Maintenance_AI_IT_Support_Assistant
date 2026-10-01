Projet : mAIntenance — AI IT Support Assistant

Overview

**mAIntenance** is an AI-powered IT support assistant designed to automate the analysis and handling of IT support tickets.
The system can understand a user's request, classify the incident, retrieve relevant knowledge, use dedicated tools, and decide whether to **resolve, request more information, or escalate** the ticket.
It also includes security controls and observability to ensure that AI-driven actions remain safe and traceable.


Objectives
* Automatically classify IT support tickets.
* Determine **category, priority and responsible team**.
* Extract relevant information and identify missing details.
* Retrieve reliable troubleshooting procedures using **RAG**.
* Use AI agents and dedicated tools to investigate incidents.
* Provide a structured final decision.
* Escalate sensitive or complex cases to a human technician.
* Monitor and trace the agent's actions.


Architecture

User
  ↓
Frontend
  ↓
Ticket Analysis
  ↓
AI Agent
  ├── Classification & Diagnosis
  ├── RAG / Knowledge Base
  ├── Tools
  └── Security
  ↓
Decision
  ├── Resolve
  ├── Request Information
  └── Escalate
  ↓
Human Validation (if required)


Main Components

	Classification & Diagnosis
Analyzes the ticket to determine its category, priority and responsible team, while extracting relevant information and detecting missing details.

	RAG / Knowledge Base
Retrieves relevant documentation and troubleshooting procedures and provides the sources used by the assistant.

	AI Agent
Orchestrates the different components, selects the appropriate tools and determines the final action.

	Backend & Tools
Provides the API and simulated IT tools for managing tickets, users, equipment and active incidents.

	Security & Observability
Protects the system against prompt injection and unsafe actions, handles human validation, and records logs and traces.

	Frontend & Evaluation
Provides the user interface, test scenarios, evaluation metrics and demonstration dashboard.


Demonstration Scenarios

	The system is designed to handle four main scenarios:
1. **Common incident** → analyze and propose a resolution.
2. **Urgent incident** → identify priority and escalate.
3. **Incomplete ticket** → ask for missing information.
4. **Sensitive/malicious request** → block unsafe actions and require human validation.

	Team
| Member | Responsibility             |
| ------ | -------------------------- |
| **1**  | Classification & Diagnosis |
| **2**  | RAG / Knowledge Base       |
| **3**  | AI Agent                   |
| **4**  | Backend & Tools            |
| **5**  | Security & Observability   |
| **6**  | Frontend & Evaluation      |


Project Status
Developed as part of the **mAIntenance & Assistance** hackathon challenge.
