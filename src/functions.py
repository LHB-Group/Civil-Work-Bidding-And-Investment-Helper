"""
    authors: 
        - Baptiste Cournault
        - Hicham Mrani
        - Levent Isbiliroglu
    
    Description:
        - All functions used for the project
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, cross_validate
import time

def re_category (ds,counts, repl_ ):
    """
        It replaces the categories that are not sufficiently presented in the dataseries
        It also fills NaN values with the defined category value
    """
    n_count = ds.value_counts()
    m_ng = ds.isin (n_count.index[n_count.values < counts])
    ds[m_ng] = repl_
    ds.fillna(repl_,inplace=True)
    return ds.astype('str')


def text_split(x):
    """ 
        x will be sth similar to 'erect a two story 88 unit residential structure'
        we do text partition with 'story' 
        it returns tuple ('erect a two ', 'story', ' 88 unit residential structure')
        then, we take the first value of tuple 
        and then apply string manipulations to obtain floor number in text
    """
    return x.partition('story')[0].replace('-',' ').split(' ')[-2]


def text2int (x):
    """
        converting text to number for the possible cases
    """
    x = x.lower()
    if 'one' in x:
        y = 1
    elif 'two' in x:
        y= 2
    elif 'three' in x:
        y=3
    elif 'four' in x:
        y = 4
    elif 'five' in x:
        y = 5
    elif 'six' in x:
        y = 6
    elif 'seven' in x:
        y = 7
    elif 'eight' in x:
        y = 8
    elif 'nine' in x:
        y = 9
    elif  'ten' in x:
        y = 10
    elif  'eleven' in x:
        y = 11
    else:
        try : 
            y = int(x)
        except :
            y = np.nan
    return y



def cat_stories (st): 
    """
    adding a column with story number categories
    """   
    if st < 3 :
      y = '0-2 stories'
    elif st< 5 :
      y = '3-4 stories'
    elif st < 8 :
      y = '5-7 stories'
    elif st < 10 :
      y = '8-9 stories'
    else:
      y = 'More than 10 stories'
    return y


def get_polygon_list(points):
    polygon_list = []
    for i in range(len(points)):
        mask = polygons_serie.contains(points_serie[i])
        polygon_list.append(polygons_serie[mask])
        print(f'{len(polygon_list)}\n')
    return polygon_list


def cross_validate_score (model, n_folds, random_state, X_train, Y_train):
    """
        Function that runs cross validation and obtain metrics for a given machine learning model.
        Output is a dictionary composed of 
            "fit_time", "score_time", 
            "test_r2", "train_r2",
            "test_neg_mean_squared_error", "train_neg_mean_squared_error",
            "test_neg_mean_squared_log_error", "train_neg_mean_squared_log_error",
            "test_neg_mean_absolute_percentage_error", "train_neg_mean_absolute_percentage_error"
            "test_explained_variance", "train_explained_variance"
    """ 
    kf = KFold(n_folds, shuffle=True, random_state=random_state).split(X_train)
    cv_results = cross_validate(model, X_train, Y_train,
                                scoring=["r2","neg_mean_squared_error","neg_mean_squared_log_error",
                                         "neg_mean_absolute_percentage_error","explained_variance"],
                                return_train_score=True, cv = kf)
    return cv_results


def score_ML_log(fname_db, dataset, model, target_variable, categorical_features, numeric_features,
                 description_ML, n_folds, random_state,
                 score_1, score_2, score_3, score_4, score_5, 
                 flog):
    """
        Function that saves the logs including metrics for a given machine learning model.
        See below for the variable names.
        flog is the address of output .csv file.
    """ 
    #In case of error in calculating score, the archived result will be -99,-99,-99
    scores = [score_1, score_2, score_3, score_4, score_5]
    for score in scores:
        try:
          if len(score) < 1 :
             score=  [-99,-99,-99]
        except:
             score=  [-99,-99,-99]      

    #We save ML model results
    df1 = pd.DataFrame(
        {
        'date':[time.ctime()],
        'experiment': [description_ML], #name of your experiment, try to describe the reason of your experiment!
        'model':[model], #model name with parameters
        'rmse_cv_mean':[score_2.mean().round(3)],
        'rmse_cv_std':[score_2.std().round(3)],
        'dataset_version':[fname_db], 
        'dataset_shape':[dataset.shape],
        'target_variable':[target_variable],
        'features_cat':[categorical_features],
        'features_num':[numeric_features],
        'random_state':[random_state],
        'n_folds':[n_folds],
        'rmse_cv':[score_2],
        'r2_score_cv':[score_1],
        'rmsle_cv':[score_3],
        'mape_cv':[score_4],
        'evs_cv':[score_5]
        }
    )

    #Try-except method added for developers using cloud computing. 
    try :
      df0 = pd.read_csv(flog) 
      df = pd.concat([df0,df1])
      df.to_csv(flog,index=False)
    except:
      flog = "exp_logs_to_concate.csv"  
      try :
        df0 = pd.read_csv(flog)
        df = pd.concat([df0,df1])
        df.to_csv(flog,index=False)
      except:
        df1.to_csv(flog,index=False)
        # Do not forget to merge your .csv with original .csv in GitHub