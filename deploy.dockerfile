FROM debian:stable-slim
RUN apt update && apt install -y --no-install-recommends python3
WORKDIR /web-app
COPY base_template.html dpkg_info.py main.py web.py ./
CMD python3 main.py --port $PORT
