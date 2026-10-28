# AI Agent — RAG-Powered Company Assistant

An AI agent built with Python that combines **LLM-based planning, tool calling, Retrieval-Augmented Generation (RAG), and human-in-the-loop email approval** to assist with internal company tasks.

The agent can answer questions about company policies using a vector database, decide when tools are needed, and send emails through Gmail after receiving explicit human approval.

## ✨ Features

- **LLM-Based Planning:** Generates a high-level execution plan before processing a user request.
- **Tool Calling:** Selects and executes tools based on the user's intent.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant company policy documents to ground answers in internal knowledge.
- **Embedding Generation:** Uses an OpenAI-compatible API to generate document and query embeddings.
- **Vector Search:** Stores and retrieves document embeddings using ChromaDB with cosine similarity.
- **Human-in-the-Loop:** Requires explicit user approval before sending an email.
- **Gmail Integration:** Sends emails through Gmail using Python's SMTP and SSL support.
- **Conversation Context:** Maintains a bounded conversation history during the running session.
- **Modular Architecture:** Separates agent orchestration, RAG processing, configuration, tools, and email delivery.

## 🏗️ Architecture

The project separates agent execution from document retrieval and external actions.

```text
AI-Agent/
├── data/
│   └── rules.txt
├── rag_steps/
│   ├── document.py
│   └── retrieval.py
├── agent.py
├── config.py
├── email_service.py
├── logger.py
├── main.py
├── rag.py
├── tools.py
├── .gitignore
└── README.md
```

### Core Components

| File | Responsibility |
|---|---|
| `main.py` | Application entry point and interactive CLI |
| `agent.py` | Agent planning, LLM interaction, tool execution, and conversation history |
| `config.py` | Environment variables and runtime configuration |
| `rag.py` | RAG initialization and company-policy retrieval |
| `rag_steps/document.py` | Document loading, cleaning, chunking, metadata attachment, and indexing |
| `rag_steps/retrieval.py` | ChromaDB integration, embedding generation, and vector retrieval |
| `tools.py` | Tool definitions and human email-approval workflow |
| `email_service.py` | Gmail delivery through SMTP over SSL |
| `data/rules.txt` | Sample internal company policies |

## 🔄 How It Works

1. **Initialization:** The application initializes the ChromaDB vector store and indexes company policy documents when the collection is empty.
2. **Planning:** The LLM generates a short execution plan based on the user's request and available conversation context.
3. **Reasoning and Tool Selection:** The agent receives the request and plan, then decides whether a tool is required.
4. **Knowledge Retrieval:** When company policies are relevant, the agent invokes `search_company_rules` to retrieve relevant document chunks.
5. **Human Approval:** When an email needs to be sent, the agent invokes `send_email` and asks the user for approval before performing the external action.
6. **Execution and Response:** Tool results are returned to the LLM, which can continue processing or produce a final answer.
7. **Conversation Update:** Completed exchanges are added to the in-memory conversation history, subject to the configured history limit.

## 🛠️ Tech Stack

- **Language:** Python
- **LLM Integration:** OpenAI Python SDK with an OpenAI-compatible API endpoint
- **Agent Orchestration:** Custom planning and tool-calling loop
- **RAG:** LangChain document abstractions and text splitters
- **Embeddings:** Custom embedding adapter using the OpenAI-compatible Embeddings API
- **Vector Database:** ChromaDB
- **Email Integration:** `smtplib`, `ssl`, and `email.message`
- **Configuration:** `python-dotenv`

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/behrouzyou/AI-Agent.git
cd AI-Agent
```

### 2. Create a Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the packages used by the current implementation:

```bash
pip install openai python-dotenv langchain-core langchain-text-splitters langchain-chroma chromadb
```

For reproducible installations, pin and maintain the tested dependency versions in a `requirements.txt` file.

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPEN_API_KEY=your_api_key
OPENAI_CHAT_MODEL=your_chat_model
OPENAI_EMBEDDING_MODEL=your_embedding_model

GMAIL_ADDRESS=your_gmail_address
GMAIL_PASSWORD=your_gmail_app_password
```

