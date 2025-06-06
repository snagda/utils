from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime

DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FieldCatalog(Base):
    __tablename__ = "field_catalog"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    label = Column(String)
    data_type = Column(String)
    description = Column(String, nullable=True)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, index=True)
    operation = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = Column(String)
    before = Column(JSON, nullable=True)
    after = Column(JSON, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dynamic CRUD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class FieldCreate(BaseModel):
    name: str
    label: str
    data_type: str
    description: str | None = None
    created_by: str = "system"

class FieldOut(FieldCreate):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class RecordCreate(BaseModel):
    data: dict
    user: str = "system"

class RecordOut(BaseModel):
    id: int
    data: dict
    class Config:
        orm_mode = True

@app.post("/fields", response_model=FieldOut)
def create_field(field: FieldCreate, db: Session = Depends(get_db)):
    db_field = FieldCatalog(**field.dict())
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field

@app.get("/fields", response_model=list[FieldOut])
def list_fields(db: Session = Depends(get_db)):
    return db.query(FieldCatalog).all()

@app.post("/records", response_model=RecordOut)
def create_record(rec: RecordCreate, db: Session = Depends(get_db)):
    db_rec = Record(data=rec.data)
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    log = AuditLog(record_id=db_rec.id, operation="create", user=rec.user, after=rec.data)
    db.add(log)
    db.commit()
    return db_rec

@app.get("/records", response_model=list[RecordOut])
def list_records(db: Session = Depends(get_db)):
    return db.query(Record).all()

@app.get("/records/{record_id}", response_model=RecordOut)
def get_record(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(Record).filter(Record.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    return rec

@app.put("/records/{record_id}", response_model=RecordOut)
def update_record(record_id: int, rec: RecordCreate, db: Session = Depends(get_db)):
    db_rec = db.query(Record).filter(Record.id == record_id).first()
    if not db_rec:
        raise HTTPException(status_code=404, detail="Record not found")
    before = db_rec.data
    db_rec.data = rec.data
    db.commit()
    db.refresh(db_rec)
    log = AuditLog(record_id=record_id, operation="update", user=rec.user, before=before, after=rec.data)
    db.add(log)
    db.commit()
    return db_rec

@app.delete("/records/{record_id}")
def delete_record(record_id: int, user: str = "system", db: Session = Depends(get_db)):
    db_rec = db.query(Record).filter(Record.id == record_id).first()
    if not db_rec:
        raise HTTPException(status_code=404, detail="Record not found")
    before = db_rec.data
    db.delete(db_rec)
    db.commit()
    log = AuditLog(record_id=record_id, operation="delete", user=user, before=before)
    db.add(log)
    db.commit()
    return {"ok": True}

