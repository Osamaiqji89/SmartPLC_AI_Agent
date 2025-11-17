"""
Initialize RAG Knowledge Base
Loads documentation into FAISS vector store
"""

import sys
from pathlib import Path

# Add parent directory and config to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "config"))

from loguru import logger

from core.llm.rag_engine import DocumentProcessor, get_rag_engine


def load_knowledge_base():
    """Load all documentation into RAG system"""

    logger.info("Initializing RAG knowledge base...")

    # Get RAG engine
    rag_engine = get_rag_engine()
    processor = DocumentProcessor()

    # Get knowledge base directory (relative to project root)
    kb_dir = Path(__file__).parent.parent / "knowledge_base"

    if not kb_dir.exists():
        logger.error(f"Knowledge base directory not found: {kb_dir}")
        return

    total_docs = 0

    # Load markdown files
    md_files = list(kb_dir.rglob("*.md"))

    for md_file in md_files:
        logger.info(f"Processing: {md_file.name}")

        try:
            # Read file
            content = processor.load_text_file(md_file)

            if not content.strip():
                logger.warning(f"Empty file: {md_file}")
                continue

            # Chunk content
            chunks = processor.chunk_text(content, chunk_size=512, chunk_overlap=50)

            logger.info(f"  → Created {len(chunks)} chunks")

            logger.info(f"  Created {len(chunks)} chunks")

            # Prepare metadata
            category = md_file.parent.name
            if category == "knowledge_base":
                category = "general"

            metadatas = []
            for i, chunk in enumerate(chunks):
                metadatas.append(
                    {
                        "source": f"{md_file.name}",
                        "category": category,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    }
                )

            # Add to RAG
            ids = rag_engine.add_documents_batch(documents=chunks, metadatas=metadatas)

            total_docs += len(ids)

        except Exception as e:
            import traceback

            logger.error(f"Error processing {md_file}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")

    # Print statistics
    stats = rag_engine.get_stats()
    logger.info(f"✅ Knowledge base initialized:")
    logger.info(f"   Total documents: {stats['document_count']}")
    logger.info(f"   Files processed: {len(md_files)}")
    logger.info(f"   Chunks added: {total_docs}")


if __name__ == "__main__":
    load_knowledge_base()
