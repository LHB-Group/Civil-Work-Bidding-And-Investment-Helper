"""
    authors: 
        - Baptiste Cournault
        - Hicham Mrani
        - Levent Isbiliroglu
    
    Description:
        This script tests different machine learning models by using cross validation
        provided a cleaned database and a list of features.
        It is inspired by a Kaggle notebook: https://www.kaggle.com/code/serigne/stacked-regressions-top-4-on-leaderboard
 
"""

import pandas as pd
import numpy as np


#sklearn libraries 
from sklearn.linear_model import LinearRegression, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor,  GradientBoostingRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import xgboost as xgb #library independent of sklearn
import lightgbm as lgb #library independent of sklearn

from functions import cross_validate_score, score_ML_log
import warnings
warnings.filterwarnings('ignore')

#inputs : fname1, description_ML, features_list, target_variable, k_fold, random_state
#db_v8 = 'https://drive.google.com/file/d/1Ffbhy12m4JG9REEdSQwwewIFE0KUiEX3/view?usp=sharing'
#fname1 = db_v8
#fname1='https://drive.google.com/uc?id=' + fname1.split('/')[-2]
fname1 = '/home/leo/Downloads/Building_Permits_v8.csv'
dataset = pd.read_csv(fname1, low_memory=False)
#Validation function
n_folds = 4
random_state = 0

description_ML = "dataset V8 | default feature used + total_area_m2 + Neighborhoods | Hicham"#add why you do this experiment

features_list = [
    "Permit Type",
    "Number of Proposed Stories_",
    "Proposed Use",
    "Proposed Units",
    "Proposed Construction Type_", 
    'lat_lon',
    "Neighborhoods - Analysis Boundaries",
    "total_area_m2",
]

target_variable = "Est_Cost_Infl_log10"


# Separate target variable Y from features X

print("Separating labels from features...")
X = dataset.loc[:,features_list]
Y = dataset.loc[:,target_variable]

print("\n...Done...\n")
print()

print('Y : ')
print(Y.head())
print()
print('X :')
print(X.head())

# Automatically detect names of numeric/categorical columns
numeric_features = []
categorical_features = []
for i,t in X.dtypes.iteritems():
    if ('float' in str(t)) or ('int' in str(t)) :
        numeric_features.append(i)
    else :
        categorical_features.append(i)

print('\nFound numeric features ', numeric_features)
print('\nFound categorical features ', categorical_features)

# Since we use Kfold, we don't divide data into train and test data set!
# And we use all dataset

X_train = X
Y_train = Y 
print("\n...Done...\n")
print()

# Create pipeline for numeric features
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')), # missing values will be replaced by columns' median
    ('scaler', StandardScaler())
])

# Create pipeline for categorical features
categorical_transformer = Pipeline(
    steps=[
    ('encoder', OneHotEncoder(drop='first')) # first column will be dropped to avoid creating correlations between features
    ])

# Use ColumnTransformer to make a preprocessor object that describes all the treatments to be done
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])# Separate target variable Y from features X


# Preprocessings on train set
print("\nPerforming preprocessings...\n")
#print(X.head())
X_train = preprocessor.fit_transform(X_train)
print('\n...Done...\n')


#Definition of models
print("\nDefining machine learning models...\n")
regressor0= LinearRegression()
#lasso regression
lasso = Lasso(alpha =0.0005, random_state=random_state)
#elastic net regression
"""
Elastic Net Regression:
    Elastic net is a combination of the two regularized linear regression: ridge and lasso. 
    Ridge utilizes an L2 penalty and lasso uses an L1 penalty. 
    Elastic net uses both the L2 and the L1 penalties. 
"""
ENet = ElasticNet(alpha=0.001, l1_ratio=0.15, random_state=random_state)


#kernel ridge regression
"""
Kernel Ridge Regression:
    KRR is a prediction technique with  classic least-squares linear regression. 
    It learns a linear function in the space induced by the respective kernel and the data. 
    It is often known as the kernel trick since it combines ridge regression with the kernel trick.
    The idea of support vector machines is considered by replacing the dot product in the support vector formulation
    by a kernel function.     
"""

KRR = KernelRidge(alpha=0.5, kernel='polynomial', gamma=0.05, degree=2, coef0=1.0)
#gradient boosting regression
"""
Gradient Boosting Model:
    GB builds an additive model in a forward stage-wise fashion;
    it allows for the optimization of arbitrary differentiable loss functions.
    In each stage a regression tree is fit on the negative gradient of the
    given loss function.
    Loss function is defined as 'huber'. It is a combination of 'squared_error' 
    and 'absolute_error'.
"""
GBoost = GradientBoostingRegressor(n_estimators=1000, learning_rate=0.05,
                                   max_depth=9, max_features='auto',
                                   min_samples_leaf=3, min_samples_split=3, 
                                   loss='huber', random_state =random_state)

