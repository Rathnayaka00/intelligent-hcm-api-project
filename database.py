# database.py
from pymongo import MongoClient
from gridfs import GridFS

client = MongoClient('mongodb+srv://oshen:oshen@cluster0.h2my8yk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

database = client.HCM

collection_user = database["user"] 
collection_user_login = database["users"]
# collection_add_vacancy =database["AddVacancy"]
collection_leave_predictions = database["LeavePredictions"]
collection_bills = database["bills"]
collection_bill_upload = database["BillUpload"] 
collection_new_candidate = database["new_candidates"]
collection_emp_vac_submit=database["empVacSubmit"]
collection_emp_time_rep=database["empTimeReport"]
collection_add_leave_request = database["LeaveRequest"]
collection_add_employee_leave_count = database["EmployeeLeaveCount"]
collection_add_manager_leave_count = database["ManagerLeaveCount"]
collection_candidate_pdf = database["candidate_pdf"]
collection_leaves=database["leaves"]
collection_remaining_leaves=database["remaining_leaves"]
collection_working_hours=database["working_hours"]
collection_interviews=database["interviews"]
collection_contact_us=database["ContactUs"]
collection_leave_predictions_dataset = database["Leave_prediction_dataset"]
collection_job_vacancies = database["JobVacancies"]
collection_add_vacancy = database['AddVacancy']
collection_job_applications = database["JobApplications"]

fs = GridFS(database,collection="candidate_pdfs")


