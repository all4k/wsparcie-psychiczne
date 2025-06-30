FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask
EXPOSE 8000
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]

