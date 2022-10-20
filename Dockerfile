FROM pytorch/pytorch

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
COPY ./src/ /app

CMD python3 -u uzbekvoicebot.py