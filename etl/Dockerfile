FROM python:3.12-slim
WORKDIR /app
COPY etl/ ./
COPY common/ ./common
COPY etl/wait-for-it.sh /wait-for-it.sh
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /wait-for-it.sh
EXPOSE 9000
CMD ["/wait-for-it.sh", "rabbitmq", "5672", "--", "python", "worker.py"]