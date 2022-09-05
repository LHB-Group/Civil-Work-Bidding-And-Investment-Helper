FROM continuumio/miniconda3
WORKDIR /home/app
COPY . /home/app
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD streamlit run --server.port $PORT app.py
