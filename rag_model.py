from langchain.prompts import ChatPromptTemplate
#from langchain.chat_models import ollama
#from langchain_ollama import ChatOllama
from langchain_ollama import ChatOllama
from typing import List
from src.chromadb import get_chroma_db
from dataclasses import dataclass

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

@dataclass
class QueryResponse:
    query_text : str
    response_text : str
    sources : List[str]

def query_rag(query_text : str) -> QueryResponse:
    db = get_chroma_db()

    #Database search
    results= db.similarity_search_with_score(query_text,k=3)
    context="\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template= ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context,question=query_text)

    model= ChatOllama(model="qwen2.5:0.5b")
    response=model.invoke(prompt)
    response_text = response.content
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    print(f"Response: {response_text}\nSources: {sources}")
    return QueryResponse(
        query_text=query_text, response_text=response_text, sources=sources
    )



if __name__ == "__main__":
    query_rag("How can I contact support?")
