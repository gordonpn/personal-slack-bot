FROM python:3.8-alpine

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN adduser --shell /bin/bash --uid 1000 --system --home /home/appuser --disabled-password appuser
WORKDIR /home/appuser
USER appuser

COPY . .

CMD ["python", "./main.py"]
