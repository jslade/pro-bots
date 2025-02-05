FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

CMD ["python", "startup.py"]
