FROM python:alpine
WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
RUN chmod 555 /app/entrypoint.sh
EXPOSE 8001
CMD ["/app/entrypoint.sh"]
