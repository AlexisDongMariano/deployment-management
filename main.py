from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request
from pydantic import BaseModel
from typing import Annotated, Optional
from sqlalchemy.orm import Session

import crud, schemas
from models import Base, Customers, Instances, Agents, Deployments, InstanceVersion, CxContacts
from database import SessionLocal, engine

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# PAGE RENDER
@app.get("/")
def test(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get('/customer-page')
async def render_customer_page(request: Request, db: db_dependency):
    customers = crud.get_customers(db)
    return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})


@app.get('/customers/edit-customer-page/{customer_id}')
async def render_edit_customer_page(request: Request, customer_id: int, db: db_dependency):
    customer = check_customer(db=db, customer_id=customer_id)
    all_cx = db.query(CxContacts).all()
    return templates.TemplateResponse("edit-customer.html", 
                                      {"request": request, "customer": customer, "customer_id": customer_id, "all_cx": all_cx})




######################################################################
# FUNCTIONS
def check_customer(db: Session, 
                   customer_id: Optional[int] = None, customer_name: Optional[int] = None,
                   new_customer: Optional[bool] = None):
    if customer_id and not new_customer:
        db_customer = db.query(Customers).filter(Customers.id == customer_id).first()
        if customer_name:
            db_customer_by_name = db.query(Customers).filter(Customers.customer_name == customer_name).first()
    else:
        db_customer = db.query(Customers).filter(Customers.customer_name == customer_name).first()

    # new customer check - creating
    if new_customer and db_customer:
        raise HTTPException(status_code=404, detail='Customer already exists.')
    # existing customer check - updating
    if not new_customer:
        if not db_customer:
            raise HTTPException(status_code=404, detail='Customer not found.')
        if customer_name and db_customer.id != db_customer_by_name.id:
            raise HTTPException(status_code=404, detail=f'Customer "{customer_name}" already exists.')
        
    
    return db_customer


def check_cx(db: Session, cx_id: Optional[int] = None, cx_username: Optional[str] = None,
             cx_email: Optional[str] = None, new_cx: Optional[bool] = None):
    if cx_id:
        db_cx = db.query(CxContacts).filter(CxContacts.id == cx_id).first()
    if cx_username:
        db_cx = db.query(CxContacts).filter(CxContacts.username == cx_username).first()

    db_cx_email = db.query(CxContacts).filter(CxContacts.email == cx_email).first()
        
    # new cx check - creating
    if new_cx:
        if db_cx:
            raise HTTPException(status_code=400, detail=f"CX {cx_username} already registered.")
        if db_cx_email:
            raise HTTPException(status_code=400, detail=f"CX email {db_cx_email.email} already registered.")

    # updating cx check
    if not new_cx:
        if not db_cx:
            raise HTTPException(status_code=404, detail=f'CX with id {cx_id} not found')
        if db_cx_email and db_cx.id != db_cx_email.id:
                raise HTTPException(status_code=400, detail=f"CX email {db_cx.email} already registered.")

    return db_cx


def check_instance(db: Session, customer_id: int, 
                   instance_name: str, 
                   new_instance: Optional[bool] = None):
    
    db_instance = db.query(Instances).filter(
        Instances.customer_id == customer_id,
        Instances.instance_name == instance_name
    ).first()

    if not db_instance and not new_instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return db_instance
######################################################################   


@app.get("/customers/", response_model=list[schemas.Customer])
def read_customers(db: db_dependency):
    return crud.get_customers(db)


@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: db_dependency):
    check_customer(db=db, customer_name=customer.customer_name, new_customer=True)

    # adding cx contacts to a customer
    cx_contact_list = set()
    for cx_id in customer.cx_contact_ids:
        db_cx = check_cx(db=db, cx_id=cx_id)
        cx_contact_list.add(db_cx)
        
    return crud.create_customer(db=db, customer=customer, cx_contact_list=cx_contact_list)


@app.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(customer: schemas.CustomerCreate, customer_id: int, db: db_dependency):
    db_customer = check_customer(db=db, customer_id=customer_id, customer_name=customer.customer_name)

    # adding cx contacts to a customer
    cx_contact_list = set()
    if customer.cx_contact_ids:
        for cx_id in customer.cx_contact_ids:
            db_cx = check_cx(db=db, cx_id=cx_id)
            cx_contact_list.add(db_cx)
    else:
        cx_contact_list = set()

    return crud.update_customer(db=db, customer=customer, update_customer=db_customer, 
                                cx_contact_list=cx_contact_list)



# @app.post("/customers/{customer_id}", response_model=schemas.Customer)
# def update_customer(customer_id: int, customer_name: str = Form(...), aws_region: Optional[str] = Form(None), cx_contacts: str = Form(...), _method: str = Form(None), db: Session = Depends(get_db)):
#     if _method != "PUT":
#         raise HTTPException(status_code=405, detail="Method Not Allowed")

