FROM python:3.9

EXPOSE 5000

COPY ./requirements.txt /usr/src/nfl_rushing/requirements.txt

WORKDIR /usr/src/nfl_rushing

RUN pip3 install -r requirements.txt

COPY ./nfl_rushing /usr/src/nfl_rushing

CMD [ "flask", "run", "--host=0.0.0.0" ]