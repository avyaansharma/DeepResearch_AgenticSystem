from typing import List, Dict

class ContentProcessor:
    def process(self, raw_data: List[Dict[str, str]]) -> List[Dict[str, any]]:
        processed_chunks = []
        for item in raw_data:
            # Simple chunking logic for now
            # In production, use semantic chunking or recursive character splitting
            content = item['markdown']
            chunks = self._chunk_text(content, 2000)
            for chunk in chunks:
                processed_chunks.append({
                    "url": item['url'],
                    "chunk": chunk,
                    "relevance_score": 1.0 # Default for now
                })
        return processed_chunks

    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
