FROM python:3.12.8-slim

WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN pip install locust --no-cache-dir

COPY ./load_testing/ .

EXPOSE 8089

CMD ["locust", "--config", "api_response_times.conf"]