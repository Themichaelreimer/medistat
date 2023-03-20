FROM node:19-alpine3.17 as build

WORKDIR /opt/code
ENV PATH /opt/code/node_modules:$PATH

COPY frontend/package.json /opt/code/package.json
RUN npm install --silent
RUN npm install @vue/cli -g
COPY frontend/ /opt/code
RUN npm audit fix --force
RUN npm run build


FROM httpd:2.4
COPY --from=build /opt/code/dist /opt/code
COPY ./config/frontend.conf /etc/apache2/sites-available/frontend.conf
