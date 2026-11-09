FROM python:3.9

LABEL maintainer="Banyan Jullian <bjullian@uoregon.edu>"

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["flask_brevets.py"]