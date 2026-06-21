import os
import logging
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import init_db, get_db
from models import JobDescription, ResumeResult
from services.resume_parser import ResumeParser
from services.skill_extractor import SkillExtractor
from services.scorer import ResumeScorer
from services.report_generator import ReportGenerator

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize engine & directories
init_db()

app = FastAPI(title="Enterprise AI Resume Screening Pipeline Core", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/api/screen")
async def screen_resumes(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resumes: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    if not resumes or len(resumes) == 0:
        raise HTTPException(status_code=400, detail="No active resume data models parsed.")
        
    try:
        # Save Job parameters
        jd_skills_all = SkillExtractor.extract_skills(job_description)
        db_jd = JobDescription(
            title=job_title,
            content=job_description,
            skills=",".join(jd_skills_all)
        )
        db.add(db_jd)
        db.commit()
        db.refresh(db_jd)
        
        evaluation_results = []
        
        for resume_file in resumes:
            # Persistent storage allocation
            file_extension = os.path.splitext(resume_file.filename)[1]
            if file_extension.lower() != '.pdf':
                logger.warning(f"File validation bypass prevented: {resume_file.filename}")
                continue
                
            temp_path = os.path.join("uploads", f"temp_{resume_file.filename}")
            with open(temp_path, "wb") as buffer:
                content = await resume_file.read()
                buffer.write(content)
                
            try:
                # Text transformation & processing matrix
                extracted_text = ResumeParser.extract_text(temp_path)
                candidate_name = ResumeParser.extract_candidate_name(extracted_text, resume_file.filename)
                
                resume_skills = SkillExtractor.extract_skills(extracted_text)
                matched, missing = SkillExtractor.compute_metrics(resume_skills, jd_skills_all)
                
                match_score = ResumeScorer.calculate_similarity(
                    resume_text=extracted_text, 
                    jd_text=job_description,
                    matched_skills=matched,
                    total_jd_skills=jd_skills_all
                )
                
                # File artifact emission
                report_file_path = ReportGenerator.generate_txt_report(
                    filename=resume_file.filename,
                    candidate_name=candidate_name,
                    job_title=job_title,
                    match_score=match_score,
                    matched_skills=matched,
                    missing_skills=missing
                )
                
                db_result = ResumeResult(
                    job_description_id=db_jd.id,
                    filename=resume_file.filename,
                    candidate_name=candidate_name,
                    match_score=match_score,
                    matched_skills=",".join(matched),
                    missing_skills=",".join(missing),
                    report_path=report_file_path
                )
                db.add(db_result)
                db.commit()
                db.refresh(db_result)
                
                evaluation_results.append({
                    "result_id": db_result.id,
                    "filename": db_result.filename,
                    "candidate_name": db_result.candidate_name,
                    "match_score": db_result.match_score,
                    "matched_skills": matched,
                    "missing_skills": missing
                })
                
            except Exception as entry_error:
                logger.error(f"Failed handling execution branch for {resume_file.filename}: {str(entry_error)}")
                continue
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        ranked_results = ResumeScorer.rank_resumes(evaluation_results)
        return {"status": "success", "results": ranked_results}
        
    except Exception as global_error:
        logger.critical(f"Pipeline Execution Failure Sequence Exception: {str(global_error)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(global_error))

@app.get("/api/report/{result_id}")
def download_report(result_id: int, db: Session = Depends(get_db)):
    result = db.query(ResumeResult).filter(ResumeResult.id == result_id).first()
    if not result or not result.report_path or not os.path.exists(result.report_path):
        raise HTTPException(status_code=404, detail="Requested analytics asset report generation record variant missing.")
    return FileResponse(path=result.report_path, filename=os.path.basename(result.report_path), media_type='text/plain')