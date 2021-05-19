FROM python:3.9

EXPOSE 5000

COPY ./requirements.txt /usr/src/requirements.txt

WORKDIR /usr/src

RUN pip3 install -r requirements.txt

COPY . /usr/src

CMD [ "flask", "run", "--host=0.0.0.0" ]