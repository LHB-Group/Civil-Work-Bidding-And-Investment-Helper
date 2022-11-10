<h1 align="center"> Civil Work Bidding Price Prediction in San Francisco. AI-Powered.🌉🏗️ 💸</h1>

![python-shield](https://forthebadge.com/images/badges/made-with-python.svg)

* [App](https://costofmyconstructionproject.herokuapp.com/)
> In case of 404, click on [video capture](https://drive.google.com/file/d/13Y7McHQZtmEVhrX_G1Ukog_OVayNIo4P/view?usp=sharing)

## Table of contents
- [Table of contents](#table-of-contents)
- [Background](#background)
- [Project](#project)
- [Key documents](#key-documents)
  - [Top-directory layout](#top-directory-layout)
- [Technologies](#technologies)
- [Datasets](#datasets)
- [Getting started](#getting-started)
  - [Ensure that pip module is installed by running :](#ensure-that-pip-module-is-installed-by-running-)
  - [How to install pipenv ?](#how-to-install-pipenv-)
  - [Clone the repository :](#clone-the-repository-)
  - [Create your virtual environment :](#create-your-virtual-environment-)
  - [Install all required librairies :](#install-all-required-librairies-)
- [Install the project](#install-the-project)
- [License](#license)
- [Authors](#authors)
- [Contact](#contact)
- [Made with ❤️ in Paris](#made-with-️-in-paris)

## Background

San Francisco is a hyper-popular city with homeless community (20% of population), natural disaster risks and astronomical housing prices. Affordable housing in San Francisco has not been an option. Meanwhile, new affordable construction projects are high in need. Many investors consider construction projects to invest in SF, which can provide high return rate. For construction projects, engineers struggle to predict the construction project cost as reasonable as possible to win biddings. 🏗️ 💸

## Project

This project is an AI-powered app 🧠🤖 to estimate cost of construction projects in San Francisco. 

* [Presentation of project](https://docs.google.com/presentation/d/1uWvuKxi8LZJN_XV6F3pEtfRy1y2JgECC/edit?usp=sharing&ouid=117915938711430623839&rtpof=true&sd=true)

Some of the efforts include data cleaning, feature engineering, setting up machine learning models, predictive error calculation, parameter tuning, creating a dashboard and deploying an online app. 

Machine learning models were trained with the historical data coming from building permits of San Francisco available
since early 1980s (thanks to datasf.org). A set of parameters and machine learning models were tested (including Linear,Lasso model, E-Net, KRidge, GBoosting, XGBoost, LGBoost and Random Forest). **Random Forest Model**🌲🌳🌲🌳 was judged to use as a final model.

> Structural work cost 

> ✅ include cost of foundation, columns, beams, slabs, floors, roof and workmanship cost

> ❌ does not include land price, finishing work, electricity & plumbing and commercial costs

![pipeline](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper/blob/0b9bc8a0add95aa4bfb8555bd3746303d31c0cf0/.img_pipeline.PNG)

## Key documents
	
1 - Notebook on [exploratory data analysis](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper/blob/Master/NoteBooks/Exploratory_Data_Analysis.ipynb)

2 - Script on [data cleaning](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper/blob/Master/src/building_permits.py) 

3 - Notebook on [machine learning predictive models](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper/blob/Master/NoteBooks/predictive_models.ipynb)

4 - Logs on [scores of machine learning models and experiments](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper/blob/Master/Tracking/exp_logs.csv)

### Top-directory layout

    .
    ├── Docker                  # App deployment. Scripts with streamlit, final ML models and Docker container settings.
    ├── NoteBooks               # Jupyter notebooks on EDA, feature engineering and ML models
    ├── ShapeOut                # Documents on building footprints in SF
    ├── Tracking                # Logs of ML model scores and experiments
    ├── src                     # Scripts on functions, database cleaning, building ground surface area and ML model experiments 
    ├── LICENSE
    ├── README.md 
	├── README_FR.md
    └── requirements.txt

## Technologies
Project is created with:
* Python 3.8
* Jupyter Notebook 6.4.12
* Python libraries (see /requirements.txt)
* Streamlit 1.12.0
* Docker 20.10.18
* VSCode 1.71.2

## Datasets
1 - [San Francisco Permit Data](https://data.sfgov.org/Housing-and-Buildings/Building-Permits/i98e-djp9/data)

> A building permit is an official approval document issued by a government agency that allows a construction or a renovation project on a property. More information can be found on this [website](https://www.thespruce.com/what-is-a-building-permit-1398344). Each city or county has its own building office to perform multiple functions such as issuing permits, inspecting buildings for safety measures, changing rules to meet the needs of a growing population, etc. For the City of San Francisco, building permits are handled by [SF DBI](www.sfdbi.org/). The dataset includes details on application/permit ID, job location, the current status of the applications and some other details. Data is uploaded weekly by DBI.

2 - [Building Footprints in San Francisco](https://data.sfgov.org/Housing-and-Buildings/Building-Footprints-File-Geodatabase-Format-/asx6-3trm)

## Getting started

To run this project you need :

- [Python 3.10](https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe)
- [pip](https://packaging.python.org/en/latest/key_projects/#pip)
- [pipenv](https://pypi.org/project/pipenv/#pipenv-python-development-workflow-for-humans) (optional)
  
### Ensure that pip module is installed by running : 
```
```sh
python -m ensurepip --default-pip
```

### How to install pipenv ?
```sh
pip install pipenv
```

### Clone the repository :
   ```sh
   git clone https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper.git
   ```

### Create your virtual environment :
Go to your repository folder and run the following command.
```sh
python -m venv my_venv
# the my_venv folder should appear
```
Once created you need to activate your venv

Windows :
```sh
# Go to your repository folder and type :
./my_venv/Scripts/activate
# You should have something like :
(my_venv) C:\Users\...\Civil-Work-Bidding-And-Investment-Helper>
```
Linux / Mac OS :
```sh
# Go to your repository folder and type :
source my_venv/bin/activate
# You should have something like :
(my_venv) C:\Users\...\Civil-Work-Bidding-And-Investment-Helper>
```

### Install all required librairies :

```sh
pip install -r requirements.txt
```

## Install the project

The install.py script permit you to dowload and create all folders and files for the project. 

**<p>Build the complete dataset can take several hours because of feature engineering but you but <span style ="color: red">you can download it [here](https://drive.google.com/file/d/1Ffbhy12m4JG9REEdSQwwewIFE0KUiEX3/view?usp=sharing)</span> and move it to < Datasets > Folder</p>**
```sh
# go to the src folder and run :
python ./install.py
```
**<p>(Build the complete dataset can take several hours because of feature engineering)</p>**

## License

Distributed under the MIT License. See LICENSE.txt for more information.

## Authors

[croustibats](https://github.com/croustibats) ,
[hicham-mrani](https://github.com/hicham-mrani) and 	
[levist7](https://github.com/levist7)

## Contact

Please see contact details on presentation file [above](#project).

---
Made with ❤️ in Paris
---
