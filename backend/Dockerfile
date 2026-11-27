FROM python:3.14.7-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .
RUN useradd --uid 10001 --create-home agrotracer
USER agrotracer
CMD ["python", "-m", "app.run"]
