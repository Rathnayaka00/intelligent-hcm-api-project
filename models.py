
# models.py
from pydantic import BaseModel,Field
from typing import Optional
from fastapi import UploadFile, File
from datetime import datetime


class User_login(BaseModel):
    type: str
    email: str
    password: str
    
class TokenRefresh(BaseModel):
    refresh_token: str

class User(BaseModel):
    fName:str
    lName:str
    contact:str
    user_email:str
    address:str
    user_pw:str
    user_type:str
    user_role:str 
    manager: Optional[str] = None

class add_vacancy(BaseModel):
    possition: str
    pre_requisits:str
    responsibilities: str
    job_type: str
    work_mode: str
    num_of_vacancies: int
    more_details: str

class UpdateVacancyStatus(BaseModel):
    new_status: str

class OT_Work_Hours(BaseModel):
    oTHourlyRate:float
    totalOT:float
    fixedOT:int
    totalOTPay:float 
    user_email:str

class Bills(BaseModel):
    amount:str
    category:str
    storename:str
    Date:str
    status:str
    submitdate:str
    invoice_number:str

#new basemodel for Employee Leaves
class EmployeeLeave(BaseModel):
    user_email:str
    name: str
    start_date: datetime
    end_date: datetime
    leave_type: str
    leave_status:str="pending"

class Leaves(BaseModel):
    l_id:str
    totla:float
    status:bool
    remaining:int
    u_id:str

class Candidate(BaseModel):
    #changed the order
    c_id:str
    email:str
    name:str
    cv:str
    score:float #addded new
    vacancy_id:str

class UpdateCandidateStatus(BaseModel):
    new_status:str


class Parsed_Candidates(BaseModel):
    candidate_id:str
    id:str
    qualifications:str
    score:str
    reason:str

class Interview(BaseModel):
    i_id:str
    c_id:str
    date:str
    time:str
    venue:str
    interviewer_id:str
    confirmed_date:str
    result:str #pending or confrim or selected or rejected
    #candidate_id:str
    

class PredictionRequest(BaseModel):
    date: str

class PredictionResponse(BaseModel):
    date: str
    predicted_attendance: int

class EmpSubmitForm(BaseModel):
    fullName:str
    eMail:str
    contact:str
    dob:str

class EmpTimeRep(BaseModel):
    date:str
    project_type:str
    totalWorkMilliSeconds:int

class FileModel(BaseModel):  
    image_url: str

      
class LeaveRequest(BaseModel):
    leaveType: str
    startDate: str
    dayCount:  str
    submitdate:str
    submitdatetime:str

class Update_leave_request(BaseModel):
    new_status: str

class EmployeeLeaveCount(BaseModel):
    submitdate: str
    sickLeaveCount: str
    casualLeaveCount: str
    annualLeaveCount:  str

class ManagerLeaveCount(BaseModel):
    submitdate:str
    sickLeaveCount: str
    casualLeaveCount: str
    annualLeaveCount:  str

class UserMessage(BaseModel):
    message: str

class TimeReportQuery(BaseModel):
    date: str

class UserResponse(BaseModel):
    message: str
    user_id: str

class JobVacancy(BaseModel):
    vacancy_id: str
    job_title: str
    job_type: str
    work_mode: str
    pdf_id: str


class JobApplicatons(BaseModel):
    c_id: str
    name: str
    email: str
    contact_number: str
    cv: str
    job_title: str
    job_type: str
    work_mode: str
    score:float
    status:str



class ContactUs(BaseModel):
    user_email: str
    user_contact_number: str
    feedback: str


class ContactUsResponse(BaseModel):
    contact_id: str
    user_email: str
    user_contact_number: str
    feedback: str
    status: str

class Manager(BaseModel):
    user_email:str
    fName:str
