FROM python:3.8-alpine

RUN apk update \ 
    && apk add --no-cache gcc git python3-dev musl-dev linux-headers libc-dev rsync zsh \ 
    findutils wget util-linux grep libxml2-dev libxslt-dev \ 
    && pip3 install --upgrade pip

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD ["python3", "the_office_bot.py"]
