from fastapi import APIRouter, HTTPException
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from database import collection_leave_predictions_dataset


router = APIRouter()


@router.post("/train_model")
async def train_model():
    data = []
    for attendance in collection_leave_predictions_dataset.find():
        attendanceData = {
            "Previous day is a holiday": attendance["Previous day is a holiday"],
            "Is Holiday": attendance["Is Holiday"],
            "Next day is a holiday": attendance["Next day is a holiday"],
            "Day of the week": attendance["Day of the week"],
            "Company Total Employee Count": attendance["Company Total Employee Count"],
            "Total Employee attendance Count": attendance["Total Employee attendance Count"]
        }
        data.append(attendanceData)
    
    df = pd.DataFrame(data)
    
    X = df[["Previous day is a holiday", "Is Holiday", "Next day is a holiday", "Day of the week", "Company Total Employee Count"]]
    y = df["Total Employee attendance Count"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

    rf_model.fit(X_train, y_train)
    joblib.dump(rf_model, "rfmodel_leave_updating.joblib") 
    return {"message": "Model trained and saved successfully"}



# app = FastAPI()
# router = APIRouter()

# @router.post("/train_model")
# async def train_model():
#     try:
#         # Load the dataset
#         data = []
#         for attendance in collection_leave_predictions_dataset.find():
#             attendanceData = {
#                 "Previous day is a holiday": attendance["Previous day is a holiday"],
#                 "Is Holiday": attendance["Is Holiday"],
#                 "Next day is a holiday": attendance["Next day is a holiday"],
#                 "Day of the week": attendance["Day of the week"],
#                 "Company Total Employee Count": attendance["Company Total Employee Count"],
#                 "Total Employee attendance Count": attendance["Total Employee attendance Count"]
#             }
#             data.append(attendanceData)
        
#         # Create a DataFrame
#         df = pd.DataFrame(data)
        
#         # Split the data into features (X) and target variable (y)
#         X = df[["Previous day is a holiday", "Is Holiday", "Next day is a holiday", "Day of the week", "Company Total Employee Count"]]
#         y = df["Total Employee attendance Count"]
        
#         # Split the data into training and testing sets
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
#         # Initialize the Random Forest Regression model
#         rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
#         # Train the model
#         rf_model.fit(X_train, y_train)
        
#         # Save the trained model
#         joblib.dump(rf_model, "rfmodel_leave_updating.joblib")
        
#         return {"message": "Model trained and saved successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# def schedule_model_training():
#     with app.app_context():
#         app.dependency_overrides = {}  # Reset dependency overrides for the scheduler context
#         app.router.startup()  # Call the startup functions explicitly
#         app.router.include_router(router)  # Re-include the router
#         import asyncio
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(train_model())  # Run the train_model function

# scheduler = BackgroundScheduler()
# scheduler.add_job(schedule_model_training, 'cron', hour=23, minute=0)
# scheduler.start()

# # Include your router
# app.include_router(router)

# # Shutdown the scheduler when the application stops
# @app.on_event("shutdown")
# def shutdown_event():
#     scheduler.shutdown()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
