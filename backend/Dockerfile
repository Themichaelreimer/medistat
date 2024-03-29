FROM ubuntu:lunar-20230301

# System packages
RUN apt update --fix-missing
RUN apt install -y python3 python3-pip
RUN apt install -y virtualenv
RUN apt install -y apache2 apache2-utils libapache2-mod-wsgi-py3
RUN apt install -y postgresql-client
# curl is needed for health checks, which run inside the container itself 
RUN apt install -y curl 
RUN apt clean

# Redirects logs to stderr and stdout so docker can capture them
RUN ln -sf /dev/stdout /var/log/apache2/access.log && ln -sf /dev/stderr /var/log/apache2/error.log

# Disable default site, enable my API
COPY ./config/backend.conf /etc/apache2/sites-available/backend.conf
RUN a2dissite 000-default
RUN a2ensite backend

# User management
RUN chown -R www-data /var/log/apache2/
RUN chown -R www-data /var/run/apache2/

# Setup python project
WORKDIR /opt/code
COPY backend /opt/code/
RUN chown -R www-data /opt/code 

USER www-data
RUN virtualenv venv-backend
RUN . /opt/code/venv-backend/bin/activate && pip3 install -r requirements.txt

CMD ["apache2ctl", "-D", "FOREGROUND"]