FROM pytorch/pytorch

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./src/ /app

CMD python -u uzbekvoicebot.py