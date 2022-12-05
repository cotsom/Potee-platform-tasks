# syntax=docker/dockerfile:1
FROM python:3.9-alpine
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers
RUN addgroup -g 2000 user \
    && adduser -u 2000 -G user -s /bin/sh -D user
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
USER user
CMD ["flask", "run"]
