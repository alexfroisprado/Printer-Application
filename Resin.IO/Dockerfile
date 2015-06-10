FROM resin/rpi-raspbian:wheezy-2015-06-03
MAINTAINER Alex Frois Prado <alex@shoprocket.co.uk>


RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    python \
    python-dev \
    python-pip \
    python-virtualenv \
    python-usb \
    git 
    
RUN pip install Pillow
RUN pip uninstall -y pyusb && pip install pyusb==1.0.0b1
RUN pip install bitarray 
RUN pip install galileo

RUN git clone https://github.com/shoprocketprinter/Pip-Application.git

COPY /Pip-Application/60-ablesystems-pyusb.rules /etc/udev/rules.d/60-ablesystems-pyusb.rules
COPY /Pip-Application/99-fitbit.rules /etc/udev/rules.d/99-fitbit.rules
CMD  service udev restart

COPY /Pip-Application/usblp_blacklist.conf /etc/modprobe.d/usblp_blacklist.conf
COPY /Pip-Application/ipv6.conf /etc/modprobe.d/ipv6.conf


Workdir /Pip-Application

CMD python V1.py

