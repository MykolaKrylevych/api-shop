FROM python:3.10.4

RUN apt-get -y update && apt-get -y upgrade

WORKDIR "/app"

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]