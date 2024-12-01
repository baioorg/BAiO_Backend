# BAIO (Bioinformatics AI Operations)

BAIO is a Python package that provides AI-powered tools for bioinformatics operations, including BLAST searches, NCBI E-utilities queries, and ANISEED database interactions.

## Installation

BAIO can be installed as a dependency in your Python project using pip:

```bash
pip install git+https://github.com/yourusername/baio.git
```

Or add to your project's pyproject.toml:

```toml
[tool.poetry.dependencies]
baio = { git = "https://github.com/yourusername/baio.git" }
```

## Backend Integration

BAIO can be integrated into your backend applications in two ways:

### 1. Direct Agent Usage

```python
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from baio.src.agents import baio_agent

# Initialize models
llm = ChatOpenAI(model="gpt-4", temperature=0, api_key="your-openai-key")
embedding = OpenAIEmbeddings(api_key="your-openai-key")

# For tools that require embeddings (BLAST, E-utilities)
result = baio_agent("Which organism does this DNA sequence come from: AGGGGCAGC...", llm, embedding)

# For tools that don't require embeddings (ANISEED)
result = baio_agent("What genes are expressed between stage 1 and 3 in ciona robusta?", llm)
```

### 2. Individual Tool Usage

You can also use specific tools directly:

```python
from baio.src.mytools import blast_tool, eutils_tool
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4", temperature=0)
embedding = OpenAIEmbeddings()

# Using BLAST tool
blast_result = blast_tool("Find this sequence: AGGGGCAGC...", llm, embedding)

# Using E-utilities tool
eutils_result = eutils_tool("Find information about TP53 gene", llm, embedding)
```

## Available Tools

- **BLAST Tool**: DNA/protein sequence searches
- **E-utilities Tool**: NCBI database queries
- **ANISEED Tool**: Gene expression queries
- **BLAT Tool**: Genome alignment queries
- **GO Tool**: Gene ontology queries

## Requirements

- Python 3.10+
- OpenAI API key for LLM and embeddings
- Packages in requirements.txt

## License

MIT License - see LICENSE.txt for details
