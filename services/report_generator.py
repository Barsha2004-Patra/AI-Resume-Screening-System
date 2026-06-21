import os
from datetime import datetime
from typing import List, Dict, Any

class ReportGenerator:
    @staticmethod
    def generate_txt_report(
        filename: str,
        candidate_name: str,
        job_title: str,
        match_score: float,
        matched_skills: List[str],
        missing_skills: List[str]
    ) -> str:
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        safe_name = "".join([c for c in candidate_name if c.isalpha() or c.isspace()]).strip().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"Report_{safe_name}_{timestamp}.txt"
        report_path = os.path.join(report_dir, report_filename)
        
        content = f"""==================================================
AI RESUME SCREENING REPORT
==================================================
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Candidate Name: {candidate_name}
Source File: {filename}
Target Job Role: {job_title}
--------------------------------------------------
OVERALL MATCH SCORE: {match_score}%
--------------------------------------------------

MATCHED SKILLS:
{', '.join(matched_skills) if matched_skills else 'None'}

MISSING REQUISITE SKILLS:
{', '.join(missing_skills) if missing_skills else 'None'}

--------------------------------------------------
Status Recommendation:
"""
        if match_score >= 75:
            content += "STRONG MATCH - Proceed immediately to technical review screening."
        elif match_score >= 45:
            content += "POTENTIAL MATCH - Consider for secondary phone screening review."
        else:
            content += "LOW MATCH - Archive profile for future opportunities."
            
        content += "\n==================================================\n"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return report_path