from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.tools.query_engine import QueryEngineTool

from supabase_vectore_store import vector_store

# Supabase vector store as retriever

index = VectorStoreIndex.from_vector_store(vector_store)
retriever = index.as_retriever(similarity_top_k=5)

supabase_query_engine = RetrieverQueryEngine(retriever=retriever)

WorkflowRetriever = QueryEngineTool.from_defaults(
    query_engine=supabase_query_engine,
    name="WorkflowRetriever",
    description="Fetches workflow steps and explanations"
)