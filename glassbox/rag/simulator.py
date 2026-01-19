"""
Barista RAG Simulator - Simulates Boeing's internal RAG tool.

Implements the simulation environment per Living Specs Section 3:
- ChromaDB vector store integration (read-only)
- Noise injection for robustness testing
- Context assembly in standard RAG pattern
"""

import logging
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

# ChromaDB import with fallback
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not installed. Using mock implementation.")


@dataclass
class RetrievedChunk:
    """A single chunk retrieved from the vector store."""
    id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_noise: bool = False  # True if injected as distractor


@dataclass
class RAGContext:
    """Assembled context for RAG query."""
    chunks: List[RetrievedChunk]
    query: str
    system_prompt: str
    formatted_prompt: str
    noise_level: float
    
    @property
    def legitimate_chunks(self) -> List[RetrievedChunk]:
        return [c for c in self.chunks if not c.is_noise]
    
    @property
    def noise_chunks(self) -> List[RetrievedChunk]:
        return [c for c in self.chunks if c.is_noise]


class BaristaSimulator:
    """
    Simulates Boeing's Barista RAG tool.
    
    Features:
    - Connect to existing ChromaDB store (read-only)
    - Retrieve Top-K chunks by similarity
    - Inject noise (distractor chunks) for robustness testing
    - Assemble context in standard RAG format
    """

    def __init__(
        self,
        vector_store_path: Optional[str] = None,
        collection_name: str = "default"
    ):
        self.vector_store_path = vector_store_path
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._mock_documents: List[str] = []
        
        if vector_store_path and CHROMADB_AVAILABLE:
            self._connect()
        else:
            self._init_mock_store()

    def _connect(self):
        """Connect to existing ChromaDB store."""
        try:
            self._client = chromadb.PersistentClient(
                path=self.vector_store_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or validate collection
            collections = self._client.list_collections()
            if collections:
                self._collection = self._client.get_collection(
                    name=self.collection_name if self.collection_name in [c.name for c in collections]
                    else collections[0].name
                )
                logger.info(f"Connected to ChromaDB collection: {self._collection.name}")
            else:
                logger.warning("No collections found in ChromaDB store")
                self._init_mock_store()
                
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            self._init_mock_store()

    def _init_mock_store(self):
        """Initialize mock document store for demo/testing."""
        self._mock_documents = [
            "The Boeing 737 MAX is a narrow-body aircraft with improved fuel efficiency.",
            "Safety protocols require pre-flight checks on all control surfaces.",
            "The 787 Dreamliner uses composite materials for the fuselage.",
            "Flight crew training includes emergency procedure simulations.",
            "Wing design optimization reduces drag by approximately 8%.",
            "Maintenance schedules are determined by flight hours and cycles.",
            "The weather in Seattle is often rainy and overcast.",  # Noise
            "Coffee breaks are important for employee morale.",  # Noise
            "The parking garage has 500 spaces on level 2.",  # Noise
            "Avionics systems undergo rigorous testing before certification.",
            "Fuel consumption varies based on altitude and payload.",
            "The company cafeteria serves lunch from 11am to 2pm.",  # Noise
        ]
        logger.info("Using mock document store")

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        noise_level: float = 0.0
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: The search query
            top_k: Number of chunks to retrieve
            noise_level: 0.0-1.0, percentage of results to replace with noise
            
        Returns:
            List of RetrievedChunk objects
        """
        if self._collection:
            return self._retrieve_from_chromadb(query, top_k, noise_level)
        else:
            return self._retrieve_from_mock(query, top_k, noise_level)

    def _retrieve_from_chromadb(
        self,
        query: str,
        top_k: int,
        noise_level: float
    ) -> List[RetrievedChunk]:
        """Retrieve from actual ChromaDB store."""
        try:
            # Query ChromaDB
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k * 2  # Get extra for noise injection
            )
            
            # Convert to chunks
            chunks = []
            documents = results.get('documents', [[]])[0]
            distances = results.get('distances', [[]])[0]
            ids = results.get('ids', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            for i, doc in enumerate(documents):
                # Convert distance to similarity (assuming cosine)
                similarity = 1 - distances[i] if i < len(distances) else 0.5
                
                chunk = RetrievedChunk(
                    id=ids[i] if i < len(ids) else f"chunk_{i}",
                    content=doc,
                    similarity_score=similarity,
                    metadata=metadatas[i] if i < len(metadatas) else {},
                    is_noise=False
                )
                chunks.append(chunk)
            
            # Apply noise injection
            return self._inject_noise(chunks, top_k, noise_level)
            
        except Exception as e:
            logger.error(f"ChromaDB retrieval failed: {e}")
            return self._retrieve_from_mock(query, top_k, noise_level)

    def _retrieve_from_mock(
        self,
        query: str,
        top_k: int,
        noise_level: float
    ) -> List[RetrievedChunk]:
        """Retrieve from mock store with simulated similarity."""
        # Simple keyword matching for simulation
        query_words = set(query.lower().split())
        
        scored_docs = []
        for i, doc in enumerate(self._mock_documents):
            doc_words = set(doc.lower().split())
            overlap = len(query_words & doc_words)
            
            # Check if this is "noise" content
            noise_indicators = ["weather", "coffee", "parking", "cafeteria", "lunch"]
            is_inherent_noise = any(indicator in doc.lower() for indicator in noise_indicators)
            
            # Simulate similarity score
            similarity = overlap / max(len(query_words), 1) * 0.5 + 0.3
            if is_inherent_noise:
                similarity *= 0.3  # Lower score for noise
            
            scored_docs.append((doc, similarity, is_inherent_noise, f"mock_{i}"))
        
        # Sort by similarity
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Create chunks
        chunks = []
        for doc, sim, is_noise, doc_id in scored_docs[:top_k * 2]:
            chunks.append(RetrievedChunk(
                id=doc_id,
                content=doc,
                similarity_score=sim,
                metadata={},
                is_noise=is_noise
            ))
        
        return self._inject_noise(chunks, top_k, noise_level)

    def _inject_noise(
        self,
        chunks: List[RetrievedChunk],
        top_k: int,
        noise_level: float
    ) -> List[RetrievedChunk]:
        """
        Inject distractor chunks based on noise level.
        
        Per Living Specs Section 3.3:
        - Replace legitimate chunks with random low-similarity chunks
        - Shuffle order to prevent recency bias
        """
        if noise_level <= 0 or not chunks:
            return chunks[:top_k]
        
        num_noise = int(top_k * noise_level)
        num_legitimate = top_k - num_noise
        
        # Separate high and low similarity chunks
        sorted_chunks = sorted(chunks, key=lambda c: c.similarity_score, reverse=True)
        legitimate = sorted_chunks[:num_legitimate]
        
        # Get low-similarity chunks as noise
        noise_pool = [c for c in sorted_chunks[num_legitimate:] if c.similarity_score < 0.5]
        if len(noise_pool) < num_noise:
            # Create synthetic noise if needed
            for i in range(num_noise - len(noise_pool)):
                noise_pool.append(RetrievedChunk(
                    id=f"noise_{i}",
                    content="[Distractor content - unrelated information]",
                    similarity_score=0.1,
                    metadata={},
                    is_noise=True
                ))
        
        # Mark noise chunks
        noise_chunks = noise_pool[:num_noise]
        for chunk in noise_chunks:
            chunk.is_noise = True
        
        # Combine and shuffle
        final_chunks = legitimate + noise_chunks
        random.shuffle(final_chunks)
        
        return final_chunks

    def assemble_context(
        self,
        query: str,
        system_prompt: str,
        top_k: int = 5,
        noise_level: float = 0.0
    ) -> RAGContext:
        """
        Assemble full RAG context per Living Specs Section 3.4.
        
        Returns a formatted prompt ready for the LLM.
        """
        chunks = self.retrieve(query, top_k, noise_level)
        
        # Format chunks
        chunk_texts = []
        for chunk in chunks:
            chunk_texts.append(f"---\n{chunk.content}\n---")
        
        context_block = "\n".join(chunk_texts)
        
        # Assemble per spec
        formatted_prompt = f"""Context Information:
{context_block}

Instruction: Based on the context above, {query}"""

        return RAGContext(
            chunks=chunks,
            query=query,
            system_prompt=system_prompt,
            formatted_prompt=formatted_prompt,
            noise_level=noise_level
        )

    def get_chunk_visualization(self, chunks: List[RetrievedChunk]) -> str:
        """
        Generate HTML for chunk visualization with color coding.
        
        Per Living Specs Section 3.3:
        - Green border: High similarity (legitimate)
        - Red border: Low similarity (noise)
        """
        html_parts = []
        
        for chunk in chunks:
            if chunk.is_noise:
                border_color = "#ef4444"  # Red
                label = "🟥 NOISE"
            else:
                border_color = "#22c55e"  # Green
                label = "🟩 LEGITIMATE"
            
            html_parts.append(f"""
            <div style="border: 2px solid {border_color}; border-radius: 8px; 
                        padding: 10px; margin: 8px 0; background: #1a1a2e;">
                <div style="font-size: 11px; color: {border_color}; margin-bottom: 5px;">
                    {label} (Similarity: {chunk.similarity_score:.2f})
                </div>
                <div style="font-size: 13px; color: #FAFAFA;">
                    {chunk.content[:200]}{'...' if len(chunk.content) > 200 else ''}
                </div>
            </div>
            """)
        
        return "".join(html_parts)

    def health_check(self) -> Dict[str, Any]:
        """Check status of vector store connection."""
        return {
            "chromadb_available": CHROMADB_AVAILABLE,
            "connected": self._collection is not None,
            "collection_name": self._collection.name if self._collection else None,
            "using_mock": self._collection is None,
            "mock_doc_count": len(self._mock_documents) if self._mock_documents else 0
        }
