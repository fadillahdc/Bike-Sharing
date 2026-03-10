# Bike Sharing

## Setup Environment - Anaconda

conda create --name air-quality python=3.9
conda activate air-quality
pip install -r requirements.txt

## Setup Environment - Shell/Terminal

mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt

## Run Streamlit App

streamlit run dashboard/dashboard.py

## Run Live Streamlit App

https://geraldairquality.streamlit.app/
