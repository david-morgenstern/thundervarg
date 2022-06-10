FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-alpine3.14-2021-10-02

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app
