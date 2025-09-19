FROM python:3.12-slim

RUN pip install psutil pyyaml

WORKDIR /app

COPY configure.py ./

CMD ["python", "configure.py"]

