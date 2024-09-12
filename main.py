# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import routes
from fastapi.security import OAuth2PasswordBearer
from utils import schedule_daily_ot_update,schedule_daily_collection

app = FastAPI()

origins = [
    "https://localhost:3000",  
    "http://localhost:3000",   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  
    allow_headers=["*"],  
)

app.include_router(routes.router)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# @app.on_event("startup")
# def startup_event():
#     schedule_daily_collection()

@app.on_event("startup")
def startup_event():
    schedule_daily_ot_update()



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
