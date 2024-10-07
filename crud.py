from sqlalchemy.orm import Session
from models import Customers, Instances, Agents, Deployments, InstanceVersion, CxContacts
import schemas

# Customer
def create_customer(db: Session, customer: schemas.CustomerCreate, cx_contact_list: set):
    new_customer = Customers(
        customer_name=customer.customer_name,
        aws_region=customer.aws_region)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    for cx in cx_contact_list:
        new_customer.cx_contacts.append(cx)

    db.commit()
    db.refresh(new_customer)
    return new_customer


def delete_customerx(db: Session, db_customer: Customers):
    print(f'Inside crud delete customer, db_customer: {db_customer.customer_name}')
    # Remove customer-cx associations
    db_customer.cx_contacts = []
    db.commit()

    # Delete customer
    db.delete(db_customer)
    db.commit()
    return db_customer


def get_customers(db: Session):
    return db.query(Customers).all()

def update_customer(db: Session, customer: schemas.CustomerCreate, update_customer: Customers, 
                    cx_contact_list: set):
    update_customer.customer_name = customer.customer_name
    update_customer.aws_region = customer.aws_region
    db.commit()
    db.refresh(update_customer)

    print(f'UPDATE_CUSTOMER.CX_CONTACTS: {update_customer.cx_contacts}')

    # print('BEFORE LOOP IN CRUD')
    # new_cx_contacts = []
    # for cx in cx_contact_list:
    #     print(f'In crud, contact cx ID: {cx.id}')
    #     # if cx not in update_customer.cx_contacts:
    #     new_cx_contacts.append(cx)
    #     # update_customer.cx_contacts.append(cx)
    # update_customer.cx_contacts = new_cx_contacts
    

    # Clear existing contacts and add new contacts
    update_customer.cx_contacts.clear()
    for cx in cx_contact_list:
        update_customer.cx_contacts.append(cx)
        
    
    db.commit()
    db.refresh(update_customer)

    return update_customer



# CX Contact
def get_cx_contacts(db: Session):
    return db.query(CxContacts).all()

def create_cx_contact(db: Session, cx: schemas.CxContactCreate):
    new_cx = CxContacts(username=cx.username, email=cx.email)
    db.add(new_cx)
    db.commit()
    db.refresh(new_cx)
    return new_cx

def update_cx_contact(db: Session, update_cx: CxContacts, cx: schemas.CxContactCreate):
    update_cx.username = cx.username
    update_cx.email = cx.email
    db.commit()
    db.refresh(update_cx)
    return update_cx 


# Instance
def get_c55_instances(db: Session, customer: schemas.Customer):
    return db.query(Instances).filter(Instances.customer_id == customer.id).all()

def create_c55_instance(db: Session, instance: schemas.InstanceCreate, customer_id: int):
    new_instance = Instances(
        instance_name=instance.instance_name, 
        customer_id=customer_id,
        c55_version=instance.c55_version,
        analytics_enabled = instance.analytics_enabled,
        last_deployment = instance.last_deployment
        )
    db.add(new_instance)
    db.commit()
    db.refresh(new_instance)
    return new_instance

def update_c55_instance(db: Session, instance: schemas.InstanceCreate, update_instance: Instances):
    # for key, value in instance.dict(exclude_unset=True).items():
    #     setattr(update_instance, key, value)

    # Check if another instance exists
    existing_instance = db.query(Instances).filter(
        Instances.customer_id == update_instance.customer_id,
        Instances.instance_name == instance.instance_name,
        Instances.id != update_instance.id
    )

    if existing_instance:
        return None

    update_instance.instance_name = instance.instance_name
    # update_instance.customer_id = instance.customer_id
    update_instance.c55_version = instance.c55_version
    update_instance.analytics_enabled = instance.analytics_enabled
    update_instance.last_deployment = instance.last_deployment

    db.commit()
    db.refresh(update_instance)
     
    return update_instance

def delete_customer(db: Session, delete_instance: Customers):
    db.delete(delete_instance)
    db.commit()
    return delete_instance

def rollback_instance_version(db: Session, instance: schemas.Instance, version: InstanceVersion):
    # Roll back the instance to the selected version
    instance.instance_name = version.instance_name
    instance.c55_version = version.c55_version
    instance.analytics_enabled = version.analytics_enabled
    instance.last_deployment = version.last_deployment
    instance.customer_id = version.customer_id
    
    db.commit()
    db.refresh(instance)
    
    return instance