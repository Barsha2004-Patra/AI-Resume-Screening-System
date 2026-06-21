from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ResumeScorer:
    @staticmethod
    def calculate_similarity(resume_text: str, jd_text: str, matched_skills: List[str], total_jd_skills: List[str]) -> float:
        if not resume_text.strip() or not jd_text.strip():
            return 0.0
            
        # 1. Calculate base text similarity using TF-IDF
        documents = [resume_text, jd_text]
        vectorizer = TfidfVectorizer(stop_words='english')
        
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            text_score = float(similarity_matrix[0][0]) * 100
        except Exception:
            text_score = 0.0

        # 2. Calculate explicit skills matching coverage
        if total_jd_skills:
            skills_coverage = (len(matched_skills) / len(total_jd_skills)) * 100
        else:
            skills_coverage = text_score

        # 3. Hybrid Score: 40% overall context + 60% hard skills coverage
        final_score = (text_score * 0.4) + (skills_coverage * 0.6)
        
        return round(min(final_score, 100.0), 2)

    @classmethod
    def rank_resumes(cls, resumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(resumes, key=lambda x: x["match_score"], reverse=True)