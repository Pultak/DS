#
# Setup image with python client for master node and coloring of slave nodes accordingly
#

FROM ghcr.io/maxotta/kiv-ds-docker:latest

RUN yum -q -y install python3
#RUN yum install make gcc wget openssl-devel bzip2-devel libffi-devel zlib-devel -y

RUN pip3 install flask
RUN pip3 install requests
RUN pip3 install netifaces

COPY python /opt/backend

CMD /usr/bin/python3 /opt/backend/main.py

# EOF
