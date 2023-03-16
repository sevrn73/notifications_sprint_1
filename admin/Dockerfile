FROM python:3.9

WORKDIR /opt/admin

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
COPY entrypoint.sh .
RUN  pip install --upgrade pip && \
  pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x /opt/admin/entrypoint.sh

ENTRYPOINT ["/opt/admin/entrypoint.sh"]