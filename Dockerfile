FROM resin/rpi-raspbian:wheezy
MAINTAINER Alex Frois Prado <alex@shoprocket.co.uk>


RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    python \
    python-dev \
    python-pip \
    python-virtualenv \
    git 
    
RUN pip install Pillow
RUN pip install pyusb
RUN pip install bitarray

RUN git clone https://github.com/shoprocketprinter/Pip-Application.git
RUN cp /Pip-Application/60-ablesystems-pyusb.rules /etc/udev/rules.d
RUN cp /Pip-Application/usblp_blacklist.conf /etc/modprobe.d

Workdir /Pip-Application

CMD python V1.py

EXPOSE 80
