"""
RAG Engine using FAISS
"""

import hashlib
import json
from pathlib import Path

from loguru import logger

_deps_loaded = False
_deps_available = False
_faiss = None
_np = None
_SentenceTransformer = None


def _ensure_rag_deps():
    global _deps_loaded, _deps_available, _faiss, _np, _SentenceTransformer
    if _deps_loaded:
        return _deps_available
    _deps_loaded = True

    # Fast fail: If already tried and failed, don't retry
    import os

    if os.environ.get("DISABLE_RAG") == "1":
        logger.info("RAG disabled via environment variable")
        _deps_available = False
        return False

    try:
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer

        _faiss = faiss
        _np = np
        _SentenceTransformer = SentenceTransformer
        _deps_available = True
        logger.info("RAG dependencies loaded")
        return True
    except Exception as e:
        _deps_available = False
        logger.warning(f"RAG unavailable: {e}")
        # Set env var to prevent future retries
        os.environ["DISABLE_RAG"] = "1"
        return False


class RAGEngine:
    def __init__(
        self,
        persist_dir="data/vector_store",
        collection_name="plc_knowledge",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self.embedder = None
        self.index = None
        self.documents = []
        self.metadata = []
        self.dimension = 0
        if not _ensure_rag_deps():
            return
        try:
            logger.info(f"Loading model: {self.embedding_model_name}")
            if _SentenceTransformer:
                self.embedder = _SentenceTransformer(self.embedding_model_name)
                self.dimension = self.embedder.get_sentence_embedding_dimension()
            logger.info(f"Model loaded, dim: {self.dimension}")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            return
        self._load_index()
        logger.info(f"RAG initialized ({len(self.documents)} docs)")

    def _load_index(self):
        ipath = self.persist_dir / f"{self.collection_name}.index"
        dpath = self.persist_dir / f"{self.collection_name}_docs.txt"
        mpath = self.persist_dir / f"{self.collection_name}_meta.txt"
        if ipath.exists() and _faiss and self.embedder:
            try:
                self.index = _faiss.read_index(str(ipath))
                if dpath.exists():
                    self.documents = [
                        d
                        for d in dpath.read_text(encoding="utf-8").split("\n---DOC---\n")
                        if d.strip()
                    ]
                if mpath.exists():
                    self.metadata = [
                        json.loads(line)
                        for line in mpath.read_text(encoding="utf-8").split("\n")
                        if line.strip()
                    ]
                logger.info(f"Loaded index: {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Load failed: {e}")
                self._init_new_index()
        else:
            self._init_new_index()

    def _init_new_index(self):
        if _faiss and self.embedder:
            self.index = _faiss.IndexFlatL2(self.dimension)
            logger.info("New FAISS index")

    def _save_index(self):
        if not self.index:
            return
        try:
            ipath = self.persist_dir / f"{self.collection_name}.index"
            dpath = self.persist_dir / f"{self.collection_name}_docs.txt"
            mpath = self.persist_dir / f"{self.collection_name}_meta.txt"
            if _faiss:
                _faiss.write_index(self.index, str(ipath))
            dpath.write_text("\n---DOC---\n".join(self.documents), encoding="utf-8")
            mpath.write_text(
                "\n".join(json.dumps(m, ensure_ascii=False) for m in self.metadata),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"Save failed: {e}")

    def add_documents_batch(self, documents, metadatas=None, ids=None):
        if not self.embedder or not self.index or not documents:
            return []
        if ids is None:
            ids = [self._generate_doc_id(doc) for doc in documents]
        if metadatas is None:
            metadatas = [{}] * len(documents)
        for i, (doc, doc_id) in enumerate(zip(documents, ids, strict=False)):
            metadatas[i]["id"] = doc_id
            metadatas[i]["length"] = len(doc)
        try:
            logger.info(f"Embedding {len(documents)} docs...")
            embeddings = self.embedder.encode(documents, show_progress_bar=True)
            if _np:
                embeddings = _np.array(embeddings).astype("float32")
                self.index.add(embeddings)
            self.documents.extend(documents)
            self.metadata.extend(metadatas)
            logger.info(f"Added {len(documents)} docs (total: {self.index.ntotal})")
            self._save_index()
            return ids
        except Exception as e:
            logger.error(f"Batch add failed: {e}")
            return []

    def search(self, query, top_k=3, filters=None):
        if not self.embedder or not self.index or self.index.ntotal == 0:
            return []
        if not query.strip():
            return []
        try:
            query_emb = self.embedder.encode([query])
            if _np:
                query_emb = _np.array(query_emb).astype("float32")
            k = min(top_k, len(self.documents))
            distances, indices = self.index.search(query_emb, k)
            results = []
            for dist, idx in zip(distances[0], indices[0], strict=False):
                if 0 <= idx < len(self.documents):
                    score = float(1 / (1 + dist))
                    result = {
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx] if idx < len(self.metadata) else {},
                        "distance": float(dist),
                        "score": score,
                        "id": (
                            self.metadata[idx].get("id", str(idx))
                            if idx < len(self.metadata)
                            else str(idx)
                        ),
                    }
                    if filters:
                        if all(result["metadata"].get(k) == v for k, v in filters.items()):
                            results.append(result)
                    else:
                        results.append(result)
            logger.debug(f"Search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def count(self):
        return len(self.documents)

    def get_stats(self):
        return {
            "collection_name": self.collection_name,
            "document_count": len(self.documents),
            "total_vectors": self.index.ntotal if self.index else 0,
            "embedding_model": self.embedding_model_name,
            "dimension": self.dimension,
        }

    def _generate_doc_id(self, content):
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class DocumentProcessor:
    @staticmethod
    def chunk_text(text, chunk_size=512, chunk_overlap=50):
        if not text:
            return []
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)

            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move forward - ALWAYS progress
            start = start + chunk_size - chunk_overlap

            # Safety: ensure we move at least 1 character forward
            if chunk_overlap >= chunk_size:
                start = start + 1

            if start >= text_len:
                break

        return chunks

    @staticmethod
    def load_text_file(file_path):
        return Path(file_path).read_text(encoding="utf-8")

    @staticmethod
    def process_pdf(file_path):
        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() for page in reader.pages)
        except Exception:  # noqa: BLE001
            return ""


def build_context_for_signal(rag_engine, signal_name, signal_metadata, top_k=3):
    query = f"Erkläre Signal {signal_name} {signal_metadata.get('type', '')} {signal_metadata.get('description', '')}"
    results = rag_engine.search(query, top_k=top_k)
    context = ["=== SIGNAL METADATA ===", f"Name: {signal_name}"]
    context.extend(f"{k}: {v}" for k, v in signal_metadata.items())
    if results:
        context.append("\n=== RELEVANT DOCUMENTATION ===")
        for i, r in enumerate(results, 1):
            context.append(
                f"\n--- Doc {i} (Source: {r['metadata'].get('source', 'Unknown')}, Score: {r.get('score', 0):.3f}) ---"
            )
            context.append(r["content"])
    return "\n".join(context)


_rag_instance = None


def get_rag_engine():
    global _rag_instance
    if _rag_instance is None:
        import sys
        from pathlib import Path

        # Add config to path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
        from config import settings

        _rag_instance = RAGEngine(
            persist_dir="data/vector_store", embedding_model=settings.embedding_model
        )
    return _rag_instance
