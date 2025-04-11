from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import csv
from database import SessionLocal
from models import Department, Job, Employee
import os
from datetime import datetime

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the API for DB migration!"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/")
async def upload_csv(db: Session = Depends(get_db)):
    departments_file = r"C:\PROYECTOS\globant\departments.csv"
    jobs_file = r"C:\PROYECTOS\globant\jobs.csv"
    employees_file = r"C:\PROYECTOS\globant\hired_employees.csv"
    
    if not all(os.path.exists(file) for file in [departments_file, jobs_file, employees_file]):
        return {"error": "One or more CSV files are missing from the specified location."}

    departments = set()
    with open(departments_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            departments.add(row[1]) 

    departments_to_insert = [Department(name=dept) for dept in departments]
    db.bulk_save_objects(departments_to_insert)

    jobs = set()
    with open(jobs_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            jobs.add(row[1])  
    
    jobs_to_insert = [Job(title=job) for job in jobs]
    db.bulk_save_objects(jobs_to_insert)
    
    db.commit() 

    employees_to_insert = []
    with open(employees_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            employee_name = row[1]
            hired_at = row[2] 
            department_id = row[3]  
            job_id = row[4] 

            if hired_at and job_id and department_id:  
                try:
                    department_id = int(department_id)
                    job_id = int(job_id)
                    employees_to_insert.append(Employee(
                        name=employee_name,
                        hired_at=hired_at,
                        department_id=department_id,
                        job_id=job_id
                    ))
                except ValueError:
                    continue  

    db.bulk_save_objects(employees_to_insert)
    db.commit() 

    num_departments = len(departments_to_insert)
    num_jobs = len(jobs_to_insert)
    num_employees = len(employees_to_insert)

    return {
        "message": f"Successfully uploaded {num_departments} departments, {num_jobs} jobs, and {num_employees} employees."
    }
