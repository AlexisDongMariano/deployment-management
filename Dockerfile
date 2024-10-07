FROM python:3.10-slim

# set working dir
WORKDIR /app

# copy requirements
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]