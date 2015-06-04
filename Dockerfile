FROM resin/rpi-raspbian:wheezy
MAITAINER Alex Frois Prado <alex@shoprocket.co.uk>


RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    python \
    python-dev \
    python-pip \
    python-virtualenv \
    git \
    
   

RUN git clone https://github.com/shoprocketprinter/Pip-Application.git
RUN cp /Pip-Application/60-ablesystems-pyusb.rules /etc/udev/rules.d
RUN cp /pip-Application/usblp_blacklist.conf /etc/modprobe.d

Workdir /Pip-Application

CMD ["python", "V1.py"]

EXPOSE 8080
