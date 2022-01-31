FROM python:3.7-slim

RUN pip3 install --upgrade pip

WORKDIR /backend

COPY requirements.txt .

RUN pip3 install -r /backend/requirements.txt --no-cache-dir

COPY . ./

COPY entrypoint.sh .

RUN chmod +x /backend/entrypoint.sh

ENTRYPOINT [ "/backend/entrypoint.sh" ]
