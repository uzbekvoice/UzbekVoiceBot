FROM pytorch/pytorch

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
COPY ./src/ /app/src

RUN apt-get update -y
RUN apt-get install libsndfile-dev -y
CMD python3 -u ./src/uzbekvoicebot.py