from typing import Dict, List


class RecursiveChunker:
    def __init__(
        self,
        normalized_documents_contents: List[Dict],
        chunk_size,
        overlap=20,
        separator=None,
    ) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.normalized_documents_contents = normalized_documents_contents
        self.default_separators = (
            separator if separator is not None else ["\n\n", "\n", ".", " ", ""]
        )

    def __r_chunker(self, normalized_content, separators):
        if len(normalized_content) <= self.chunk_size:
            return [normalized_content] if normalized_content.strip() else []

        separator = self.default_separators[-1]
        remaining_separator = []
        for i, sep in enumerate(self.default_separators):
            if sep == "" or sep in normalized_content:
                separator = sep
                remaining_separator = separators[i + 1 :]
                break
        if separator:
            splits = normalized_content.split(separator)
        else:
            splits = list(normalized_content)
        chunks = []
        current_chunk = ""

        for part in splits:
            piece = part + separator if separator else part
            if len(current_chunk) + len(piece) <= self.chunk_size:
                current_chunk += piece
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if len(piece) > self.chunk_size:
                    chunks.extend(self.__r_chunker(piece, remaining_separator))
                    current_chunk = ""
                else:
                    current_chunk = piece
        if current_chunk:
            chunks.append(current_chunk)

        if self.overlap > 0 and len(chunks) > 1:
            overlapped = [chunks[0]]
            for i in range(1, len(chunks)):
                prev_tail = chunks[i - 1][-self.overlap :]
                overlapped.append(prev_tail + chunks[i])
            chunks = overlapped
        return chunks

    def recursive_chunker(self) -> List[Dict]:
        """
        Output format
        [
            {
                Chunks = [chunk_one , chunk_two , ... , chunk_n]
                metadata = {
                    document_name : document_name,
                    document_id : document_id
                }
            }
        ]

        """
        chunk_values: List[Dict] = []
        for normalized_document_content in self.normalized_documents_contents:
            document_id = normalized_document_content["metadata"]["document_id"]
            document_name = normalized_document_content["metadata"]["source_file"]
            normalized_content = normalized_document_content["content"]
            chunks = self.__r_chunker(normalized_content, self.default_separators)
            chunk_values.append(
                {
                    "chunks": chunks,
                    "metadata": {
                        "document_name": document_name,
                        "document_id": document_id,
                    },
                }
            )
        return chunk_values
