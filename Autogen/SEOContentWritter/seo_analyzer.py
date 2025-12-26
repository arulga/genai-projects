"""SEO Analysis Utilities"""
from typing import List, Dict, Any

class SEOAnalyzer:
    """SEO analysis utilities"""
    
    @staticmethod
    def calculate_keyword_score(content: str, keywords: List[str]) -> float:
        """Calculate keyword optimization score"""
        if not content or not keywords:
            return 0.0
            
        content_lower = content.lower()
        total_words = len(content.split())
        
        if total_words == 0:
            return 0.0
        
        keyword_counts = sum(content_lower.count(kw.lower()) for kw in keywords)
        keyword_density = (keyword_counts / total_words) * 100
        
        # Optimal density: 1-2%
        if 1.0 <= keyword_density <= 2.0:
            return 10.0
        elif 0.5 <= keyword_density < 1.0 or 2.0 < keyword_density <= 3.0:
            return 7.0
        else:
            return 4.0
    
    @staticmethod
    def calculate_readability_score(content: str) -> float:
        """Calculate readability score"""
        if not content:
            return 0.0
            
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        words = content.split()
        
        if len(sentences) == 0 or len(words) == 0:
            return 5.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Optimal: 15-20 words per sentence
        if 15 <= avg_words_per_sentence <= 20:
            return 10.0
        elif 10 <= avg_words_per_sentence < 15 or 20 < avg_words_per_sentence <= 25:
            return 7.0
        else:
            return 5.0
    
    @staticmethod
    def calculate_structure_score(content: str) -> float:
        """Evaluate content structure"""
        score = 0.0
        
        # Check for headings
        if '# ' in content:
            score += 2.0
        if '## ' in content:
            score += 2.0
        if '### ' in content:
            score += 1.0
        
        # Check word count
        word_count = len(content.split())
        if 800 <= word_count <= 2000:
            score += 3.0
        elif 500 <= word_count < 800:
            score += 2.0
        
        # Check for lists
        if '- ' in content or '* ' in content:
            score += 2.0
        
        return min(score, 10.0)
    
    @staticmethod
    def calculate_overall_seo_score(content: str, keywords: List[str]) -> Dict[str, Any]:
        """Calculate comprehensive SEO score"""
        keyword_score = SEOAnalyzer.calculate_keyword_score(content, keywords)
        readability_score = SEOAnalyzer.calculate_readability_score(content)
        structure_score = SEOAnalyzer.calculate_structure_score(content)
        
        # Weighted average
        overall_score = (
            keyword_score * 0.4 +
            readability_score * 0.3 +
            structure_score * 0.3
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "keyword_score": round(keyword_score, 2),
            "readability_score": round(readability_score, 2),
            "structure_score": round(structure_score, 2),
            "breakdown": {
                "keyword_optimization": f"{keyword_score}/10",
                "readability": f"{readability_score}/10",
                "content_structure": f"{structure_score}/10"
            }
        }