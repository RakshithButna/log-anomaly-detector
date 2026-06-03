# Data models
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, nullable=False)       # which service sent the log
    level = Column(String, nullable=False)          # INFO, ERROR, WARNING
    message = Column(String, nullable=False)        # the actual log message
    latency_ms = Column(Float, nullable=True)       # response time in ms
    timestamp = Column(DateTime, default=datetime.utcnow)

class AnomalyRecord(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, nullable=False)        # which service triggered it
    anomaly_type = Column(String, nullable=False)   # HIGH_LATENCY or HIGH_ERROR_RATE
    detail = Column(String, nullable=False)         # what exactly happened
    latency_ms = Column(Float, nullable=True)       # latency at time of anomaly
    resolved = Column(Boolean, default=False)       # has it been fixed?
    timestamp = Column(DateTime, default=datetime.utcnow)
