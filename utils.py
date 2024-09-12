# utils.py
import bcrypt
from jose import jwt
from jose.exceptions import JWTError
from fastapi import Depends
from datetime import datetime, timedelta
from fastapi import HTTPException
from config import SECRET_KEY, ALGORITHM
from database import collection_user,collection_emp_time_rep,collection_working_hours,collection_leave_predictions_dataset
from fastapi.security import OAuth2PasswordBearer
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import PIL.Image
import google.generativeai as genai
from io import BytesIO
import logging
import json
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    encoded_password = password.encode("utf-8")
    hashed = bcrypt.hashpw(encoded_password, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    encoded_plain_password = plain_password.encode("utf-8")
    encoded_hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(encoded_plain_password, encoded_hashed_password)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def authenticate_user(email: str, password: str):
    existing_user = collection_user.find_one({"user_email": email})
    if not existing_user or not verify_password(password, existing_user["user_pw"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return existing_user


async def authenticate_user_exist(email: str):
    existing_user = collection_user.find_one({"user_email": email}, {"_id": 0, "user_email": 1, "user_type": 1})
    if not existing_user:
        raise HTTPException(status_code=401, detail="Incorrect email")
    return existing_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print("Received Token:", token)
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
    except:
        raise credentials_exception
    user = await authenticate_user_exist(email=payload)
    if user is None:
        raise credentials_exception
    return user

def extract_entities_from_text(billtext):
    url = "https://ai-textraction.p.rapidapi.com/textraction"
    payload = {
        "text": billtext
        ,
        "entities": [
            {
                "var_name": "store",
                "type": "string",
                "description": "invoice store"
            },
            {
                "var_name": "invoicenumber",
                "type": "string",
                "description": "invoice reference number"
            },
            {
                "var_name": "date",
                "type": "string",
                "description": "date"
            },
            {
                "var_name": "totalpayableamount",
                "type": "string",
                "description": "total amount in invoice"
            },

        ]
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "998c96c929msh24a280d46e133afp144d06jsna115bef7f7da",
        "X-RapidAPI-Host": "ai-textraction.p.rapidapi.com"
    }

    res = requests.post(url, json=payload, headers=headers).json()
    data = {"storename": res['results']['store'],
            "invoicenumber": res['results']['invoicenumber'],
            "date": res['results']['date'],
            "totalamount": res['results']['totalpayableamount']
            }

    return (data)


async def fetch_and_extract_text(item):
    bill_type = item.get("bill_type")
    image_url = item.get("image_url")

    if not image_url:
        return "No image URL found."

    response = requests.get(image_url)
    img = PIL.Image.open(BytesIO(response.content))

    API_KEY = "AIzaSyDVVsp4j5iewM7hMw_h6m8oWFOIz0Fxsao"
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ]

     
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-pro-vision")

    response = model.generate_content([
        # "this is a bill. i need text about customer name, customer address, total amount, billing details and dates, total amount, date, receipt id, organization name,invoice number. extract that text and can you give output as paragraph.",
        # img
         "this is a bill. i need extract about customer name, customer address, total amount, billing dates, total amount, receipt id, organization name,invoice number.If you can't extract all the datas try to get invoice number,dates and customer name",
        img
    ], safety_settings=safety_settings, stream=True)

    try:
        response.resolve()
        extracted_text = response.text if len(response.text.split("\n")) > 1 else "No text extracted."
    except Exception as e:
        extracted_text = "Error during text extraction. Please try it Manually."

    return extracted_text

async def extract_text_from_images(images):
    results = []
    for image_data in images:
        extracted_text = await fetch_and_extract_text(image_data)
        results.append({"bill_type": image_data.get("bill_type"), "extracted_text": extracted_text})

    return results

def convert_object_id(doc):
    doc['_id'] = str(doc['_id'])
    return doc

def is_holiday(date):
    future_holidays = {
        "0115": "Tamil Thai Pongal Day",
        "0125": "Duruthu Full Moon Poya Day",
        "0204": "Independence Day",
        "0223": "Navam Full Moon Poya Day",
        "0308": "Mahasivarathri Day",
        "0324": "Medin Full Moon Poya Day",
        "0329": "Good Friday",
        "0411": "Id-Ul-Fitr (Ramazan Festival Day)",
        "0412": "Day prior to Sinhala & Tamil New Year Day",
        "0413": "Sinhala & Tamil New Year Day",
        "0423": "Bak Full Moon Poya Day",
        "0501": "May Day (International Workers Day)",
        "0523": "Vesak Full Moon Poya Day",
        "0524": "Day following Vesak Full Moon Poya Day",
        "0617": "Id-Ul-Alha (Hadji Festival Day)",
        "0621": "Poson Full Moon Poya Day",
        "0720": "Esala Full Moon Poya Day",
        "0819": "Nikini Full Moon Poya Day",
        "0916": "Milad-Un-Nabi (Holy Prophet's Birthday)",
        "0917": "Binara Full Moon Poya Day",
        "1017": "Vap Full Moon Poya Day",
        "1031": "Deepavali Festival Day",
        "1115": "Ill Full Moon Poya Day",
        "1214": "Unduvap Full Moon Poya Day",
        "1225": "Christmas Day"
    }

    if date in future_holidays.keys():
        return 1
    else:
        return 0

def create_future_data(date):
    current_year = pd.Timestamp.now().year

    full_date_str = f"{current_year}-{date[:2]}-{date[2:]}"

    future_date_datetime = pd.to_datetime(full_date_str, format='%Y-%m-%d', errors='raise')
    print("Input Date:", future_date_datetime)

    next_day = future_date_datetime + pd.DateOffset(days=1)
    previous_day = future_date_datetime - pd.DateOffset(days=1)
    print("Next Day:", next_day)
    print("Previous Day:", previous_day)

    next_day_holiday = is_holiday(next_day.strftime("%m%d")) or next_day.dayofweek == 6
    previous_day_holiday = is_holiday(previous_day.strftime("%m%d")) or previous_day.dayofweek == 6
    print("Next Day Holiday:", next_day_holiday)
    print("Previous Day Holiday:", previous_day_holiday)

    is_holiday_flag = 1 if is_holiday(date) or future_date_datetime.dayofweek == 6 else 0
    print("Is Holiday Flag:", is_holiday_flag)

    day_of_week = future_date_datetime.dayofweek
    print("Day of the Week:", day_of_week)

    company_total_employee_count = 200

    if previous_day.dayofweek == 6 and next_day_holiday:
        previous_day_holiday = 1

    future_data = pd.DataFrame({
        "Previous day is a holiday": [previous_day_holiday],
        "Is Holiday": [is_holiday_flag],
        "Next day is a holiday": [next_day_holiday],
        "Day of the week": [day_of_week],
        "Company Total Employee Count": [company_total_employee_count],
    })

    return future_data  
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_leave_prediction_data():
    today = datetime.now().strftime('%Y-%m-%d')
    date_mmdd = datetime.now().strftime('%m%d')
    attendance = collection_emp_time_rep.find({"date": today, "totalWorkMilliSeconds": {"$gt": 0}})
    total_attendance = attendance.count()
    print("Total Attendance:", total_attendance)

    future_data = create_future_data(date_mmdd)

    leave_prediction_data = {
        "Date": int(date_mmdd),
        "Total Employee attendance Count": total_attendance,
        "Previous day is a holiday": future_data["Previous day is a holiday"].values[0],
        "Is Holiday": future_data["Is Holiday"].values[0],
        "Next day is a holiday": future_data["Next day is a holiday"].values[0],
        "Day of the week": future_data["Day of the week"].values[0],
        "Company Total Employee Count": future_data["Company Total Employee Count"].values[0]
    }
    collection_leave_predictions_dataset.insert_one(leave_prediction_data)
    logger.info(f"Updated leave prediction data for {today}.")


def schedule_daily_collection():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_leave_prediction_data, 'cron', hour=21, minute=0)
    scheduler.start()
    logger.info("Scheduled daily collection at 21:00.")

def update_daily_ot():
    today=datetime.now().strftime('%Y-%m-%d')
    emp_records=collection_emp_time_rep.find({"date":today})
    total_working_time={}
    for emp in emp_records:
        emp_email=emp.get("user_email")
        working_time= emp.get("totalWorkMilliSeconds")
        if emp_email in total_working_time:
            total_working_time[emp_email] += working_time
        else:
            total_working_time[emp_email] = working_time
    
    ot_hours={}

    for emp_email,tot_working in total_working_time.items():
            if tot_working>=28800000:
                ot_hours[emp_email]=(tot_working-28800000)/3600000
            else:
                ot_hours[emp_email]=0

    for emp_email,ot in ot_hours.items():
        collection_working_hours.update_one({"u_email":emp_email},{"$inc":{"totalOT":ot}})

    
    logger.info(f"Updated leave prediction data for {today}.")

def schedule_daily_ot_update():
    schedular=BackgroundScheduler()
    schedular.add_job(update_daily_ot,'cron',hour=23,minute=59)
    schedular.start()
    logger.info("Scheduled daily oy update at 23.59")

