FROM python:3.8-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apk add --update --no-cache \
        g++ \
        libxml2 \
        libxml2-dev \
        libxslt-dev \
        py3-lxml
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"] 
