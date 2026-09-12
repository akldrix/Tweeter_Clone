FROM python:3.12-alpine

WORKDIR /backend

COPY ./backend/requirements.txt /backend/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt

COPY ./backend /backend

CMD ["python3", "run.py"]