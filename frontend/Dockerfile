FROM node:16-alpine as build

WORKDIR /opt/code
ENV PATH /opt/code/node_modules:$PATH

COPY frontend/package.json /opt/code/package.json
RUN npm install --silent
RUN npm install @vue/cli -g
COPY frontend/ /opt/code
RUN npm run build

FROM httpd:2.4
COPY --from=build /opt/code/dist /usr/local/apache2/htdocs/
COPY ./config/frontend.conf /etc/apache2/sites-available/frontend.conf

RUN apt update && apt install -y curl
