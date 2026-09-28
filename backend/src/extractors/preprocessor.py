import re
import spacy
import logging

logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("Spacy model 'en_core_web_sm' not found. Ensure it was downloaded.")
    nlp = None

def normalize_text(text: str) -> str:
    """Normalizes text by replacing odd characters and standardizing whitespace."""
    # Replace non-breaking spaces and tabs with regular spaces
    text = re.sub(r'[\xa0\t]+', ' ', text)
    # Remove page break artifacts if any
    text = re.sub(r'--- PAGE BREAK ---', '\n\n', text)
    return text.strip()

def clean_text_for_ml(text: str) -> str:
    """
    Cleans text specifically for ML models:
    - Lowercase
    - Lemmatization
    - Remove punctuation, stop words, and numbers/symbols
    """
    if not nlp:
        # Fallback if no spaCy model
        text = text.lower()
        return re.sub(r'[^a-z\s]', '', text).strip()
        
    doc = nlp(text)
    clean_tokens = [
        token.lemma_.lower() for token in doc 
        if not token.is_stop 
        and not token.is_punct 
        and not token.is_space
        and token.is_alpha  # Only keep alphabetic words
    ]
    return " ".join(clean_tokens)

def segment_clauses(full_text: str) -> list:
    """
    Segments full document text into individual clauses.
    Preserves original text for display and creates clean_text for ML.
    """
    full_text = normalize_text(full_text)
    
    # Heuristic 1: Split by double newlines or numbered list patterns (1., 2., a), etc.)
    # We'll use a regex that looks for double newlines OR a number/letter followed by a dot at the start of a line/space.
    # To keep it simple and robust, let's pre-process numbered lists to ensure they have double newlines before them.
    full_text = re.sub(r'(\s+)(\d+\.\s+[A-Z])', r'\n\n\2', full_text)
    
    raw_blocks = re.split(r'\n\s*\n', full_text)
    
    clauses = []
    clause_id = 1
    
    for block in raw_blocks:
        block = block.strip()
        # Remove single newlines within a block (join lines)
        block = re.sub(r'(?<!\n)\n(?!\n)', ' ', block)
        
        if not block or len(block) < 15: # Ignore very short fragments
            continue
            
        # Heuristic 2: If a block is moderately long (>40 words), it might be multiple squashed clauses.
        # Let's segment by sentence using spaCy if it's over 40 words.
        word_count = len(block.split())
        if word_count > 40 and nlp:
            doc = nlp(block)
            for sent in doc.sents:
                sent_text = sent.text.strip()
                if len(sent_text) > 15:
                    clauses.append({
                        "clause_id": clause_id,
                        "text": sent_text,
                        "clean_text": clean_text_for_ml(sent_text)
                    })
                    clause_id += 1
        else:
            clauses.append({
                "clause_id": clause_id,
                "text": block,
                "clean_text": clean_text_for_ml(block)
            })
            clause_id += 1
            
    return clauses
