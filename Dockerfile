FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y libpq-dev
RUN pip3 install --upgrade pip
RUN pip3 install django
RUN pip3 install reportlab==3.6.10
RUN pip3 install psycopg2
RUN pip3 install PyPDF2
RUN pip3 install pandas
RUN pip3 install openpyxl
RUN pip3 install numpy
RUN pip3 install requests==2.28.2
RUN pip3 install tk
RUN pip3 install python-math
RUN pip3 install beautifulsoup4
RUN pip3 install django-storages
RUN pip3 install boto
COPY . .
CMD python3 manage.py runserver 0.0.0.0:80