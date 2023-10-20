FROM node:16.13.2-alpine as build-step

RUN mkdir -p /app
WORKDIR /app
COPY . /app
RUN npm install
RUN npm run build
# CMD ["npm", "start"]
# FROM nginx:1.20.1
# COPY --from=build-step /app/dist/ng-docker-example /usr/share/nginx/html
# EXPOSE 4200:80

FROM nginx:1.23.2-alpine
COPY --from=build-step /app/build/distribution /usr/share/nginx/html

VOLUME /tmp
ARG http_proxy
ARG https_proxy
ARG HTTP_PROXY_AUTH
ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
ENV HTTP_PROXY_AUTH=$HTTP_PROXY_AUTH
RUN env
RUN apk add bash curl logrotate --no-cache
ENV http_proxy=""
ENV https_proxy=""
ENV HTTP_PROXY_AUTH=""
RUN env
# COPY distribution /usr/share/nginx/html/
COPY start-webui.sh /
COPY nginx-logrotate-conf /etc/logrotate.d/nginx
CMD ["/bin/sh", "/start-webui.sh"]
