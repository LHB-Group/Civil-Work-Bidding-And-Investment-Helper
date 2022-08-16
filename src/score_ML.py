import time
import pandas as pd

#In case of error in calculating score, the archived result will be -99,-99,-99
scores = [score_1, score_2, score_3, score_4, score_5]
for score in scores:
    try:
      if len(score) < 1 :
         score=  [-99,-99,-99]
    catch:
         score=  [-99,-99,-99]      
        
    
df0 = pd.read_csv("../Tracking/exp_logs.csv") 
df1 = pd.DataFrame(
    {
    'date':[time.ctime()],
    'experiment': [description_ML], # put the name of you experiment -> it must be explicit !
    'model':model,
    'rmse_cv_mean':[score_2.mean().round(3)],
    'rmse_cv_std':[score_2.std().round(3)],
    'dataset_version':[fname1], # correct format examples : permit_building_v1, permit_building_v23 ... ect
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

df = pd.concat([df0,df1])

df.to_csv("../Tracking/exp_logs.csv",index=False)