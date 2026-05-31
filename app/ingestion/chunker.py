from pydantic import BaseModel
from typing import Any
from app.ingestion.document_loader import Document

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    doc_type: str
    text: str
    section: str | None
    chunk_index: int
    metadata: dict[str, Any]
    source_path: str

def split_into_sections(text: str) -> list[dict[str, Any]]:
    """
    Splits markdown text into sections based on headings (#, ##, ###).
    Returns a list of dicts: [{'heading': str | None, 'text': str}]
    """
    sections = []
    current_heading = None
    current_lines = []
    
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            # Count leading '#'
            h_count = 0
            for char in stripped:
                if char == '#':
                    h_count += 1
                else:
                    break
            
            # Ensure it is a valid header followed by a space
            if h_count > 0 and h_count < len(stripped) and stripped[h_count] == ' ':
                # Save previous section if it has content
                section_text = "\n".join(current_lines).strip()
                if section_text or current_heading:
                    sections.append({"heading": current_heading, "text": section_text})
                
                # Start new section
                current_heading = stripped[h_count:].strip()
                current_lines = []
                continue
                
        current_lines.append(line)
        
    # Save the final section
    section_text = "\n".join(current_lines).strip()
    if section_text or current_heading:
        sections.append({"heading": current_heading, "text": section_text})
        
    return sections

def chunk_text(text: str, target_words: int = 700, overlap_words: int = 100) -> list[str]:
    """
    Splits a raw string into overlapping word-based chunks.
    Ensures that no empty chunks are created.
    """
    words = text.split()
    if not words:
        return []
        
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + target_words]
        chunk_text_str = " ".join(chunk_words).strip()
        if chunk_text_str:
            chunks.append(chunk_text_str)
            
        if i + target_words >= len(words):
            break
            
        advance = max(1, target_words - overlap_words)
        i += advance
            
    return chunks

def chunk_document(document: Document, target_words: int = 700, overlap_words: int = 100) -> list[DocumentChunk]:
    """
    Chunks a single Document into a list of DocumentChunks using section-aware logic.
    """
    sections = split_into_sections(document.text)
    
    # Filter out empty sections
    valid_sections = [s for s in sections if s["text"].strip()]
    
    chunks_data = []
    chunk_index = 0
    
    if not valid_sections:
        # Fallback to standard word-based sliding window chunking
        text_chunks = chunk_text(document.text, target_words, overlap_words)
        for t_chunk in text_chunks:
            chunk_id = f"{document.doc_id}::chunk_{chunk_index:03d}"
            chunks_data.append(DocumentChunk(
                chunk_id=chunk_id,
                doc_id=document.doc_id,
                title=document.title,
                doc_type=document.doc_type,
                text=t_chunk,
                section=None,
                chunk_index=chunk_index,
                metadata=document.metadata,
                source_path=document.source_path
            ))
            chunk_index += 1
    else:
        for sec in valid_sections:
            sec_text = sec["text"]
            sec_heading = sec["heading"]
            sec_words = sec_text.split()
            
            threshold = target_words + overlap_words
            if len(sec_words) <= threshold:
                # Keep whole section as one chunk
                chunk_id = f"{document.doc_id}::chunk_{chunk_index:03d}"
                chunks_data.append(DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=document.doc_id,
                    title=document.title,
                    doc_type=document.doc_type,
                    text=sec_text,
                    section=sec_heading,
                    chunk_index=chunk_index,
                    metadata=document.metadata,
                    source_path=document.source_path
                ))
                chunk_index += 1
            else:
                # Split too-long section into overlapping word chunks
                text_chunks = chunk_text(sec_text, target_words, overlap_words)
                for t_chunk in text_chunks:
                    chunk_id = f"{document.doc_id}::chunk_{chunk_index:03d}"
                    chunks_data.append(DocumentChunk(
                        chunk_id=chunk_id,
                        doc_id=document.doc_id,
                        title=document.title,
                        doc_type=document.doc_type,
                        text=t_chunk,
                        section=sec_heading,
                        chunk_index=chunk_index,
                        metadata=document.metadata,
                        source_path=document.source_path
                    ))
                    chunk_index += 1
                    
    return chunks_data

def chunk_documents(documents: list[Document], target_words: int = 700, overlap_words: int = 100) -> list[DocumentChunk]:
    """
    Chunks a list of Documents and returns a unified list of DocumentChunks.
    """
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc, target_words, overlap_words))
    return all_chunks
