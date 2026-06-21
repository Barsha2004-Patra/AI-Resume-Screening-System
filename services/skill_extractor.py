import re
from typing import List, Set

class SkillExtractor:
    SKILLS_DATABASE = [
        "python", "java", "c++", "javascript", "typescript", "html", "css", "sql", "nosql",
        "mongodb", "postgresql", "mysql", "redis", "aws", "azure", "gcp", "docker", "kubernetes",
        "fastapi", "flask", "django", "react", "angular", "vue", "node.js", "express", "spring",
        "scikit-learn", "tensorflow", "pytorch", "keras", "nlp", "bert", "gpt", "llm", "pandas",
        "numpy", "scipy", "tableau", "powerbi", "excel", "git", "ci/cd", "jenkins", "agile",
        "scrum", "devops", "mlops", "spark", "hadoop", "kafka", "graphql", "rest api", "microservices"
    ]

    @classmethod
    def extract_skills(cls, text: str) -> List[str]:
        extracted_skills: Set[str] = set()
        text_lower = text.lower()
        
        # Tokenize and boundaries
        for skill in cls.SKILLS_DATABASE:
            # Escape skill for regex processing
            pattern = r'\b' + re.escape(skill) + r'\b'
            if skill in ["c++", "node.js", "ci/cd"]:
                pattern = re.escape(skill)
            
            if re.search(pattern, text_lower):
                extracted_skills.add(skill)
                
        return sorted(list(extracted_skills))

    @classmethod
    def compute_metrics(cls, resume_skills: List[str], jd_skills: List[str]):
        resume_set = set([s.lower() for s in resume_skills])
        jd_set = set([s.lower() for s in jd_skills])
        
        matched = resume_set.intersection(jd_set)
        missing = jd_set.difference(resume_set)
        
        return sorted(list(matched)), sorted(list(missing))