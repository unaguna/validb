FROM python:3.8

RUN apt update
RUN apt install -y default-mysql-client-core

COPY .bashrc /root

COPY ./requirements.txt /var/lib/
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r /var/lib/requirements.txt
RUN rm /var/lib/requirements.txt

ADD ./my.cnf /etc/mysql/conf.d/my.cnf
ADD ./root_my.cnf /root/.my.cnf
RUN chmod 600 /root/.my.cnf

WORKDIR /root/src