**Configuration notes:**

- `OPEN_API_KEY`: API key for the configured OpenAI-compatible provider.
- `OPENAI_CHAT_MODEL`: Chat model identifier.
- `OPENAI_EMBEDDING_MODEL`: Embedding model identifier.
- `GMAIL_ADDRESS`: Gmail account used to send emails.
- `GMAIL_PASSWORD`: Gmail App Password, where supported, rather than your regular account password.

The current API endpoint is configured in the source code as:

```python
https://api.gapgpt.app/v1
```

Ensure that your selected chat and embedding models are available through the configured provider.

**Security:** Never commit your `.env` file or expose API keys and email credentials in source control.

## ▶️ Usage

Run the application from the project root:

```bash
python main.py
```

The application prepares the RAG vector store and starts an interactive command-line session.

Example interaction:

```text
شما: قوانین دورکاری شرکت چیست؟

پاسخ:
[Answer grounded in the retrieved company policies]
```

To exit the application:

```text
شما: exit
```

### Available Tools

| Tool | Description |
|---|---|
| `search_company_rules` | Retrieves relevant internal company policies using RAG |
| `send_email` | Sends an email after explicit human approval |

The agent is instructed to answer in Persian and avoid inventing company policies.

## 🧠 RAG Pipeline

The retrieval pipeline consists of the following stages:

1. Load the policy document from `data/rules.txt`.
2. Normalize whitespace and clean the document text.
3. Split the document into smaller chunks using `RecursiveCharacterTextSplitter`.
4. Attach source metadata and chunk identifiers.
5. Generate embeddings through the configured API.
6. Store document vectors in ChromaDB.
7. Retrieve the most relevant chunks for a query using cosine similarity.

### Current RAG Configuration

| Parameter | Default |
|---|---:|
| Chunk size | 250 characters |
| Chunk overlap | 20 characters |
| Retrieval top-k | 2 |
| Vector collection | `rules` |
| Vector database directory | `db/vectors.db` |

These values are configurable in `config.py`.

## 📧 Human-in-the-Loop Email Workflow

Email sending is treated as an external action requiring explicit approval.

Before an email is sent, the application displays the recipient, subject, and body and requests confirmation in the terminal.

```text
آیا این ایمیل ارسال شود؟ (yes/no)
```

- `yes`: Proceeds with email delivery.
- Any other response: Cancels the send operation.

Email delivery uses Gmail's SMTP server over SSL on port `465`.

## 🔧 Configuration and Limitations

The following are important characteristics of the current implementation:

- Conversation history is maintained in memory and is not persisted across application restarts.
- `MAX_MEMORY_SIZE` controls the retained history size; the current configuration should be adjusted if multiple complete conversation turns are required.
- `MAX_ITERATION` limits the number of agent iterations.
- The initial indexing logic checks whether the vector collection is empty. Changes to an already indexed document are not automatically synchronized with the existing collection.
- The application currently exposes company-policy retrieval and email sending, rather than a general-purpose collection of external integrations.
- The current interface is a command-line application.

## 🔮 Potential Improvements

- Add persistent conversation memory.
- Implement document update detection and incremental re-indexing.
- Add automated tests for agent execution, retrieval, and email approval.
- Improve error handling and retry policies.
- Add structured logging and execution tracing.
- Introduce configurable model providers and API endpoints.
- Add a web interface or API layer.
- Improve email delivery reliability and validation.
- Add observability for tool calls, retrieval quality, latency, and token usage.

## 🔐 Security

- Keep secrets in environment variables.
- Require explicit approval for external side effects.
- Avoid logging sensitive credentials or confidential document contents.
- Validate tool arguments and handle provider errors safely.
- Use least-privilege credentials for external services.

## 👨‍💻 Author

**Behrouz**

GitHub: [@behrouzyou](https://github.com/behrouzyou)

---

*This project is an educational implementation of an LLM-powered agent using custom orchestration, tool calling, and Retrieval-Augmented Generation.*