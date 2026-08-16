import uuid
import time
from typing import List, Dict, Optional
from threading import Lock
import logging
from datetime import datetime

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Tuning knobs ──────────────────────────────────────────────
EMBED_BATCH_SIZE = 256         # texts per SentenceTransformer.encode() call
UPSERT_BATCH_SIZE = 200        # points per Qdrant upsert() call (reduce round-trips)
QDRANT_TIMEOUT = 120           # seconds – cloud free-tier can be slow
UPSERT_RETRY_COUNT = 3         # retries per micro-batch upsert
UPSERT_RETRY_DELAY = 1         # initial backoff in seconds
# ──────────────────────────────────────────────────────────────


class VectorStoreService:
    _instance = None
    _lock = Lock()
    _known_collections: set = set()  # Cache to avoid redundant HTTP checks

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(VectorStoreService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # Try loading the model with retries
        max_retries = 3
        retry_delay = 5
        model_name = 'all-MiniLM-L6-v2'
        
        for attempt in range(max_retries):
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Successfully loaded SentenceTransformer model: {model_name}")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to load model after {max_retries} attempts: {str(e)}")
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        self._init_qdrant_client()
        self._initialized = True
        
    def _init_qdrant_client(self):
        """Initialize Qdrant client with generous timeout"""
        try:
            if settings.QDRANT_URL:
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=QDRANT_TIMEOUT,
                )
                logger.info(f"Connected to Qdrant cloud: {settings.QDRANT_URL} (timeout={QDRANT_TIMEOUT}s)")
            else:
                self.client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=QDRANT_TIMEOUT,
                )
                logger.info(f"Connected to local Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
                
            collections = self.client.get_collections()
            logger.info(f"Qdrant OK – {len(collections.collections)} collections found")
            
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise Exception(f"Failed to initialize Qdrant client: {str(e)}")
        
    def create_collection(self, collection_name: str):
        """Create a new Qdrant collection (idempotent, cached)"""
        # Fast path: skip HTTP if we already verified this collection
        if collection_name in self._known_collections:
            return

        try:
            try:
                self.client.get_collection(collection_name)
                logger.info(f"Collection {collection_name} already exists")
                self._known_collections.add(collection_name)
                return
            except Exception:
                pass
                
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {collection_name}")
            self._known_collections.add(collection_name)
            
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"Collection {collection_name} already exists (race condition)")
                self._known_collections.add(collection_name)
                return
            logger.error(f"Failed to create collection {collection_name}: {str(e)}")
            raise

    # ── Pipelined encode + upsert ──────────────────────────────
    def add_texts(self, collection_name: str, texts: List[str], metadata: List[Dict] = None):
        """
        Add text chunks to the collection.

        Uses a pipelined approach: while batch N is being upserted
        over the network, batch N+1 is already encoding on the CPU.
        This overlaps CPU work with network I/O for significant speedup.
        """
        from concurrent.futures import ThreadPoolExecutor, Future

        if not texts:
            logger.warning("No texts provided to add_texts")
            return

        total = len(texts)
        logger.info(f"add_texts: {total} texts → collection {collection_name}")

        # Ensure collection exists (cached — instant after first call)
        self.create_collection(collection_name)

        now_iso = datetime.utcnow().isoformat()
        upserted = 0
        pending_future: Future = None

        # Single background thread for upserting while we encode the next batch
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="qdrant-upsert") as executor:
            for batch_start in range(0, total, EMBED_BATCH_SIZE):
                batch_end = min(batch_start + EMBED_BATCH_SIZE, total)
                batch_texts = texts[batch_start:batch_end]

                # ── Encode this batch (CPU-bound) ──────────────
                embeddings = self.model.encode(
                    batch_texts,
                    show_progress_bar=False,
                    normalize_embeddings=True,   # pre-normalize for COSINE
                )
                logger.info(f"  Encoded {batch_start}-{batch_end} of {total}")

                # ── Build PointStruct list ─────────────────────
                points = []
                for i in range(len(batch_texts)):
                    global_i = batch_start + i
                    payload = {"text": batch_texts[i], "created_at": now_iso}
                    if metadata and global_i < len(metadata):
                        payload.update(metadata[global_i])
                    points.append(PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embeddings[i].tolist(),
                        payload=payload,
                    ))

                # ── Wait for previous upsert to finish ─────────
                if pending_future is not None:
                    pending_future.result()  # raises if the upsert failed

                # ── Fire off this upsert in background ─────────
                pending_future = executor.submit(
                    self._upsert_batch_points, collection_name, points,
                )
                upserted += len(points)
                logger.info(f"  Queued upsert {upserted}/{total} points")

            # Wait for the very last upsert to complete
            if pending_future is not None:
                pending_future.result()

        logger.info(f"✓ add_texts complete: {total} texts → {collection_name}")

    def _upsert_batch_points(self, collection_name: str, points: List[PointStruct]):
        """Upsert a batch of points, splitting into sub-batches of UPSERT_BATCH_SIZE."""
        for start in range(0, len(points), UPSERT_BATCH_SIZE):
            end = min(start + UPSERT_BATCH_SIZE, len(points))
            self._upsert_with_retry(collection_name, points[start:end])

    def _upsert_with_retry(self, collection_name: str, points: List[PointStruct]):
        """Upsert a single micro-batch with exponential backoff retries."""
        delay = UPSERT_RETRY_DELAY
        for attempt in range(UPSERT_RETRY_COUNT):
            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=points,
                    wait=False,  # Don't block until indexed — huge speedup on cloud
                )
                return
            except Exception as e:
                if attempt < UPSERT_RETRY_COUNT - 1:
                    logger.warning(
                        f"Upsert batch failed (attempt {attempt + 1}/{UPSERT_RETRY_COUNT}), "
                        f"retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                    delay *= 2
                else:
                    logger.error(f"Upsert batch failed after {UPSERT_RETRY_COUNT} attempts")
                    raise
    # ───────────────────────────────────────────────────────────

    def delete_collection(self, collection_name: str):
        """Delete a Qdrant collection"""
        try:
            result = self.client.delete_collection(collection_name)
            self._known_collections.discard(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return result
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "doesn't exist" in error_msg or "404" in error_msg:
                logger.info(f"Collection {collection_name} doesn't exist, nothing to delete")
                return
            logger.error(f"Failed to delete collection {collection_name}: {str(e)}")
            raise Exception(f"Failed to delete collection {collection_name}: {str(e)}")

    def search(self, collection_name: str, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar text chunks using query_points"""
        try:
            # Check if collection exists first
            try:
                collection_info = self.client.get_collection(collection_name)
                logger.info(f"Searching collection {collection_name}: {collection_info.points_count} total points")
            except Exception:
                logger.warning(f"Collection {collection_name} does not exist or is empty")
                return []
            
            # Encode the query to get vector (must match insertion normalization)
            query_vector = self.model.encode([query], normalize_embeddings=True)[0]
            
            # Use query_points API instead of search
            search_result = self.client.query_points(
                collection_name=collection_name,
                query=query_vector.tolist(),
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            
            results = []
            if search_result and hasattr(search_result, 'points'):
                for point in search_result.points:
                    score = float(point.score) if hasattr(point, 'score') else 0.0
                    payload = point.payload if hasattr(point, 'payload') else {}
                    results.append({
                        "text": payload.get("text", "") if payload else "",
                        "metadata": {k: v for k, v in payload.items() if k != "text"} if payload else {},
                        "score": score
                    })
            
            logger.info(f"Search returned {len(results)} results for query: '{query[:50]}...'")
            for i, r in enumerate(results[:3]):
                logger.debug(f"Result {i+1}: Score={r['score']:.3f} | Text: {r['text'][:80]}...")
            
            return results
            
        except AttributeError as e:
            if "query_points" in str(e):
                # Fallback for older qdrant-client versions that use search instead
                logger.warning(f"query_points not available, trying legacy search method: {str(e)}")
                return self._search_legacy(collection_name, query, limit)
            logger.error(f"Error searching collection {collection_name}: {str(e)}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Error searching collection {collection_name}: {str(e)}", exc_info=True)
            return []
    
    def _search_legacy(self, collection_name: str, query: str, limit: int = 5) -> List[Dict]:
        """Legacy search fallback for qdrant-client < 1.0"""
        try:
            query_vector = self.model.encode([query])[0]
            
            # Try using search method with point vectors
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector.tolist(),
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            
            results = []
            for scored_point in search_result:
                score = float(scored_point.score)
                payload = scored_point.payload if hasattr(scored_point, 'payload') else {}
                results.append({
                    "text": payload.get("text", ""),
                    "metadata": {k: v for k, v in payload.items() if k != "text"},
                    "score": score
                })
            
            return results
        except Exception as e:
            logger.error(f"Legacy search also failed: {str(e)}")
            return []

    def get_collection_info(self, collection_name: str) -> Optional[Dict]:
        """Get information about a collection"""
        try:
            collection_info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": getattr(collection_info, 'vectors_count', 0),
                "points_count": getattr(collection_info, 'points_count', 0),
                "status": str(getattr(collection_info, 'status', 'unknown')),
            }
        except Exception as e:
            logger.error(f"Error getting collection info for {collection_name}: {str(e)}")
            return {
                "name": collection_name,
                "vectors_count": 0,
                "points_count": 0,
                "status": "error"
            }

    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.get_collections()
            return [collection.name for collection in collections.collections]
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return []

    def get_collection_stats(self, collection_name: str) -> Dict:
        """Get statistics for a collection"""
        try:
            collection_info = self.client.get_collection(collection_name)
            return {
                "total_points": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "status": collection_info.status.value if collection_info.status else "unknown"
            }
        except Exception as e:
            logger.error(f"Error getting stats for collection {collection_name}: {str(e)}")
            return {
                "total_points": 0,
                "vectors_count": 0,
                "indexed_vectors_count": 0,
                "status": "error"
            }

    def scroll_collection(self, collection_name: str, limit: int = 100, offset: Optional[str] = None) -> Dict:
        """Scroll through all points in a collection"""
        try:
            result = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            return {
                "points": [
                    {
                        "id": point.id,
                        "payload": point.payload
                    }
                    for point in result[0]
                ],
                "next_page_offset": result[1]
            }
        except Exception as e:
            logger.error(f"Error scrolling collection {collection_name}: {str(e)}")
            return {"points": [], "next_page_offset": None}

    def delete_points(self, collection_name: str, point_ids: List[str]) -> bool:
        """Delete specific points from a collection"""
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=point_ids
                )
            )
            logger.info(f"Deleted {len(point_ids)} points from collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting points from collection {collection_name}: {str(e)}")
            return False

    def update_payload(self, collection_name: str, point_id: str, payload: Dict) -> bool:
        """Update payload for a specific point"""
        try:
            self.client.set_payload(
                collection_name=collection_name,
                payload=payload,
                points=[point_id]
            )
            logger.info(f"Updated payload for point {point_id} in collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating payload for point {point_id}: {str(e)}")
            return False

    def health_check(self) -> Dict:
        """Check Qdrant health and return status"""
        try:
            collections = self.client.get_collections()
            return {
                "status": "healthy",
                "collections_count": len(collections.collections),
                "message": "Qdrant is running and accessible"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "collections_count": 0,
                "message": f"Qdrant connection failed: {str(e)}"
            }
