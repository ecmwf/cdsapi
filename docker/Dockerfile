FROM python:3.7-alpine 

RUN pip3 install cdsapi
WORKDIR /input
COPY request.json request.json
WORKDIR /output
WORKDIR /app
COPY retrieve.py retrieve.py

CMD ["python", "retrieve.py"]
