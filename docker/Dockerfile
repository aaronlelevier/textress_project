FROM python:3.4
ENV PYTHONUNBUFFERED 1
RUN mkdir /textra_project
WORKDIR /textra_project
COPY ../requirements.txt /textra_project/
RUN pip install -r requirements.txt
ADD ../. /textra_project/