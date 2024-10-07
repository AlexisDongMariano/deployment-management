from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date

# Pydantic models


# Deployments
class DeploymentBase(BaseModel):
    deployment_date: date
    c55_version: str
    analytics_enabled: bool
    instance_id: int
    agent_id: int

class DeploymentCreate(DeploymentBase):
    pass

class Deployment(DeploymentBase):
    id: int

    class Config:
        orm_mode = True


# Instance
class InstanceBase(BaseModel):
    instance_name: str
    c55_version: str
    analytics_enabled: bool
    last_deployment: Optional[date] = None

class InstanceCreate(InstanceBase):
    pass

class Instance(InstanceBase):
    id: int
    deployments: List[Deployment] = []

    class Config:
        orm_mode = True


# CxContact
class CxContactBase(BaseModel):
    username: str
    email: str

class CxContactCreate(CxContactBase):
    pass

class CxContact(CxContactBase):
    id: int

    class Config:
        orm_mode = True


# Customer
class CustomerBase(BaseModel):
    customer_name: str
    aws_region: Optional[str] = None

class CustomerCreate(CustomerBase):
    cx_contact_ids: List[int] = []   # List of CxContact IDs to associate with the customer

class Customer(CustomerBase):
    id: int
    cx_contacts: List[CxContact] = []
    instances: List[Instance] = []

    class Config:
        orm_mode = True


# Agent
class AgentBase(BaseModel):
    agent_name: str

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: int
    deployments: List[Deployment] = []

    class Config:
        orm_mode = True