#xgb
"""
    Extreme Gradient Boosting - XGB Model
    XG Model is one of the most used algorithm in ML. It is an implementation of gradient boosted decision trees.
    It was designed for speed and performance. It is an enhanced gradient boosting library and uses a gradient boosting framework.
    Ref. to the algorithm paper:

    XGBoost: A Scalable Tree Boosting System by Tianqi Chen, Carlos Guestrin
    link : https://arxiv.org/abs/1603.02754
    
    Parameters were tuned by GridSearch.
"""
model_xgb = xgb.XGBRegressor(colsample_bytree=0.8, gamma=0.4, 
                             learning_rate=0.1, max_depth=25, 
                             min_child_weight=1.5, n_estimators=400,
                             reg_alpha=1.2, reg_lambda=1.1,
                             subsample=0.7, silent=1,
                             random_state =random_state, nthread = -1)


#light gb
"""
    LightGBM - Gradient Boosting With LightGBM
    LightGBM is an algorithm developed by Microsoft in 2017. It has an advantage of changing the training algorithm that make the run time faster and likely result in a more effective model.
    Ref. to the LightGBM algorithm paper:

    LightGBM: A Highly Efficient Gradient Boosting Decision Tree, 2017.
    link : https://papers.nips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html
    
    Parameters were obtained by GridSearch.
"""
model_lgb = lgb.LGBMRegressor(objective='regression',num_leaves=5,
                              learning_rate=0.05, n_estimators=720,
                              max_bin = 55, bagging_fraction = 0.8,
                              bagging_freq = 5, feature_fraction = 0.2319,
                              feature_fraction_seed=9, bagging_seed=9,
                              min_data_in_leaf =6, min_sum_hessian_in_leaf = 11)
#random forest
"""
    A random forest regressor.

    'A random forest is a meta estimator that fits a number of classifying
    decision trees on various sub-samples of the dataset and uses averaging
    to improve the predictive accuracy and control over-fitting.
    The sub-sample size is controlled with the `max_samples` parameter if
    `bootstrap=True` (default), otherwise the whole dataset is used to build
    each tree.'
    
    Parameters were obtained by GridSearch.
"""
randomForestRegressor = RandomForestRegressor(max_depth=7, min_samples_leaf =4,
                                              min_samples_split=2, n_estimators=300,
                                              random_state=random_state)
print('\n...Done...\n')

models = [regressor0,
          lasso,
          ENet,
          KRR,
          GBoost, 
          model_xgb,
          model_lgb,
          randomForestRegressor
          ]

model_names = ["Linear Regressor Model",
               "Lasso Model",
               "Elastic Net Regressor Model",
               "Kernel Ridge Model",
               "Gradient Boosting Model",
               "XGBoost Model",
               "Light Gradient Boosting Model",
               "Random Forest Regressor Model"
               ]

count = 0
for model in models :
  print("\n**********"+model_names[count]+"**********")
  print("**********Scores on test set**********\n")
  cv_scores = cross_validate_score (model, n_folds, random_state, X_train, Y_train)
  score_1 = cv_scores['test_r2']
  print("R2 score - mean : {:.4f}  |  std : {:.4f}\n".format(score_1.mean(), score_1.std()))

  score_2 = np.sqrt(-cv_scores['test_neg_mean_squared_error'])
  print("\nRoot mean squared error - mean : {:.4f}  |  std : {:.4f}\n".format(score_2.mean(), score_2.std()))

  score_3 = np.sqrt(-cv_scores['test_neg_mean_squared_log_error'])
  print("\nRMSLE -logarithmic error - mean : {:.4f}  |  std : {:.4f}\n".format(score_3.mean(), score_3.std()))

  score_4 = -cv_scores["test_neg_mean_absolute_percentage_error"]
  print("\nMean absolute percentage error - mean : {:.3f}  |  std : {:.3f}\n".format(score_4.mean(), score_4.std()))

  score_5 = cv_scores["test_explained_variance"]
  print("\nExplained variance score - mean : {:.4f}  |  std : {:.4f}\n".format(score_5.mean(), score_5.std()))
  print("----------------END--------------------")
  count = count + 1
  score_ML_log(fname1, dataset, model, target_variable, categorical_features, numeric_features,
               description_ML, n_folds, random_state,
               score_1, score_2, score_3, score_4, score_5, 
               flog = "../Tracking/exp_logs.csv")