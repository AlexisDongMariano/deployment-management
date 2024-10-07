# Creating requirements.txt
pip freeze > requirements.txt









CUSTOMERS = [
    {'name': 'customer1', 'region': 'region1'},
    {'name': 'customer2', 'region': 'region1'}
]

class Customer(BaseModel):
    name: str
    region: str | None = None
    



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/customers/{customer_name}")
async def read_customer(customer_name: str):
    for customer in CUSTOMERS:
        if customer.get('id').casefold() == customer_name.casefold():
            return customer
    


@app.post("/customers/")
async def create_customer(customer: Customer):
    return customer



NEXT! Create CUSTOMER:
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customers).filter(models.Customers.customer_name == customer.customer_name).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Customer already registered")
    
    new_customer = models.Customers(customer_name=customer.customer_name)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    for contact_id in customer.cx_contact_ids:
        db_contact = db.query(models.CxContacts).filter(models.CxContacts.id == contact_id).first()
        if not db_contact:
            raise HTTPException(status_code=404, detail=f"Contact with id {contact_id} not found")
        new_customer.cx_contacts.append(db_contact)
    
    db.commit()
    db.refresh(new_customer)
    
    return new_customer


=================
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customers</title>
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Customers</h1>
        <div class="accordion" id="customersAccordion">
            {% for customer in customers %}
            <div class="card">
                <div class="card-header" id="heading{{ customer.id }}">
                    <h2 class="mb-0">
                        <button class="btn btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ customer.id }}" aria-expanded="true" aria-controls="collapse{{ customer.id }}">
                            {{ customer.customer_name }}
                        </button>
                    </h2>
                </div>
                <div id="collapse{{ customer.id }}" class="collapse" aria-labelledby="heading{{ customer.id }}" data-bs-parent="#customersAccordion">
                    <div class="card-body">
                        <h5>Contact Information</h5>
                        <ul>
                            {% for contact in customer.cx_contacts %}
                            <li>{{ contact.username }} - {{ contact.email }}</li>
                            {% endfor %}
                        </ul>
                        <h5>Instances</h5>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Instance Name</th>
                                    <th>C55 Version</th>
                                    <th>Analytics Enabled</th>
                                    <th>Last Deployment</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for instance in customer.instances %}
                                <tr>
                                    <td>{{ instance.id }}</td>
                                    <td>{{ instance.instance_name }}</td>
                                    <td>{{ instance.c55_version }}</td>
                                    <td>{{ instance.analytics_enabled }}</td>
                                    <td>{{ instance.last_deployment }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script src="/static/js/bootstrap.bundle.min.js"></script>
</body>
</html>





# UPDATING CX next