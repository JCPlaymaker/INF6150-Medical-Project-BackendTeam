FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

WORKDIR /app

COPY . .

COPY ./entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


EXPOSE 8082

CMD ["./entrypoint.sh"]

