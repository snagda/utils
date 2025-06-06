import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from crud_app.backend.main import Base, FieldCreate, RecordCreate, create_field, create_record, list_records
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import crud_app.backend.main as main_module
import pytest

@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    main_module.SessionLocal = TestingSessionLocal
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_create_field_and_record(db):
    field = create_field(FieldCreate(name="title", label="Title", data_type="string"), db)
    assert field.name == "title"

    rec = create_record(RecordCreate(data={"title": "First"}), db)
    assert rec.data["title"] == "First"
