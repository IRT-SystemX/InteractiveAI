FROM node:20-alpine as build-step
RUN mkdir -p /app
WORKDIR /app
COPY . /app
ARG VITE_POWERGRID_SIMU
ENV VITE_POWERGRID_SIMU=$VITE_POWERGRID_SIMU
RUN npm ci
RUN npm run build

FROM nginx:alpine
COPY --from=build-step /app/dist /usr/share/nginx/html

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
COPY start-webui.sh /
COPY nginx-logrotate-conf /etc/logrotate.d/nginx
CMD ["/bin/sh", "/start-webui.sh"]
