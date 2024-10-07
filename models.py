from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base

# Database models

# Association table for many-to-many relationship
customer_cx_association = Table(
    'customer_cx_association',
    Base.metadata,
    Column('customer_id', Integer, ForeignKey('customers.id')),
    Column('cx_id', Integer, ForeignKey('cx_contacts.id')),
    UniqueConstraint('customer_id', 'cx_id', name='uq_customer_contact')
)

class Customers(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, unique=True, index=True, nullable=False)
    aws_region = Column(String, nullable=True)
    
    instances = relationship('Instances', back_populates='customer', cascade="all, delete-orphan")
    cx_contacts = relationship('CxContacts', secondary=customer_cx_association, back_populates='customers')


class CxContacts(Base):
    __tablename__ = 'cx_contacts'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    customers = relationship('Customers', secondary=customer_cx_association, back_populates='cx_contacts')


class Instances(Base):
    __tablename__ = 'instances'
    
    id = Column(Integer, primary_key=True, index=True)
    instance_name = Column(String, index=True, nullable=False)
    c55_version = Column(String, nullable=False)
    analytics_enabled = Column(Boolean, default=False)
    last_deployment = Column(Date, nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    
    customer = relationship('Customers', back_populates='instances')
    deployments = relationship('Deployments', back_populates='instance')

    def create_version(self, db):
        version = InstanceVersion(
            instance_id=self.id,
            instance_name=self.instance_name,
            c55_version=self.c55_version,
            analytics_enabled=self.analytics_enabled,
            last_deployment=self.last_deployment,
            customer_id=self.customer_id,
            version_date=datetime.now(timezone.utc)
        )


class InstanceVersion(Base):
    __tablename__ = 'instance_versions'

    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, index=True)
    instance_name = Column(String, nullable=False)
    c55_version = Column(String, nullable=False)
    analytics_enabled = Column(Boolean, default=False)
    last_deployment = Column(Date, nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    version_date = Column(DateTime, default=datetime.now(timezone.utc))


class Agents(Base):
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, unique=True, index=True, nullable=False)
    
    deployments = relationship('Deployments', back_populates='agent')


class Deployments(Base):
    __tablename__ = 'deployments'
    
    id = Column(Integer, primary_key=True, index=True)
    deployment_date = Column(Date, nullable=False)
    analytics_enabled = Column(Boolean, nullable=False)
    c55_version = Column(String, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    instance_id = Column(Integer, ForeignKey('instances.id'))
    agent_id = Column(Integer, ForeignKey('agents.id'))
    
    instance = relationship('Instances', back_populates='deployments')
    agent = relationship('Agents', back_populates='deployments')