# syntax=docker/dockerfile:1
# comment to trigger ci
FROM harbor.irtsysx.fr/cab/cab-common:3.11.6-slim

RUN mkdir -p /usr/share/man/man1 \
  && apt-get update \
  && apt-get install -y --no-install-recommends default-jre \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


# Install recommendation-service modules
COPY . /my_app/

WORKDIR /my_app
RUN pip3 install --default-timeout=2000 --no-cache-dir -r requirements.txt

# CMD ["./entrypoint.sh"]
