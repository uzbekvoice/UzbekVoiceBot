FROM pytorch/pytorch

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
COPY ./src/ /app/src

CMD python3 -u ./src/uzbekvoicebot.py