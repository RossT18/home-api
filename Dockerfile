FROM python:3.13

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./main.py /code/main.py
COPY ./util.py /code/util.py
COPY ./cache.py /code/cache.py
COPY ./routes /code/routes
COPY ./static /code/static

CMD ["fastapi", "run", "main.py", "--port", "5100"]