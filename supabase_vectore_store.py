from abc import abstractmethod
from typing import Any, List, Sequence
from llama_index.core.vector_stores.types import VectorStore, BasePydanticVectorStore
from llama_index.core.schema import NodeWithScore
from openai import BaseModel
from supabase import Client

from env import TABLE_NAME
from supabase_client import supabase_client  # or use `postgrest` directly

class SupabaseVectorStore(BasePydanticVectorStore):
    client: Client = supabase_client
    table_name: str = TABLE_NAME
    
    @property
    def client(self) -> Client:
        return supabase_client
    
    def add(
        self,
        nodes: Sequence[BaseModel],
        **kwargs: Any,
    ) -> List[str]:
        """Add nodes to vector store."""
        ...
        
    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id."""
        ...
    
    

    def query(self, query_embedding, top_k=5):
        # Call Supabase RPC or SQL for vector similarity search
        response = self.client.rpc("match_document", {
            "query_embedding": query_embedding,
            "match_count": top_k
        }).execute()

        # Convert to NodeWithScore
        return [
            NodeWithScore(
                node_id=row["id"],
                node_content=row["content"],
                score=row["similarity"]
            )
            for row in response.data
        ]
        
vector_store = SupabaseVectorStore()
