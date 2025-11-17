"""Test RAG Loading"""

import sys
from pathlib import Path

# Add config to path
sys.path.insert(0, str(Path(__file__).parent / "config"))

print("Testing RAG engine...")
from core.llm.rag_engine import get_rag_engine  # noqa: E402

rag = get_rag_engine()
print(f"\nRAG Status: {'✅ AKTIV' if rag and rag.index else '❌ NICHT AKTIV'}")

if rag and rag.index:
    print(f"Dokumente geladen: {len(rag.documents)}")
    print(f"Index Größe: {rag.index.ntotal} Vektoren")

    # Test search
    results = rag.search("pressure sensor", top_k=3)
    print(f"\nTest-Suche 'pressure sensor': {len(results)} Ergebnisse")
    for i, (doc, score) in enumerate(results, 1):
        print(f"  {i}. Score: {score:.3f} - {doc[:80]}...")
else:
    print("RAG konnte nicht geladen werden!")
