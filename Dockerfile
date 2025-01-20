FROM python:3.12.3


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


ARG PORT
ARG DATABASE_URL
ARG AWS_ACCESS
ARG AWS_SECRET
ARG BUCKET_NAME
ARG AWS_S3_ENDPOINT_URL
ARG AWS_LOCATION
ARG DEBUG
ARG FOCUS_API_KEY
ARG FOCUS_URL

RUN python manage.py collectstatic

ENV DJANGO_SETTINGS_MODULE=redesanta.settings

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]