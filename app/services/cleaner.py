import re
import unicodedata
from typing import Dict


class CleanerService:
    """
    Rule-based text cleaning service for OCR output.
    EU compliant - no external LLM calls for sensitive data.
    Optimized for Mistral OCR Markdown output.
    """
    
    # Common OCR mistakes mapping
    OCR_CORRECTIONS = {
        'O': '0',  # Letter O to zero (contextual)
        'l': '1',  # Letter l to one (contextual)
        'I': '1',  # Letter I to one (contextual)
        'S': '5',  # Letter S to five (contextual)
        'Z': '2',  # Letter Z to two (contextual)
    }
    
    def __init__(self):
        pass
    
    def clean_text(self, text: str) -> str:
        """
        Clean OCR text using rule-based methods only.
        Optimized for Mistral OCR Markdown output.
        """
        if not text:
            return ""
        
        # 1. Unicode normalization (NFC form)
        text = unicodedata.normalize('NFC', text)
        
        # 2. Remove Markdown image references
        text = self._remove_markdown_images(text)
        
        # 3. Remove empty/useless Markdown tables
        text = self._clean_markdown_tables(text)
        
        # 4. Remove masked/redacted patterns (***_*** etc.)
        text = self._remove_masked_patterns(text)
        
        # 5. Remove non-printable characters
        text = self._remove_non_printable(text)
        
        # 6. Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 7. Remove excessive whitespace
        text = self._normalize_whitespace(text)
        
        # 8. Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        # 9. Remove scanning artifacts
        text = self._remove_artifacts(text)
        
        # 10. Remove duplicate text blocks
        text = self._remove_duplicate_blocks(text)
        
        # 11. Format paragraphs
        text = self._format_paragraphs(text)
        
        # 12. Final cleanup
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def _remove_markdown_images(self, text: str) -> str:
        """Remove Markdown image references like ![img-0.jpeg](img-0.jpeg)"""
        # Remove image syntax: ![alt](src)
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
        # Remove standalone image filenames
        text = re.sub(r'\bimg-\d+\.(jpeg|jpg|png|gif|webp)\b', '', text, flags=re.IGNORECASE)
        return text
    
    def _clean_markdown_tables(self, text: str) -> str:
        """
        Clean up Markdown tables:
        - Remove tables with only empty cells
        - Remove excessive table separators
        - Simplify tables with actual content
        """
        lines = text.split('\n')
        cleaned_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if it's a table row
            if '|' in line:
                # Check if the row has any real content
                # Remove | and --- and whitespace, see what's left
                content = re.sub(r'[\|\-\s]', '', line)
                
                # If it's a table separator row (| --- | --- |)
                if re.match(r'^[\|\s\-:]+$', line):
                    # Keep separator only if previous line was a header with content
                    if cleaned_lines and '|' in cleaned_lines[-1]:
                        prev_content = re.sub(r'[\|\-\s]', '', cleaned_lines[-1])
                        if prev_content and len(prev_content) > 3:
                            cleaned_lines.append(line)
                # If row has actual content (more than just punctuation)
                elif content and len(content) > 2 and not re.match(r'^[\*\_\s]+$', content):
                    # Clean up excessive empty cells
                    # Replace multiple empty cells with single separator
                    cleaned_row = re.sub(r'\|\s*\|\s*(\|\s*)+', '| ', line)
                    cleaned_row = cleaned_row.strip()
                    if cleaned_row and cleaned_row != '|' and cleaned_row != '| |':
                        cleaned_lines.append(cleaned_row)
            else:
                cleaned_lines.append(line)
            
            i += 1
        
        return '\n'.join(cleaned_lines)
    
    def _remove_masked_patterns(self, text: str) -> str:
        """
        Remove patterns used for masking/redacting data in OCR output.
        Examples: ***_******_***, _____, etc.
        """
        # Remove long sequences of asterisks with underscores (masked data)
        text = re.sub(r'(\*{2,}[_\*]*){2,}', '[REDACTED]', text)
        
        # Remove very long underscore sequences (10+)
        text = re.sub(r'_{10,}', '', text)
        
        # Remove long sequences of dots (but preserve ellipsis ...)
        text = re.sub(r'\.{10,}', '', text)
        
        # Remove repeated dot patterns used as form fillers
        text = re.sub(r'(\.\s*){10,}', '', text)
        
        # Clean up [REDACTED] if there are multiple in a row
        text = re.sub(r'(\[REDACTED\]\s*){2,}', '[REDACTED] ', text)
        
        return text
    
    def _remove_non_printable(self, text: str) -> str:
        """Remove non-printable characters except whitespace"""
        printable_chars = []
        for char in text:
            if char.isprintable() or char in ['\n', '\t', ' ']:
                printable_chars.append(char)
            elif unicodedata.category(char)[0] == 'C':
                printable_chars.append(' ')
            else:
                printable_chars.append(char)
        
        return ''.join(printable_chars)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize various types of whitespace"""
        # Replace multiple spaces with single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Remove spaces at the beginning and end of lines
        lines = [line.strip() for line in text.split('\n')]
        
        # Remove empty lines but preserve paragraph breaks (max 2 newlines)
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR misreads (contextual)."""
        # Fix common date patterns: O1/O1/2O23 -> 01/01/2023
        text = re.sub(
            r'\b([O0])(\d)/([O0])(\d)/([12O])([O0])(\d{2})\b', 
            lambda m: f"{m.group(1).replace('O', '0')}{m.group(2)}/{m.group(3).replace('O', '0')}{m.group(4)}/{m.group(5).replace('O', '2')}{m.group(6).replace('O', '0')}{m.group(7)}", 
            text
        )
        
        # Fix Slovak Rodné číslo patterns: 95O515/1234 -> 950515/1234
        text = re.sub(
            r'\b(\d{2})([O0])(\d{3})/(\d{3,4})\b',
            lambda m: f"{m.group(1)}{m.group(2).replace('O', '0')}{m.group(3)}/{m.group(4)}",
            text
        )
        
        # Fix IBAN patterns with O->0
        text = re.sub(
            r'\b(SK|IT|DE)(\d{2})([O0\d\s]+)\b',
            lambda m: m.group(1) + m.group(2) + m.group(3).replace('O', '0'),
            text
        )
        
        return text
    
    def _remove_artifacts(self, text: str) -> str:
        """Remove scanning and OCR artifacts"""
        # Remove excessive dots (but keep ellipsis)
        text = re.sub(r'\.{4,}', '...', text)
        
        # Remove excessive dashes (keep max 3)
        text = re.sub(r'-{4,}', '---', text)
        
        # Remove excessive equals
        text = re.sub(r'={4,}', '', text)
        
        # Remove lines that are only dashes/equals/underscores
        text = re.sub(r'^[\-=_]{3,}$', '', text, flags=re.MULTILINE)
        
        return text
    
    def _remove_duplicate_blocks(self, text: str) -> str:
        """
        Remove duplicate text blocks that often appear in OCR output.
        Uses multiple strategies to detect and remove duplicates.
        """
        # Strategy 1: Remove duplicate paragraphs (separated by empty lines)
        text = self._remove_duplicate_paragraphs(text)
        
        # Strategy 2: Remove duplicate sentences within paragraphs
        text = self._remove_duplicate_sentences(text)
        
        # Strategy 3: Remove consecutive duplicate lines
        text = self._remove_consecutive_duplicates(text)
        
        return text
    
    def _remove_duplicate_paragraphs(self, text: str) -> str:
        """Remove exact duplicate paragraphs"""
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)
        
        seen = set()
        unique_paragraphs = []
        
        for para in paragraphs:
            # Normalize for comparison (lowercase, strip, collapse whitespace)
            normalized = re.sub(r'\s+', ' ', para.strip().lower())
            
            # Skip very short paragraphs from duplicate detection
            if len(normalized) < 20:
                unique_paragraphs.append(para)
                continue
            
            # Use first 100 chars as key to catch near-duplicates
            key = normalized[:100] if len(normalized) > 100 else normalized
            
            if key not in seen:
                seen.add(key)
                unique_paragraphs.append(para)
        
        return '\n\n'.join(unique_paragraphs)
    
    def _remove_duplicate_sentences(self, text: str) -> str:
        """Remove duplicate sentences that start the same way"""
        lines = text.split('\n')
        result_lines = []
        seen_sentence_starts = set()
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines and table rows
            if not stripped or stripped.startswith('|'):
                result_lines.append(line)
                continue
            
            # Get first 50 chars as sentence key
            sentence_key = re.sub(r'\s+', ' ', stripped.lower())[:50]
            
            # Only filter longer, meaningful sentences
            if len(stripped) > 30 and sentence_key in seen_sentence_starts:
                continue
            
            if len(stripped) > 30:
                seen_sentence_starts.add(sentence_key)
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _remove_consecutive_duplicates(self, text: str) -> str:
        """Remove consecutive duplicate lines"""
        lines = text.split('\n')
        result_lines = []
        prev_normalized = None
        
        for line in lines:
            normalized = re.sub(r'\s+', ' ', line.strip().lower())
            
            # Keep empty lines to preserve structure
            if not normalized:
                if result_lines and result_lines[-1].strip():
                    result_lines.append(line)
                continue
            
            # Skip if same as previous
            if normalized == prev_normalized:
                continue
            
            result_lines.append(line)
            prev_normalized = normalized
        
        return '\n'.join(result_lines)
    
    def _format_paragraphs(self, text: str) -> str:
        """Format paragraphs properly"""
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                formatted_lines.append(line)
            elif formatted_lines and formatted_lines[-1] != '':
                formatted_lines.append('')
        
        text = '\n'.join(formatted_lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def get_cleaning_stats(self, original: str, cleaned: str) -> Dict[str, any]:
        """Get statistics about the cleaning process."""
        original_len = len(original) if original else 0
        cleaned_len = len(cleaned) if cleaned else 0
        
        return {
            "original_length": original_len,
            "cleaned_length": cleaned_len,
            "characters_removed": original_len - cleaned_len,
            "reduction_percent": round((1 - cleaned_len / original_len) * 100, 1) if original_len > 0 else 0,
            "original_lines": original.count('\n') + 1 if original else 0,
            "cleaned_lines": cleaned.count('\n') + 1 if cleaned else 0,
        }
