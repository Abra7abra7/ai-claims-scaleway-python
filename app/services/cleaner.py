import re
import unicodedata
from typing import Dict


class CleanerService:
    """
    Rule-based text cleaning service for OCR output.
    EU compliant - no external LLM calls for sensitive data.
    """
    
    # Common OCR mistakes mapping
    OCR_CORRECTIONS = {
        # Numbers vs Letters
        'O': '0',  # Letter O to zero (contextual)
        'l': '1',  # Letter l to one (contextual)
        'I': '1',  # Letter I to one (contextual)
        'S': '5',  # Letter S to five (contextual)
        'Z': '2',  # Letter Z to two (contextual)
    }
    
    # Patterns for common OCR artifacts
    ARTIFACT_PATTERNS = [
        r'\|',  # Vertical bars from scanning artifacts
        r'[_]{2,}',  # Multiple underscores
        r'[\^\~]{2,}',  # Tildes and carets
    ]
    
    def __init__(self):
        pass
    
    def clean_text(self, text: str) -> str:
        """
        Clean OCR text using rule-based methods only.
        
        Steps:
        1. Unicode normalization
        2. Remove non-printable characters
        3. Normalize whitespace
        4. Remove duplicate spaces
        5. Fix common OCR errors
        6. Remove scanning artifacts
        7. Format paragraphs
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # 1. Unicode normalization (NFC form)
        text = unicodedata.normalize('NFC', text)
        
        # 2. Remove non-printable characters (keep newlines, tabs)
        text = self._remove_non_printable(text)
        
        # 3. Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 4. Remove excessive whitespace
        text = self._normalize_whitespace(text)
        
        # 5. Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        # 6. Remove scanning artifacts
        text = self._remove_artifacts(text)
        
        # 7. Format paragraphs
        text = self._format_paragraphs(text)
        
        # 8. Final cleanup - remove duplicate spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def _remove_non_printable(self, text: str) -> str:
        """Remove non-printable characters except whitespace"""
        printable_chars = []
        for char in text:
            # Keep printable characters and common whitespace
            if char.isprintable() or char in ['\n', '\t', ' ']:
                printable_chars.append(char)
            # Replace control characters with space
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
        """
        Fix common OCR misreads.
        This is contextual - only fix in specific patterns.
        """
        # Fix common date patterns: O1/O1/2O23 -> 01/01/2023
        text = re.sub(r'\b([O0])(\d)/([O0])(\d)/([12O])([O0])(\d{2})\b', 
                     lambda m: f"{m.group(1).replace('O', '0')}{m.group(2)}/{m.group(3).replace('O', '0')}{m.group(4)}/{m.group(5).replace('O', '2')}{m.group(6).replace('O', '0')}{m.group(7)}", 
                     text)
        
        # Fix Slovak Rodné číslo patterns: 95O515/1234 -> 950515/1234
        text = re.sub(r'\b(\d{2})([O0])(\d{3})/(\d{3,4})\b',
                     lambda m: f"{m.group(1)}{m.group(2).replace('O', '0')}{m.group(3)}/{m.group(4)}",
                     text)
        
        # Fix IBAN patterns with O->0
        text = re.sub(r'\b(SK|IT|DE)(\d{2})([O0\d\s]+)\b',
                     lambda m: m.group(1) + m.group(2) + m.group(3).replace('O', '0'),
                     text)
        
        # Fix phone numbers: +42l 9OO -> +421 900
        text = re.sub(r'\+(\d{2})([lI1])(\s*)(\d?)([O0])(\d)',
                     lambda m: f"+{m.group(1)}{m.group(2).replace('l', '1').replace('I', '1')}{m.group(3)}{m.group(4)}{m.group(5).replace('O', '0')}{m.group(6)}",
                     text)
        
        return text
    
    def _remove_artifacts(self, text: str) -> str:
        """Remove scanning and OCR artifacts"""
        for pattern in self.ARTIFACT_PATTERNS:
            text = re.sub(pattern, '', text)
        
        # Remove excessive dots (but keep ellipsis)
        text = re.sub(r'\.{4,}', '...', text)
        
        # Remove excessive dashes
        text = re.sub(r'-{3,}', '--', text)
        
        return text
    
    def _format_paragraphs(self, text: str) -> str:
        """Format paragraphs properly"""
        # Split into lines
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                formatted_lines.append(line)
            elif formatted_lines and formatted_lines[-1] != '':
                # Add empty line for paragraph break
                formatted_lines.append('')
        
        # Join and normalize paragraph breaks
        text = '\n'.join(formatted_lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def get_cleaning_stats(self, original: str, cleaned: str) -> Dict:
        """
        Get statistics about the cleaning process.
        
        Args:
            original: Original text
            cleaned: Cleaned text
            
        Returns:
            Dictionary with cleaning statistics including reduction percentage
        """
        original_len = len(original)
        cleaned_len = len(cleaned)
        
        # Calculate reduction percentage
        if original_len > 0:
            reduction_percent = round((1 - cleaned_len / original_len) * 100, 1)
        else:
            reduction_percent = 0.0
        
        return {
            "original_length": original_len,
            "cleaned_length": cleaned_len,
            "characters_removed": original_len - cleaned_len,
            "reduction_percent": reduction_percent,
            "original_lines": original.count('\n') + 1,
            "cleaned_lines": cleaned.count('\n') + 1,
        }

