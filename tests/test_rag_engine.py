"""
Unit Tests for RAG Engine
"""

from core.llm.rag_engine import DocumentProcessor


class TestRAGEngine:
    """Test suite for RAG Engine"""

    def test_rag_initialization(self, rag_engine):
        """Test RAG engine initializes correctly"""
        assert rag_engine is not None
        stats = rag_engine.get_stats()
        assert stats["document_count"] == 0

    def test_add_single_document(self, rag_engine):
        """Test adding single document"""
        doc_id = rag_engine.add_document(
            content="Test document about AI_02 pressure sensor",
            metadata={"source": "test", "category": "signals"},
        )

        assert doc_id is not None
        stats = rag_engine.get_stats()
        assert stats["document_count"] == 1

    def test_add_batch_documents(self, rag_engine, sample_documents):
        """Test adding multiple documents in batch"""
        docs = [d["content"] for d in sample_documents]
        metas = [d["metadata"] for d in sample_documents]

        ids = rag_engine.add_documents_batch(docs, metas)

        assert len(ids) == len(sample_documents)
        stats = rag_engine.get_stats()
        assert stats["document_count"] == len(sample_documents)

    def test_semantic_search(self, rag_engine, sample_documents):
        """Test semantic search functionality"""
        # Add documents
        docs = [d["content"] for d in sample_documents]
        metas = [d["metadata"] for d in sample_documents]
        rag_engine.add_documents_batch(docs, metas)

        # Search for pressure sensor
        results = rag_engine.search("Drucksensor AI_02", top_k=2)

        assert len(results) > 0
        assert "AI_02" in results[0]["content"]
        assert results[0]["metadata"]["category"] == "signals"

    def test_search_with_filters(self, rag_engine, sample_documents):
        """Test search with metadata filters"""
        docs = [d["content"] for d in sample_documents]
        metas = [d["metadata"] for d in sample_documents]
        rag_engine.add_documents_batch(docs, metas)

        # Search only in error category
        results = rag_engine.search("Fehler", top_k=3, filters={"category": "errors"})

        assert len(results) > 0
        assert all(r["metadata"]["category"] == "errors" for r in results)

    def test_delete_document(self, rag_engine):
        """Test document deletion"""
        doc_id = rag_engine.add_document(content="Test document to delete", metadata={"test": True})

        # Verify added
        stats = rag_engine.get_stats()
        assert stats["document_count"] == 1

        # Delete
        success = rag_engine.delete_document(doc_id)
        assert success is True

        # Verify deleted
        stats = rag_engine.get_stats()
        assert stats["document_count"] == 0

    def test_empty_search_query(self, rag_engine):
        """Test search with empty query returns empty results"""
        results = rag_engine.search("", top_k=5)
        assert results == []

    def test_search_no_results(self, rag_engine):
        """Test search returns empty when no documents"""
        results = rag_engine.search("some query", top_k=5)
        assert results == []


class TestDocumentProcessor:
    """Test suite for Document Processor"""

    def test_chunk_text(self):
        """Test text chunking"""
        text = "This is a test. " * 100  # Create long text

        chunks = DocumentProcessor.chunk_text(text, chunk_size=100, chunk_overlap=20)

        assert len(chunks) > 1
        assert all(len(chunk) <= 100 + 50 for chunk in chunks)  # Allow some variance

    def test_chunk_short_text(self):
        """Test chunking short text"""
        text = "Short text"

        chunks = DocumentProcessor.chunk_text(text, chunk_size=100)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_empty_text(self):
        """Test chunking empty text"""
        chunks = DocumentProcessor.chunk_text("", chunk_size=100)
        assert chunks == []

    def test_chunk_with_overlap(self):
        """Test chunk overlap"""
        text = "A" * 50 + "B" * 50 + "C" * 50

        chunks = DocumentProcessor.chunk_text(text, chunk_size=60, chunk_overlap=10)

        # Check overlap exists
        assert len(chunks) >= 2
