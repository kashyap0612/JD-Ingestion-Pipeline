import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, index_path: Path, metadata_path: Path, model_name: str):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.encoder = SentenceTransformer(model_name)
        self.dimension = self.encoder.get_sentence_embedding_dimension()
        self.index = self._load_or_create_index()
        if not self.metadata_path.exists():
            self.metadata_path.write_text("[]", encoding="utf-8")

    def _load_or_create_index(self) -> faiss.IndexFlatL2:
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        return faiss.IndexFlatL2(self.dimension)

    def _append_metadata(self, rows: list[dict]) -> None:
        existing = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        existing.extend(rows)
        self.metadata_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    def add_chunks(self, chunks: list[str], metadatas: list[dict]) -> int:
        if not chunks:
            return 0
        vectors = self.encoder.encode(chunks, normalize_embeddings=True)
        matrix = np.asarray(vectors, dtype="float32")
        self.index.add(matrix)
        faiss.write_index(self.index, str(self.index_path))
        self._append_metadata(metadatas)
        return len(chunks)
