from sqlalchemy import Column, Integer, String, DateTime, TIMESTAMP, ForeignKey, Table, Text, Date
from sqlalchemy.orm import relationship
from db.database import Base
from sqlalchemy.schema import PrimaryKeyConstraint
from datetime import datetime

# 中間テーブルの定義
user_specialties = Table(
    'user_specialties',
    Base.metadata,
    Column('user_id', String(50), ForeignKey('user_master.user_id'), primary_key=True),
    Column('specialty', String(50), ForeignKey('specialty.specialty'), primary_key=True)
)

user_orientations = Table(
    'user_orientations',
    Base.metadata,
    Column('user_id', String(50), ForeignKey('user_master.user_id'), primary_key=True),
    Column('orientation', String(50), ForeignKey('orientation.orientation'), primary_key=True)
)

class UserMaster(Base):
    __tablename__ = "user_master"

    user_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    avatar_url = Column(String(255))
    core_time = Column(String(50))

    specialties = relationship("Specialty", secondary=user_specialties, back_populates="users")
    orientations = relationship("Orientation", secondary=user_orientations, back_populates="users")
    team_members = relationship("TeamMember", back_populates="user")

class Specialty(Base):
    __tablename__ = "specialty"

    specialty = Column(String(50), primary_key=True)
    users = relationship("UserMaster", secondary=user_specialties, back_populates="specialties")

class Orientation(Base):
    __tablename__ = "orientation"

    orientation = Column(String(50), primary_key=True)
    users = relationship("UserMaster", secondary=user_orientations, back_populates="orientations")

class StatusTable(Base):
    __tablename__ = "status_table"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey('user_master.user_id'), nullable=False)
    biz = Column(Integer, nullable=False)
    design = Column(Integer, nullable=False)
    tech = Column(Integer, nullable=False)

class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    members = relationship("TeamMember", back_populates="team")

class TeamMember(Base):
    __tablename__ = 'team_members'
    
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    role = Column(String(10), nullable=False)
    user_id = Column(String(50), ForeignKey('user_master.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        PrimaryKeyConstraint('team_id', 'role'),
    )
    
    user = relationship("UserMaster", back_populates="team_members")
    team = relationship("Team", back_populates="members")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)
    correct_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)