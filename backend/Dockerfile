FROM ubuntu:lunar-20230301

# System packages
RUN apt update
RUN apt install -y python3 python3-pip
RUN apt install -y apache2 apache2-utils libapache2-mod-wsgi-py3
RUN apt clean

# Redirects logs to stderr and stdout so docker can capture them
RUN ln -sf /dev/stdout /var/log/apache2/access.log && ln -sf /dev/stderr /var/log/apache2/error.log

# Disable default site, enable my API
COPY ./config/backend.conf /etc/apache2/sites-available/backend.conf
RUN a2dissite 000-default
RUN a2ensite backend

# User management
RUN groupadd -r apacheuser && useradd -r -g apacheuser apacheuser
RUN chown -R apacheuser /var/log/apache2/
RUN chown -R apacheuser /var/run/apache2/
USER apacheuser

# Setup python project
WORKDIR /opt/code
COPY backend/* /opt/code

CMD ["apache2ctl", "-D", "FOREGROUND"]