import json
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .config import APP_NAME, FRONTEND_ORIGINS
from .database import Base, engine, get_db
from .models import User, Recommendation
from .schemas import RegisterRequest, LoginRequest, HomeBudgetInput, PartyBudgetInput, JewelryBudgetInput, ChatRequest
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .ai import generate_planner, chat
from .recommendations import fallback_home, fallback_party, fallback_jewelry

Base.metadata.create_all(bind=engine)
app = FastAPI(title=APP_NAME, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=FRONTEND_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
BASE_DIR=Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")

@app.get("/", include_in_schema=False)
def root(): return FileResponse(BASE_DIR/"static"/"index.html")
@app.get("/{page}.html", include_in_schema=False)
def pages(page: str):
    allowed={"login","register","dashboard","planner","history","detail"}
    if page not in allowed: raise HTTPException(404,"Page not found")
    return FileResponse(BASE_DIR/"static"/f"{page}.html")

@app.get("/api/health")
def health(): return {"status":"ok","app":APP_NAME}

@app.post("/api/auth/register")
def register(data:RegisterRequest, db:Session=Depends(get_db)):
    if db.query(User).filter((User.username==data.username)|(User.email==data.email)).first():
        raise HTTPException(409,"Username or email already exists")
    user=User(username=data.username.strip(), email=data.email.lower(), full_name=data.full_name, password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"message":"Account created","user":{"id":user.id,"username":user.username,"email":user.email,"full_name":user.full_name}}

@app.post("/api/auth/login")
def login(data:LoginRequest, db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==data.username.strip()).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Invalid username or password")
    token=create_access_token(user.id,user.username)
    return {"access_token":token,"token_type":"bearer","user":{"id":user.id,"username":user.username,"email":user.email,"full_name":user.full_name}}

@app.get("/api/me")
def me(user:User=Depends(get_current_user)):
    return {"id":user.id,"username":user.username,"email":user.email,"full_name":user.full_name}

def save_recommendation(db,user,kind,payload,result):
    title={"home":"Home Budget Plan","party":"Party Budget Plan","jewelry":"Jewelry Budget Plan"}[kind]
    item=Recommendation(user_id=user.id,recommendation_type=kind,title=title,input_summary=json.dumps(payload),full_result=json.dumps(result))
    db.add(item); db.commit(); db.refresh(item)
    return item

def run_plan(kind,data,user,db):
    payload=data.model_dump()
    fn={"home":fallback_home,"party":fallback_party,"jewelry":fallback_jewelry}[kind]
    result=generate_planner(kind,payload,fn)
    item=save_recommendation(db,user,kind,payload,result)
    result["recommendation_id"]=item.id
    return result

@app.post("/api/planner/home")
def home(data:HomeBudgetInput,user:User=Depends(get_current_user),db:Session=Depends(get_db)): return run_plan("home",data,user,db)
@app.post("/api/planner/party")
def party(data:PartyBudgetInput,user:User=Depends(get_current_user),db:Session=Depends(get_db)): return run_plan("party",data,user,db)
@app.post("/api/planner/jewelry")
def jewelry(data:JewelryBudgetInput,user:User=Depends(get_current_user),db:Session=Depends(get_db)): return run_plan("jewelry",data,user,db)

@app.get("/api/history")
def history(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.query(Recommendation).filter(Recommendation.user_id==user.id).order_by(Recommendation.created_at.desc()).all()
    return {"history":[{"id":r.id,"type":r.recommendation_type,"title":r.title,"input_summary":json.loads(r.input_summary),"created_at":r.created_at.isoformat()} for r in rows]}

@app.get("/api/recommendation-details/{recommendation_id}")
def recommendation_details(recommendation_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    r=db.query(Recommendation).filter(Recommendation.id==recommendation_id,Recommendation.user_id==user.id).first()
    if not r: raise HTTPException(404,"Recommendation not found")
    return {"id":r.id,"type":r.recommendation_type,"title":r.title,"input":json.loads(r.input_summary),"full_result":json.loads(r.full_result),"created_at":r.created_at.isoformat()}

@app.get("/api/dashboard")
def dashboard(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.query(Recommendation).filter(Recommendation.user_id==user.id).order_by(Recommendation.created_at.desc()).all()
    return {"user":{"username":user.username,"full_name":user.full_name},"recommendation_count":len(rows),"recent":[{"id":r.id,"type":r.recommendation_type,"title":r.title,"created_at":r.created_at.isoformat()} for r in rows[:5]]}

@app.post("/api/ai/chat")
def ai_chat(data:ChatRequest,user:User=Depends(get_current_user)): return {"reply":chat(data.message)}
