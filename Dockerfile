# FOR UBUNTU SERVER
FROM ubuntu:20.04

# FOR RAILWAY
RUN DEBIAN_FRONTEND=noninteractive

# Set timezone:
ENV CONTAINER_TIMEZONE=Asia/Ho_Chi_Minh
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

# Install dependencies:
RUN apt-get update && apt-get install -y keyboard-configuration

RUN apt-get update && apt-get -y install sudo
RUN sudo apt-get install software-properties-common -y
RUN sudo apt-get install python3.10 -y
RUN sudo apt-get install python3-pip -y

RUN sudo apt-get install -y fonts-liberation
RUN sudo apt-get install -y xdg-utils

# Sets the working directory in the container  
COPY . /app

# WORKDIR /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt --ignore-installed

# Command to run on container start    
ENTRYPOINT ["python3"]
CMD ["flask-api.py"]