#     db_customer = check_customer(db=db, customer_id=customer_id)
    
#     db_customer.customer_name = customer_name
#     db_customer.aws_region = aws_region
    
#     contact_ids = [int(id.strip()) for id in cx_contacts.split(',')]
#     db_customer.cx_contacts = []
#     for contact_id in contact_ids:
#         db_contact = db.query(models.CxContacts).filter(models.CxContacts.id == contact_id).first()
#         if not db_contact:
#             raise HTTPException(status_code=404, detail=f"Contact with id {contact_id} not found")
#         db_customer.cx_contacts.append(db_contact)
    
#     try:
#         db.commit()
#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Duplicate customer-contact association")
    
#     db.refresh(db_customer)
    
#     return db_customer

    
@app.delete("/customers/{customer_id}", response_model=schemas.Customer)
def delete_customer(customer_id: int, db: db_dependency):
    db_customer = check_customer(db=db, customer_id=customer_id)
    print(f'DELETING CUSTOMER, db_customer: {db_customer.customer_name}')
    return crud.delete_customerx(db=db, db_customer=db_customer)


# CX CONTACTS
@app.get("/cx_contacts/", response_model=list[schemas.CxContact])
def read_cx_contacts(db: db_dependency):
    return crud.get_cx_contacts(db)


@app.post("/cx_contacts/", response_model=schemas.CxContact)
def create_cx_contact(cx: schemas.CxContactCreate, db: db_dependency):
    check_cx(db=db, cx_username=cx.username, cx_email=cx.email, new_cx=True)
    return crud.create_cx_contact(db=db, cx=cx)


@app.put("/cx_contacts/{cx_id}")
def update_cx_contact(cx: schemas.CxContactCreate, cx_id: int, db: db_dependency):
    update_cx = check_cx(db=db, cx_id=cx_id, cx_email=cx.email)

    cx_by_username = db.query(CxContacts).filter(CxContacts.username == cx.username).first()
    # check if username is taken by another cx
    if not cx_by_username:
        return crud.update_cx_contact(db=db, update_cx=update_cx, cx=cx)
    if update_cx.id != cx_by_username.id:
        raise HTTPException(status_code=400, detail=f"CX username {cx.username} is already registered.")

    return crud.update_cx_contact(db=db, update_cx=update_cx, cx=cx)


# INSTANCE
@app.get("/customers/{customer_id}/instances/", response_model=list[schemas.Instance])
def get_c55_instances(customer_id: int, db: db_dependency):
    db_customer = check_customer(db=db, customer_id=customer_id)
    return crud.get_c55_instances(db, db_customer)


@app.post("/customers/{customer_id}/instances/", response_model=schemas.Instance)
def create_c55_instance(customer_id: int, instance: schemas.InstanceCreate, db:db_dependency):
    db_customer = check_customer(db=db, customer_id=customer_id)
    db_instance = check_instance(db=db, customer_id=db_customer.id, 
                                 instance_name=instance.instance_name, 
                                 new_instance=True)

    if db_instance:
        raise HTTPException(status_code=422, detail='Instance already exists.')
    
    return crud.create_c55_instance(db=db, customer_id=customer_id, instance=instance)


@app.put("/customers/{customer_id}/instances/{instance_name}", response_model=schemas.Instance)
def update_c55_instance(customer_id: int, instance_name: str, instance: schemas.InstanceCreate, db: db_dependency):
    db_customer = check_customer(db=db, customer_id=customer_id)
    db_instance = check_instance(db=db, customer_id=db_customer.id, instance_name=instance_name)

    # Create a new version of the instance before updating
    # db_instance.create_version(db)
    updated_instance = crud.update_c55_instance(db=db, instance=instance, update_instance=db_instance)
    if updated_instance is None:
        raise HTTPException(status_code=400, detail="Instance name already exists for this customer")

    # Update the instance with the new data
    return updated_instance
    
@app.delete("/customers/{customer_id}/instances/{instance_name}", response_model=schemas.Instance)
def delete_c55_instance(customer_id: int, instance_name: str, db: db_dependency):
    db_instance = check_instance(db=db, customer_id=customer_id, instance_name=instance_name)
    return crud.delete_customer(db=db, delete_instance=db_instance)



@app.post("/customers/{customer_id}/instances/{instance_id}/rollback", response_model=schemas.Instance)
def rollback_instance_version(customer_id: int, instance_id: int, version_id: int, db: db_dependency):
    db_customer = check_customer(db=db, customer_id=customer_id)
    
    # Get the version to roll back to
    version = db.query(InstanceVersion).filter(
        InstanceVersion.id == version_id,
        InstanceVersion.instance_id == instance_id
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Get the current instance
    instance = db.query(Instances).filter(Instances.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return crud.rollback_instance_version(db=db, instance=instance, version=version)
