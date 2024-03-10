from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy_file import FileField, ImageField
from sqlalchemy_file.storage import StorageManager
from libcloud.storage.drivers.local import LocalStorageDriver
import os

engine = create_engine('sqlite:///bot_data.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

os.makedirs("files", 0o777, exist_ok=True)

sez_documents = LocalStorageDriver("files").get_container('sez_documents')
sz_files = LocalStorageDriver("files").get_container('sz_files')

StorageManager.add_storage('sez_documents', sez_documents)
StorageManager.add_storage('sz_files', sz_files)


class FirstOrderData(Base):
    __tablename__ = 'first_order_data'
    id = Column(Integer, autoincrement=True, primary_key=True)
    order_type = Column(String)

    fio = Column(String)
    email = Column(String)
    position = Column(String)
    basis = Column(String)
    phone_number = Column(String)
    manager_fio = Column(String)
    project_supervisor_fio = Column(String)

    created_at = Column(DateTime, default=datetime.now())


class SecondOrderData(Base):
    __tablename__ = 'second_order_data'
    id = Column(Integer, autoincrement=True, primary_key=True)
    order_type = Column(String)
    fio = Column(String)
    user_role = Column(String)
    basis = Column(String, nullable=True)
    document = Column(FileField(upload_storage='sez_documents'), nullable=True)
    phone_number = Column(String)
    project_supervisor_fio = Column(String, nullable=True)
    first_date = Column(Date)
    second_date = Column(Date, nullable=True)
    objects = Column(String)

    created_at = Column(DateTime, default=datetime.now())


class ThirdOrderData(Base):
    __tablename__ = 'third_order_data'
    id = Column(Integer, autoincrement=True, primary_key=True)
    order_type = Column(String)
    fio = Column(String)
    email = Column(String)
    position = Column(String)
    basis = Column(String)
    phone_number = Column(String)
    project_supervisor_fio = Column(String)
    document = Column(FileField(upload_storage='sz_files'))

    created_at = Column(DateTime, default=datetime.now())


Base.metadata.create_all(engine)
