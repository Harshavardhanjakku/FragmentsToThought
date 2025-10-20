#!/usr/bin/env python3
"""
Advanced Document Processing & Chunking System
Features:
- Content-aware chunking
- Semantic boundary preservation
- Metadata enrichment
- Multi-level chunking strategy
- Quality optimization
"""

import os
import re
import time
import shutil
from typing import List, Dict, Any
from dataclasses import dataclass
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

@dataclass
class ChunkMetadata:
    chunk_type: str
    section: str
    importance: float
    keywords: List[str]
    word_count: int

class AdvancedDocumentProcessor:
    def __init__(self):
        self.DATA_PATH = "data"
        self.CHROMA_PATH = "chroma"
        self.MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Content type patterns
        self.content_patterns = {
            "education": [
                r"education", r"degree", r"university", r"college", r"cgpa", 
                r"btech", r"cse", r"academic", r"student", r"graduation"
            ],
            "experience": [
                r"experience", r"intern", r"work", r"job", r"company", 
                r"position", r"role", r"responsibility", r"achievement"
            ],
            "projects": [
                r"project", r"developed", r"built", r"created", r"github", 
                r"repository", r"application", r"system", r"platform"
            ],
            "skills": [
                r"skill", r"technology", r"programming", r"language", 
                r"framework", r"tool", r"proficient", r"expertise"
            ],
            "achievements": [
                r"award", r"certificate", r"patent", r"competition", 
                r"hackathon", r"rank", r"place", r"winner", r"recognition"
            ],
            "personal": [
                r"about", r"name", r"contact", r"email", r"phone", 
                r"linkedin", r"profile", r"introduction"
            ]
        }
        
        # Importance keywords
        self.importance_keywords = {
            "high": ["patent", "award", "first place", "winner", "cgpa", "rank"],
            "medium": ["project", "experience", "skill", "certificate"],
            "low": ["contact", "email", "phone", "about"]
        }

    def load_documents(self) -> List[Document]:
        """Load documents with enhanced processing"""
        print("[DEBUG] Loading documents with advanced processing...")
        
        loader = DirectoryLoader(self.DATA_PATH, glob="**/*.md")
        documents = loader.load()
        
        print(f"[DEBUG] Loaded {len(documents)} documents")
        
        # Enhance documents with metadata
        enhanced_docs = []
        for doc in documents:
            enhanced_doc = self._enhance_document(doc)
            enhanced_docs.append(enhanced_doc)
        
        return enhanced_docs

    def _enhance_document(self, doc: Document) -> Document:
        """Enhance document with additional metadata"""
        content = doc.page_content
        metadata = doc.metadata.copy()
        
        # Add content analysis
        metadata["word_count"] = len(content.split())
        metadata["char_count"] = len(content)
        metadata["has_name"] = any(name in content.lower() for name in ["jakku harshavardhan", "harsha", "harshavardhan"])
        metadata["content_type"] = self._classify_content_type(content)
        
        return Document(page_content=content, metadata=metadata)

    def _classify_content_type(self, content: str) -> str:
        """Classify content type based on patterns"""
        content_lower = content.lower()
        
        # Check each content type
        for content_type, patterns in self.content_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    return content_type
        
        return "general"

    def advanced_text_splitting(self, documents: List[Document]) -> List[Document]:
        """Advanced text splitting with content awareness"""
        print("[DEBUG] Starting advanced text splitting...")
        
        all_chunks = []
        
        for doc in documents:
            content = doc.page_content
            metadata = doc.metadata.copy()
            
            # Different splitting strategies based on content type
            if metadata.get("content_type") == "education":
                chunks = self._split_education_content(content, metadata)
            elif metadata.get("content_type") == "projects":
                chunks = self._split_project_content(content, metadata)
            elif metadata.get("content_type") == "experience":
                chunks = self._split_experience_content(content, metadata)
            else:
                chunks = self._split_general_content(content, metadata)
            
            all_chunks.extend(chunks)
        
        print(f"[DEBUG] Created {len(all_chunks)} optimized chunks")
        return all_chunks

    def _split_education_content(self, content: str, metadata: Dict) -> List[Document]:
        """Specialized splitting for education content"""
        # Split by education sections
        sections = re.split(r'\n(?=🎓|Bachelor|Master|Degree|University|College)', content)
        
        chunks = []
        for i, section in enumerate(sections):
            if len(section.strip()) < 50:  # Skip very short sections
                continue
                
            # Further split if section is too long
            if len(section) > 800:
                sub_chunks = self._split_by_sentences(section, 600)
                chunks.extend(sub_chunks)
            else:
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_type": "education",
                    "section_index": i,
                    "importance": self._calculate_importance(section),
                    "keywords": self._extract_keywords(section)
                })
                chunks.append(Document(page_content=section.strip(), metadata=chunk_metadata))
        
        return chunks

    def _split_project_content(self, content: str, metadata: Dict) -> List[Document]:
        """Specialized splitting for project content"""
        # Split by project headers
        sections = re.split(r'\n(?=#### |### |## |\*\*[A-Z])', content)
        
        chunks = []
        for i, section in enumerate(sections):
            if len(section.strip()) < 50:
                continue
                
            if len(section) > 1000:
                sub_chunks = self._split_by_sentences(section, 800)
                chunks.extend(sub_chunks)
            else:
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_type": "project",
                    "section_index": i,
                    "importance": self._calculate_importance(section),
                    "keywords": self._extract_keywords(section)
                })
                chunks.append(Document(page_content=section.strip(), metadata=chunk_metadata))
        
        return chunks

    def _split_experience_content(self, content: str, metadata: Dict) -> List[Document]:
        """Specialized splitting for experience content"""
        # Split by experience entries
        sections = re.split(r'\n(?=🔹|📅|\*\*[A-Z])', content)
        
        chunks = []
        for i, section in enumerate(sections):
            if len(section.strip()) < 50:
                continue
                
            if len(section) > 900:
                sub_chunks = self._split_by_sentences(section, 700)
                chunks.extend(sub_chunks)
            else:
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_type": "experience",
                    "section_index": i,
                    "importance": self._calculate_importance(section),
                    "keywords": self._extract_keywords(section)
                })
                chunks.append(Document(page_content=section.strip(), metadata=chunk_metadata))
        
        return chunks

    def _split_general_content(self, content: str, metadata: Dict) -> List[Document]:
        """General splitting for other content types"""
        # Use RecursiveCharacterTextSplitter with optimized parameters
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        chunks = text_splitter.split_text(content)
        
        document_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_type": "general",
                "section_index": i,
                "importance": self._calculate_importance(chunk),
                "keywords": self._extract_keywords(chunk)
            })
            document_chunks.append(Document(page_content=chunk, metadata=chunk_metadata))
        
        return document_chunks

    def _split_by_sentences(self, text: str, max_length: int) -> List[Document]:
        """Split text by sentences while respecting max length"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunks.append(Document(page_content=current_chunk.strip(), metadata={}))
                current_chunk = sentence + " "
        
        if current_chunk.strip():
            chunks.append(Document(page_content=current_chunk.strip(), metadata={}))
        
        return chunks

    def _calculate_importance(self, text: str) -> float:
        """Calculate importance score for a chunk"""
        text_lower = text.lower()
        score = 0.5  # Base score
        
        # Check for high importance keywords
        for keyword in self.importance_keywords["high"]:
            if keyword in text_lower:
                score += 0.3
        
        # Check for medium importance keywords
        for keyword in self.importance_keywords["medium"]:
            if keyword in text_lower:
                score += 0.2
        
        # Check for name mentions
        if any(name in text_lower for name in ["jakku harshavardhan", "harsha"]):
            score += 0.2
        
        # Length bonus (prefer substantial content)
        if 200 <= len(text) <= 800:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        text_lower = text.lower()
        keywords = []
        
        # Extract name variations
        if "jakku harshavardhan" in text_lower:
            keywords.append("jakku_harshavardhan")
        if "harsha" in text_lower:
            keywords.append("harsha")
        
        # Extract technology keywords
        tech_keywords = ["python", "java", "javascript", "react", "node", "aws", "mysql", "mongodb"]
        for keyword in tech_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # Extract project keywords
        project_keywords = ["project", "github", "repository", "application", "system"]
        for keyword in project_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return keywords

    def save_to_chroma(self, chunks: List[Document]):
        """Save chunks to ChromaDB with enhanced processing"""
        print("[DEBUG] Removing old Chroma DB...")
        if os.path.exists(self.CHROMA_PATH):
            shutil.rmtree(self.CHROMA_PATH)
        
        print("[DEBUG] Creating embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name=self.MODEL_NAME)
        
        print("[DEBUG] Creating enhanced Chroma DB...")
        db = Chroma.from_documents(chunks, embeddings, persist_directory=self.CHROMA_PATH)
        
        print("[DEBUG] Persisting Chroma DB...")
        db.persist()
        
        print(f"[DEBUG] Successfully saved {len(chunks)} optimized chunks to {self.CHROMA_PATH}")
        
        # Print chunk statistics
        self._print_chunk_statistics(chunks)

    def _print_chunk_statistics(self, chunks: List[Document]):
        """Print detailed chunk statistics"""
        print("\n" + "="*60)
        print("CHUNK STATISTICS")
        print("="*60)
        
        # Count by type
        type_counts = {}
        importance_scores = []
        word_counts = []
        
        for chunk in chunks:
            chunk_type = chunk.metadata.get("chunk_type", "unknown")
            type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
            
            importance = chunk.metadata.get("importance", 0.5)
            importance_scores.append(importance)
            
            word_count = len(chunk.page_content.split())
            word_counts.append(word_count)
        
        print(f"Total chunks: {len(chunks)}")
        print(f"Average importance: {sum(importance_scores)/len(importance_scores):.2f}")
        print(f"Average word count: {sum(word_counts)/len(word_counts):.1f}")
        
        print("\nChunks by type:")
        for chunk_type, count in type_counts.items():
            print(f"  {chunk_type}: {count}")
        
        print("\nHigh importance chunks (>0.7):")
        high_importance = [c for c in chunks if c.metadata.get("importance", 0) > 0.7]
        print(f"  Count: {len(high_importance)}")
        
        print("="*60)

def main():
    """Main function to run advanced document processing"""
    print("[DEBUG] Starting Advanced Document Processing...")
    
    processor = AdvancedDocumentProcessor()
    
    # Step 1: Load documents
    documents = processor.load_documents()
    
    # Step 2: Advanced text splitting
    chunks = processor.advanced_text_splitting(documents)
    
    # Step 3: Save to ChromaDB
    processor.save_to_chroma(chunks)
    
    print("[DEBUG] Advanced document processing completed!")

if __name__ == "__main__":
    main()
