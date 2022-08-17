FROM continuumio/miniconda3
WORKDIR /home/app
COPY app.py app.py
COPY prepro.joblib prepro.joblib
COPY model.joblib model.joblib
COPY requirements.txt requirements.txt
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]
