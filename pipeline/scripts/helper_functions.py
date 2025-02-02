import numpy as np 
from scipy.stats import pearsonr
import os
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.metrics import explained_variance_score
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Lasso, Ridge, ElasticNet,LinearRegression,LogisticRegression
from sklearn.svm import SVC,SVR
from sklearn.feature_selection import SelectKBest, f_regression
import matplotlib.pyplot as plt
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, LeaveOneGroupOut
import glob
import math
from sklearn.ensemble import RandomForestClassifier

import warnings
warnings.filterwarnings('ignore') 

# Function comments are enhanced with ChatGPT.

def prepare_data(X):
    '''Clean X-data (remove zero-value input variables)'''

    # remove inputs that are 0 for all subjects
    zeros=X==0
    zeros=np.sum(zeros,0)
    zeros=zeros==X.shape[0]
    X=X[:,~zeros]
    print("Final size of X: " + str(X.shape))
    
    return X

def prepare_image_data(X):
    '''Clean X-data (remove zero-value input variables)'''

    # remove inputs that are 0 for all subjects
    X=np.reshape(X, (101,902629))
    print("Final size of X: " + str(X.shape))
    
    return X

def np_pearson_cor(x, y):
    '''Fast array-based pearson correlation that is more efficient. 
    FROM: https://cancerdatascience.org/blog/posts/pearson-correlation/.
        x - input N x p
        y - output N x 1
        
        returns correlation p x 1 '''
    xv = x - x.mean(axis=0)
    yv = y - y.mean(axis=0)
    xvss = (xv * xv).sum(axis=0)
    yvss = (yv * yv).sum(axis=0)
    result = np.matmul(xv.transpose(), yv) / np.sqrt(np.outer(xvss, yvss))
    
    # bound the values to -1 to 1 in the event of precision issues
    return np.maximum(np.minimum(result, 1.0), -1.0)


def np_pearson_cor_abs(x, y):
    '''Fast array-based pearson correlation that is more efficient. 
    FROM: https://cancerdatascience.org/blog/posts/pearson-correlation/.
        x - input N x p
        y - output N x 1
        
        returns correlation p x 1 '''
    print(x.shape)
    print(y.shape)
    xv = x - x.mean(axis=0)
    yv = y - y.mean(axis=0)
    xvss = (xv * xv).sum(axis=0)
    yvss = (yv * yv).sum(axis=0)
    result = np.matmul(xv.transpose(), yv) / np.sqrt(np.outer(xvss, yvss))
    
    # bound the values to -1 to 1 in the event of precision issues
    return abs(np.maximum(np.minimum(result, 1.0), -1.0))

        
def save_plots_true_pred(true, pred,filename, corr):
    f1 = plt.figure()
    plt.scatter(true, pred,s=10, c='black')
    plt.xlim(-0.1, 1.1)
    plt.ylim(-0.1, 1.1)
    plt.text(0.1, 0.1, corr)
    plt.xlabel('True normed motor score')
    plt.ylabel('Predicted normed motor score')
    np.save(os.path.join(filename + "_true.npy"), true)
    np.save(os.path.join( filename + "_pred.npy"), pred)

    plt.savefig(filename +'_truepred.png')
      
def naive_pearson_cor(X, Y):
    '''Naive (scipy-based/iterative) pearson correlation. 
    FROM: https://cancerdatascience.org/blog/posts/pearson-correlation/.
        x - input N x p
        y - output N x 1
        
        returns correlation p x 1 '''
    result = np.zeros(shape=(X.shape[1], Y.shape[1]))
    for i in range(X.shape[1]):
        for j in range(Y.shape[1]):
            r, _ = pearsonr(X[:,i], Y[:,j])
            result[i,j] = r
    return result[0]

def determine_featselect_range(X):
    #This function determines the range of values to use for the k parameter in the SelectKBest
    # feature selection method. The k parameter specifies the number of top-ranking features to select.

    # The range of values is determined using the number of columns in the input matrix X, with a minimum value of
    # X_min_dim and a maximum value of X_max_dim. The range is determined by taking n logarithmically spaced values
    # between the logarithms of these minimum and maximum values, with a base of base. These values are then converted
    # to int values and returned as the k_range.
    X_max_dim = X.shape[1]
    X_min_dim = 5
    n = 30
    base = 2
    k_range=np.logspace(math.log(X_min_dim,base),math.log(X_max_dim,base), n,base=base, dtype=int)
    return k_range

def get_models(model_type='regression', model_list=None):
    # This code defines a function named get_models() that takes two arguments: model_type and model_list. 
    # The function uses the model_type argument to determine which set of models to return. If model_type is set to 'regression',
    # the function will return a list of regression models. If model_type is set to 'classification', the function 
    # will return a list of classification models. The model_list argument is used to filter the models that are returned 
    # by the function. Only models whose names are included in the model_list will be returned. The function returns 
    # a tuple containing two elements: a list of models and a list of labels for those models.
    
    mdls=[]
    if model_type == 'regression':
        if 'ridge' in model_list:
            ridge = Pipeline([('featselect', SelectKBest(f_regression)), ('ridge', Ridge(normalize=True, max_iter=1000000, random_state=0))])
            mdls = ridge
        if 'elastic_net' in model_list:
            elastic_net =  Pipeline([('elastic_net', ElasticNet(normalize=True, max_iter=1000000, random_state=0, warm_start=True, tol=8.1))])
            mdls = elastic_net
        if 'lasso' in model_list:
            lasso =  Pipeline([('lasso', Lasso(normalize=True, max_iter=1000000, random_state=0))])
            mdls = lasso
        if 'ensemble_reg' in model_list:
            ensemble_reg = Pipeline([('ensemble_reg', LinearRegression())])
            mdls = ensemble_reg
        if 'svr' in model_list:
            svr = Pipeline([('svr', SVR())])
            mdls = svr
        if 'linear_regression' in model_list:
            linear_regression = Pipeline([('linear_regression', LinearRegression())])
            mdls = linear_regression
        if 'ridge_nofeatselect' in model_list:
            ridge_nofeatselect = Pipeline([('ridge_nofeatselect', Ridge(normalize=True, max_iter=1000000, random_state=0))])
            mdls = ridge_nofeatselect
        mdls_labels = model_list

        return mdls, mdls_labels
        
    elif model_type == 'classification': 
        print('Selecting classification models')
        if 'svm' in model_list:
            svm = Pipeline([ ('svm', SVC(probability=True, class_weight='balanced', kernel='linear', random_state=0))])
            mdls.append(svm)
        if 'rbf_svm' in model_list:
            rbf_svm = Pipeline([('svm', SVC(probability=True, class_weight='balanced', kernel='rbf', random_state=0))])
            mdls.append(rbf_svm)  
        if 'log' in model_list:
            log = Pipeline([('logistic', LogisticRegression(class_weight='balanced', solver='liblinear', random_state=0))])
            mdls.append(log)
        if 'rf' in model_list:
            rf = Pipeline([('rf', RandomForestClassifier())])
            mdls.append(rf)
        mdls_labels = model_list 
    return mdls, mdls_labels

def inner_loop(mdl, mdl_label, X, Y, group, inner_cv, n_jobs):
    
    if mdl_label =='ensemble_reg':
        print('No feature selection')
    elif mdl_label=='linear_regression':
        print('No feature selection -- Linear regression')
    elif mdl_label=='ridge_nofeatselect':
        print('No feature selection -- Ridge regression')
    else:
        k_range = determine_featselect_range(X)
    
    if mdl_label=='ridge':
        grid_params ={'ridge__alpha': np.logspace(-2, 2, 30, base=10,dtype=None),
                      'featselect__k':k_range}
        score = 'explained_variance'
        
    elif mdl_label =='ridge_nofeatselect':
        grid_params ={'ridge_nofeatselect__alpha': np.logspace(-2, 2, 30, base=10,dtype=None)}
        score = 'explained_variance'
        
    elif mdl_label=='ensemble_reg':
        score = 'explained_variance'
        
    elif mdl_label=='linear_regression':
        score = 'explained_variance'
        
    elif mdl_label=='svr':
        grid_params = {'svr__C': [0.0001, 0.001, 0.01, 0.1, 1],
                        'svr__gamma': [0.001, 0.01, 0.1, 1]}
        score = 'explained_variance'   
            
    elif mdl_label=='elastic_net':
        grid_params ={'elastic_net__alpha': np.logspace(-2, 2, 30, base=10,dtype=None), 'elastic_net__l1_ratio':np.linspace(0, 1, 30, dtype=None)}
        score = 'explained_variance'
        
    elif mdl_label=='lasso':
        grid_params ={'lasso__alpha': np.logspace(-2, 2, 30, base=10,dtype=None)}
        score = 'explained_variance'
        
    elif mdl_label == 'svm':
        grid_params = {'svm__C': [0.0001, 0.001, 0.01, 0.1, 1]}
        score = 'roc_auc'
    elif mdl_label== 'rbf_svm':
        grid_params = {'svm__C': [0.0001, 0.001, 0.01, 0.1, 1],
                        'svm__gamma': [0.001, 0.01, 0.1, 1]}
        score = 'roc_auc'
    elif mdl_label=='log':
        grid_params = {'logistic__C': [0.0001, 0.001, 0.01, 0.1, 1, 10],
                       'logistic__penalty': ['l1', 'l2']}
        score = 'roc_auc'
    elif mdl_label=='xgboost':
        grid_params = {'xgboost__gamma': [0.5, 1, 1.5, 2, 5],
                       'xgboost__learning_rate': [0.01, 0.1, 0.3],
                       'xgboost__max_depth': [3, 4, 5]}
    elif mdl_label=='rf':
        grid_params = {'rf__n_estimators': [5, 10, 15, 20],
                 'rf__max_depth': [2, 5, 7, 9]}
        score = 'roc_auc'
    else:
        print('Model not found..')
        return mdl
    
    if mdl_label == 'ensemble_reg':
        return mdl
    elif mdl_label=='linear_regression':
        return mdl
    else:
        print('Performing grid search for: {} \n'.format(mdl_label))

        grid_search = GridSearchCV(estimator=mdl, param_grid=grid_params, scoring=score, cv=inner_cv, refit=True, verbose=1,
                                n_jobs=n_jobs, return_train_score=False, pre_dispatch='2*n_jobs')

    grid_search.fit(X, Y, group)
    best_mdl = grid_search.best_estimator_

    return best_mdl

def get_beta_coefficients(cols, mdl, mdl_label, chaco_type, atlas, X):
    # In case there was feature selection, return full size feature set with 0s for features not selected
    
    beta_coeffs = mdl.named_steps[mdl_label].coef_
    
    # first transform (ie rearrange) the beta coefficients

    if chaco_type =='chacovol':
        if atlas == 'fs86subj':
            
            idx=np.ones(shape=(86,1), dtype='bool')
            idx[cols]=False # set SC weights that are features to be 1
            idx=idx.flatten()
            zeroidx=np.arange(0, 86, dtype='int')
            zeroidx=zeroidx[idx]
            
            # fill spots with 0's (up to 3192)
            k=0
            activation_full = beta_coeffs
            while k < zeroidx.shape[0]:
                activation_full=np.insert(activation_full, zeroidx[k],0)
                k=k+1
            
            #print("Full 3192: " + str(np.sum(activation_full>0)))
            # fill spots with 0's (up to 3655)
            zeros=X==0
            zeros=np.sum(zeros,0) # number of zeros across subjects
            zeros=zeros==X.shape[0] # find columns with zeros for all 101 subjects
            X=X[:,~zeros]
            
            zeroidx=np.arange(0, 86)
            zeroidx=zeroidx[zeros]
            
            # fill spots with 0's
            k=0
            a = activation_full
            while k < zeroidx.shape[0]:
                a=np.insert(a, zeroidx[k],0)
                k=k+1
            
            beta_coeffs = a
        elif atlas == 'shen268':
            
            idx=np.ones(shape=(268,1), dtype='bool')
            idx[cols]=False # set SC weights that are features to be 1
            idx=idx.flatten()
            zeroidx=np.arange(0, 268, dtype='int')
            zeroidx=zeroidx[idx]
            
            # fill spots with 0's (up to 3192)
            k=0
            activation_full = beta_coeffs
            while k < zeroidx.shape[0]:
                activation_full=np.insert(activation_full, zeroidx[k],0)
                k=k+1
            
            #print("Full 3192: " + str(np.sum(activation_full>0)))
            # fill spots with 0's (up to 3655)
            zeros=X==0
            zeros=np.sum(zeros,0) # number of zeros across subjects
            zeros=zeros==X.shape[0] # find columns with zeros for all 101 subjects
            X=X[:,~zeros]
            
            zeroidx=np.arange(0, 268)
            zeroidx=zeroidx[zeros]
            
            # fill spots with 0's
            k=0
            a = activation_full
            while k < zeroidx.shape[0]:
                a=np.insert(a, zeroidx[k],0)
                k=k+1
            
            activation = a
            beta_coeffs = a
    elif chaco_type=='chacoconn':
        if atlas == 'fs86subj':
                
            idx=np.ones(shape=(3192,1), dtype='bool')
            idx[cols]=False # set SC weights that are features to be 1
            idx=idx.flatten()
            zeroidx=np.arange(0, 3192, dtype='int')
            zeroidx=zeroidx[idx]
            
            # fill spots with 0's (up to 3192)
            k=0
            activation_full = beta_coeffs
            while k < zeroidx.shape[0]:
                activation_full=np.insert(activation_full, zeroidx[k],0)
                k=k+1
            
            #print("Full 3192: " + str(np.sum(activation_full>0)))
            # fill spots with 0's (up to 3655)
            zeros=X==0
            zeros=np.sum(zeros,0) # number of zeros across subjects
            zeros=zeros==X.shape[0] # find columns with zeros for all 101 subjects
            X=X[:,~zeros]
            
            zeroidx=np.arange(0, 3655)
            print(zeroidx.shape)
            print(zeros.shape)
            zeroidx=zeroidx[zeros]
            
            # fill spots with 0's
            k=0
            a = activation_full
            while k < zeroidx.shape[0]:
                a=np.insert(a, zeroidx[k],0)
                k=k+1
            
            activation = a
            fs86_counts = np.zeros((86, 86))
            inds = np.triu_indices(86, k=1)
            fs86_counts[inds] = activation
            beta_coeffs = fs86_counts
        elif atlas == 'shen268':
            idx=np.ones(shape=(25056,1), dtype='bool')
            idx[cols]=False # set SC weights that are features to be 1
            idx=idx.flatten()
            zeroidx=np.arange(0, 25056, dtype='int')
            zeroidx=zeroidx[idx]
            
            # fill spots with 0's (up to 3192)
            k=0
            activation_full = beta_coeffs
            while k < zeroidx.shape[0]:
                activation_full=np.insert(activation_full, zeroidx[k],0)
                k=k+1
            
            #print("Full 3192: " + str(np.sum(activation_full>0)))
            # fill spots with 0's (up to 3655)
            zeros=X==0
            zeros=np.sum(zeros,0) # number of zeros across subjects
            zeros=zeros==X.shape[0] # find columns with zeros for all 101 subjects
            X=X[:,~zeros]
            
            zeroidx=np.arange(0, 35778)
            zeroidx=zeroidx[zeros]
            
            # fill spots with 0's
            k=0
            a = activation_full
            while k < zeroidx.shape[0]:
                a=np.insert(a, zeroidx[k],0)
                k=k+1
            
            activation = a
            shen268_counts = np.zeros((268, 268))
            inds = np.triu_indices(268, k=1)
            shen268_counts[inds] = activation
            beta_coeffs = shen268_counts
        

    return beta_coeffs

def create_outer_cv(outer_cv_id):
    #This code defines a function that creates a cross-validation object for use in training and evaluating machine learning models.
    # The function takes as input an identifier for the type of cross-validation to use (outer_cv_id).
    
    if outer_cv_id=="1": # random
        outer_cv = KFold(n_splits=5, shuffle=True)
    elif outer_cv_id =="2": # leave one group out
        outer_cv = LeaveOneGroupOut()
    elif outer_cv_id =='3':
        outer_cv = GroupKFold(n_splits=5)
    elif outer_cv_id == "4" or outer_cv_id =="5":
        outer_cv = GroupShuffleSplit(train_size=.8)
    return outer_cv
        
def create_inner_cv(inner_cv_id, perm):
    #This code defines a function that creates a cross-validation object for use in training and evaluating machine learning models.
    # The function takes as input an identifier for the type of cross-validation to use (inner_cv_id) and a random seed (perm).
    
    # Based on the value of inner_cv_id, the function returns a different cross-validation object. For example,
    # if inner_cv_id is 1, the function returns a KFold object with 5 splits and shuffling enabled. If inner_cv_id is 3, 
    # the function returns a GroupKFold object with 5 splits. This allows the user to easily create different types of
    # cross-validation objects without having to specify all the parameters each time.
    
    if inner_cv_id=="1": # random
        inner_cv = KFold(n_splits=5, shuffle=True, random_state=perm)
    elif inner_cv_id =="2": # leave one group out
        inner_cv = KFold(n_splits=5, shuffle=True, random_state = perm)
    elif inner_cv_id =='3':
        inner_cv = GroupKFold(n_splits=5)
    elif inner_cv_id == "4":
        inner_cv = KFold(n_splits=5, shuffle=True,random_state=perm)
    elif inner_cv_id == "5":
        inner_cv = GroupShuffleSplit(train_size = 0.8)
    return inner_cv
    
def run_regression(x, Y, subIDs, inner_cv_id, outer_cv_id, model_tested, atlas, y_var, chaco_type, subset, save_models,results_path,crossval_type,nperms,null, output_folder, acute_data):
    # This code implements a cross-validation procedure for training and evaluating machine learning models on brain imaging data. 
    # The function takes as input the features (x), labels (Y), grouping information (group), inner and outer cross-validation schemes 
    # (inner_cv_id, outer_cv_id), a list of models to test (model_tested), an atlas of the brain (atlas), the name of the dependent variable 
    # (y_var), a string indicating the type of structural disconnection (chaco_type), a subset of the data to use (subset), a flag indicating whether
    # to save trained models (save_models), a path to save the results (results_path), the type of cross-validation (crossval_type), the number
    # of permutations to run (nperms), a flag indicating whether to run a null model (null), a path to save the output (output_folder).
    #
    #The function first prepares the features x for training by reshaping them based on the value of atlas. Next, it creates the outer cross-validation object
    # and splits the data into training and testing sets using the provided indices. Then, it loops through the different models specified in
    # model_tested and trains and evaluates each model using the training and testing sets. The function returns the trained models, 
    # explained variance, variable importance, correlations, and size of the test group for each model.
    # - ChatGPT

        
    if atlas =='lesionload_m1' :
        X=np.array(x).reshape(-1,1)
    elif atlas == 'lesionload_all':
        X=np.array(x)
    elif atlas == 'lesionload_all_2h' or atlas == 'lesionload_slnm':
        X=np.array(x)
    else:
        X = x
        
    if acute_data:
        acute_Y = acute_data['acute_Y']
        acute_subIDs = acute_data['acute_subIDs']
        if atlas =='lesionload_m1' :
            acute_X =acute_data['acute_LL']
            acute_X=np.array(acute_X).reshape(-1,1)
        elif atlas == 'lesionload_all':
            acute_X =acute_data['acute_LL']
            acute_X=np.array(acute_X)
        elif atlas == 'lesionload_all_2h' or atlas == 'lesionload_slnm':
            acute_X =acute_data['acute_LL']
            acute_X=np.array(acute_X)
        else:
            acute_X =acute_data['acute_X']
            acute_X = acute_X

    # grab CV object for outer CV
    outer_cv = create_outer_cv(outer_cv_id)
    
    outer_cv_splits = outer_cv.get_n_splits(X, Y, subIDs)
    
    models = np.zeros((outer_cv_splits), dtype=object)
    explained_var  = np.zeros((outer_cv_splits), dtype=object)
    correlations  = np.zeros((outer_cv_splits), dtype=object)
    size_testgroup =[]

    for n in range(0,nperms):
        
        print('\n\n~ ~ ~ ~ ~ ~ ~ ~ ~ ~ PERMUTATION: {}/{} ~ ~ ~ ~ ~ ~ ~ ~ ~ \n\n'.format(n, nperms))
        
        beta_coeffs_weights=[]
        for cv_fold, (train_id, test_id) in enumerate(outer_cv.split(X, Y, subIDs)): 
                        
            print("------ Outer Fold: {}/{} ------".format(cv_fold + 1, outer_cv_splits))
            
            X_train, X_test = X[train_id], X[test_id]  # for acutechronic, this is only chronic data.
            y_train, y_test = Y[train_id], Y[test_id]

            group_train, group_test = subIDs[train_id], subIDs[test_id]
            
            if acute_data:
                print('Acute data incorporated into training set.')
                X_train = np.concatenate((X_train, acute_X),axis=0)
                y_train = np.concatenate((y_train, acute_Y),axis=0)
                group_train = np.concatenate((group_train, acute_subIDs), axis=0)
    
            
            print('Size of test: {}'.format(y_test.shape[0]))
            print('Size of train: {}'.format(X_train.shape[0]))
            
            # grab the model specified/create Pipeline if necessary
            mdl, mdl_label = get_models('regression', model_tested) 

            # save size of test group
            size_testgroup.append(group_test.shape[0])
            
            # grab CV object 
            inner_cv = create_inner_cv(inner_cv_id,n)

            # do cross-validation to find an optimal model 
            mdl = inner_loop(mdl, mdl_label, X_train, y_train, group_train, inner_cv, 10)  

            # fit best model to full training set
            mdl.fit(X_train, y_train)
            
            # extract features from the fit model
            if model_tested == 'ridge':
                cols = mdl['featselect'].get_support(indices=True)
                beta_coeffs = get_beta_coefficients(cols, mdl, mdl_label, chaco_type, atlas, x)
                beta_coeffs_weights.append(beta_coeffs)

            elif model_tested== 'ridge_nofeatselect':
                mdl_label=mdl_label
                if atlas =='lesionload_all':
                    cols = [0, 1, 2, 3, 4, 5]
                    beta_coeffs = get_beta_coefficients(cols, mdl, mdl_label, chaco_type, atlas, x)
                    beta_coeffs_weights.append(beta_coeffs)
                    
                elif atlas == 'lesionload_all_2h':
                    cols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
                    beta_coeffs = get_beta_coefficients(cols, mdl, mdl_label, chaco_type, atlas, x)
                    beta_coeffs_weights.append(beta_coeffs)
                    
                elif atlas == 'lesionload_slnm':
                    cols = [0, 1, 2, 3, 4]
                    beta_coeffs = get_beta_coefficients(cols, mdl, mdl_label, chaco_type, atlas, x)
                    beta_coeffs_weights.append(beta_coeffs)
                elif atlas == 'shen268':
                    cols = range(268)
                    beta_coeffs = get_beta_coefficients(cols, mdl, mdl_label, chaco_type, atlas, x)
                    beta_coeffs_weights.append(beta_coeffs)
                elif atlas == 'fs86subj':
                    cols = range(86)
                    beta_coeffs = get_beta_coefficients(cols, mdl, mdl_label, chaco_type, atlas, x)
                    beta_coeffs_weights.append(beta_coeffs)
            else:
                mdl_label=mdl_label

                beta_coeffs_weights=[]

            # predict scores in the test set
            y_pred= mdl.predict(X_test)
            
            # create filename suffix for saving outputs
            filename =  '{}_{}_{}_{}_{}_crossval{}_perm{}'.format(atlas, y_var, chaco_type, subset, mdl_label,crossval_type,n)

            # sanity check to make sure test subjects != any training subjects
            #np.save(os.path.join(results_path,output_folder, filename + "_train_IDs"), group_train)
            #np.save(os.path.join(results_path,output_folder, filename + "_test_IDs"), group_test)
            
            expl=explained_variance_score(y_test, y_pred)
            correlations[cv_fold] = np_pearson_cor(y_test,y_pred)[0]
            
            print('R^2 score: {} '.format(np.round(explained_variance_score(y_test, y_pred), 3)))
            print('Correlation: {} '.format(np.round(np_pearson_cor(y_test,y_pred)[0][0], 3)))
            explained_var[cv_fold]=expl
            
            if save_models:
                models[cv_fold] = mdl
                
            print('\n')

        print('Mean correlation over all outer folds: {}'.format(np.mean(correlations)[0]))
        print('Mean R^2 over all outer folds: {}'.format(np.mean(explained_var)))

        print('\n\n')
        np.save(os.path.join(results_path, output_folder,filename+ "_scores.npy"), explained_var)
        np.save(os.path.join(results_path,output_folder, filename + "_model.npy"), models)
        np.save(os.path.join(results_path,output_folder, filename+ "_correlations.npy"), correlations)
        np.save(os.path.join(results_path,output_folder, filename + "_beta_coeffs.npy"), beta_coeffs_weights)
        np.save(os.path.join(results_path, output_folder,filename+ "_test_group_sizes.npy"), size_testgroup)


def run_regression_final(x, Y, subIDs, inner_cv_id, outer_cv_id, model_tested, atlas, y_var, chaco_type, subset, save_models,results_path,crossval_type,nperms,null, output_folder, acute_data):
    # Runs only 1 split of 5-fold cross validation, does not estimate performance, returns model with highest out-of-sample accuracy

    X = prepare_data(x) 
    
    if acute_data:
        acute_Y = acute_data['acute_Y']
        acute_subIDs = acute_data['acute_subIDs']
        
        acute_X =acute_data['acute_X']
        acute_X = prepare_data(acute_X) 

    mdl, mdl_label = get_models('regression', model_tested) 

    k_range = determine_featselect_range(X)
    
    
    grid_params ={'ridge__alpha': np.logspace(-2, 2, 30, base=10,dtype=None),
                    'featselect__k':k_range}
    score = 'explained_variance'
    
    inner_cv = create_inner_cv(inner_cv_id,1)
    current_best=0
    for cv_fold, (train_id, test_id) in enumerate(inner_cv.split(X, Y, group)):
        X_train, X_test = X[train_id], X[test_id]
        y_train, y_test = Y[train_id], Y[test_id]

        group_train, group_test = group[train_id], group[test_id]
        X_train = np.concatenate((X_train, acute_X),axis=0)
        y_train = np.concatenate((y_train, acute_Y),axis=0)
        group_train = np.concatenate((group_train, acute_subIDs), axis=0)
        
        best_alpha,best_k, maxexpl= do_grid_search(X_train, X_test, y_train, y_test, mdl, grid_params, score)
        if maxexpl >= current_best:
            best_a = best_alpha
            best_kfeats = best_k
            current_best=maxexpl
    
    print(best_kfeats)
    print(best_a)
    
    model = SelectKBest(score_func=f_regression, k=best_kfeats)
    X_subset = model.fit_transform(X_train, y_train) 
    
    
    feats_selected = model.get_support()
    mdl = Ridge(alpha = best_a, normalize=True, max_iter=1000000, random_state=0)
    mdl.fit(X_subset, y_train)
    
    coeffs = mdl.coef_
    counter=0
    final_beta_coeff_vector=np.empty(shape=(268,1))
    for i in range(0,268):
        if feats_selected[i]==True:
            final_beta_coeff_vector[i]=coeffs[counter]
            counter = counter + 1
        else:
            final_beta_coeff_vector[i]=0
    np.savetxt('/home/ubuntu/enigma/results/analysis_1/final_model_weights_alldata.txt',final_beta_coeff_vector)
    
    #best_mdl = grid_search.best_estimator_
    
def do_grid_search(X_train, X_test, y_train, y_test, mdl, grid_params, score):
    explained_var = np.empty(shape=(30,30))
    
    current_best= 0
    for a, alpha in enumerate(grid_params['ridge__alpha']):
        for b, k in enumerate(grid_params['featselect__k']):
            model = SelectKBest(score_func=f_regression, k=k)
            X_subset = model.fit_transform(X_train, y_train) 
            X_test_subset = model.transform(X_test)
            mdl = Ridge(alpha = alpha, normalize=True, max_iter=1000000, random_state=0)
            y_pred = mdl.fit(X_subset, y_train).predict(X_test_subset)
            expl=explained_variance_score(y_test, y_pred)
            explained_var[a,b]=expl
            
            if expl >=current_best:
                best_alpha = alpha
                best_alpha_idx = a
                best_k = k
                best_k_idx = b
                current_best = expl
    return best_alpha, best_k, np.max(explained_var)



def run_regression_ensemble(X1, C, Y, subIDs, inner_cv_id, outer_cv_id, model_tested, atlas, y_var, chaco_type, subset, save_models,results_path,crossval_type,nperms,null,output_folder, acute_data):
    X2 = C

            
    print('\nRunning ensemble model!')
    if acute_data:
        acute_Y = acute_data['acute_Y']
        if atlas =='lesionload_m1':
            acute_X1 =acute_data['acute_LL']
            acute_X1=np.array(acute_X1).reshape(-1,1)
        elif atlas == 'lesionload_all':
            acute_X1 =acute_data['acute_LL']
            acute_X1=np.array(acute_X1)
        elif atlas == 'lesionload_all_2h' or atlas == 'lesionload_slnm':
            acute_X1 =acute_data['acute_LL']
            acute_X1=np.array(acute_X1)
        else:
            acute_X1 =acute_data['acute_X']
            acute_X1 = prepare_data(acute_X1) 
            
        acute_X2 = acute_data['acute_C']
        print(acute_X2)
            
    if atlas =='lesionload_m1':
        X1=np.array(X1).reshape(-1,1)
    elif atlas == 'lesionload_all':
        X1=np.array(X1)
    elif atlas == 'lesionload_all_2h':
        X1=np.array(X1)
    elif atlas == 'lesionload_slnm':
        X1=np.array(X1)

    else:
        X1 = prepare_data(X1) 

    outer_cv = create_outer_cv(outer_cv_id)

    outer_cv_splits = outer_cv.get_n_splits(X1, Y, subIDs)
    
    models = np.zeros((1, outer_cv_splits), dtype=object)
    explained_var  = np.zeros((1,outer_cv_splits), dtype=object)

    correlations_ensemble  = np.zeros((1,outer_cv_splits), dtype=object)
    mean_abs_error = np.zeros((1,outer_cv_splits), dtype=object)

    size_testgroup =[]
    for n in range(0,nperms):
        print('\n\n~ ~ ~ ~ ~ ~ ~ ~ ~ ~ PERMUTATION: {}/{} ~ ~ ~ ~ ~ ~ ~ ~ ~ \n\n'.format(n, nperms))
        
        for cv_fold, (train_id, test_id) in enumerate(outer_cv.split(X1, Y, subIDs)):
            inner_cv = create_inner_cv(inner_cv_id,n)

            print("------ Outer Fold: {}/{} ------".format(cv_fold + 1, outer_cv_splits))
            
            X1_train, X1_test = X1[train_id], X1[test_id]
            X2_train, X2_test = X2[train_id], X2[test_id]

            y_train, y_test = Y[train_id], Y[test_id]
            group_train, group_test = subIDs[train_id], subIDs[test_id]

            if acute_data:
                print('Acute data incorporated into training set.')
                X1_train = np.concatenate((X1_train, acute_X1),axis=0)
                X2_train = np.concatenate((X2_train, acute_X2),axis=0)

                y_train = np.concatenate((y_train, acute_Y),axis=0)
                group_train = np.concatenate((group_train,acute_Y))
            
            print('Size of test group: {}'.format(group_test.shape[0]))
            print('Size of train group: {}'.format(group_train.shape[0]))
            print('Number of sites in test set: {}\n'.format(np.unique(group_test).shape[0]))            

            size_testgroup.append(group_test.shape[0])
            
            mdl_idx=0
            print(model_tested)
            mdl, mdl_label1 = get_models('regression', model_tested) 
            
            # first model: X1 (lesion data)
            print('~~ Running model 1: lesion info ~~~')
            mdl1 = inner_loop(mdl, mdl_label1, X1_train, y_train, group_train, inner_cv, 10)  
            mdl1.fit(X1_train, y_train)
            y1_pred= mdl1.predict(X1_test)
                
            print('~~ Running model 2: demographics ~~~')
            # second model: demographic data
            mdl, mdl_label = get_models('regression', 'linear_regression')
            mdl = inner_loop(mdl, mdl_label, X2_train, y_train, group_train, inner_cv, 10)
            mdl.fit(X2_train, y_train)
            y2_pred= mdl.predict(X2_test)
        
            
            avg_pred = np.mean([y1_pred, y2_pred], axis=0)
            expl=explained_variance_score(y_test, avg_pred)
            filename = '{}_{}_{}_{}_{}_crossval{}_perm{}_ensemble_demog'.format(atlas, y_var, chaco_type, subset, mdl_label1,crossval_type,n)
            
            correlations_ensemble[mdl_idx, cv_fold] = np_pearson_cor(y_test,avg_pred)[0]
 
            
   
            
            explained_var[mdl_idx, cv_fold] =explained_variance_score(y_test, avg_pred)

            print('\n')
            print('R^2 score (ensemble): {} '.format(np.round(explained_variance_score(y_test, avg_pred), 3)))
            print('Correlation (ensemble): {} '.format(np.round(np_pearson_cor(y_test,avg_pred)[0][0], 3)))
            print('\n')
            print('Corr chaco only: {} '.format(np.round(np_pearson_cor(y_test, y1_pred)[0][0], 3)))
            print('Corr demog only: {} '.format(np.round(np_pearson_cor(y_test, y2_pred)[0][0], 3)))
            print('\n')
            explained_var[mdl_idx, cv_fold]=expl
            if save_models:
                models[mdl_idx, cv_fold] = mdl1
                
            mdl_idx += 1


        if null>0:
            print('NULL!')
            filename = filename + '_null_' + str(null)
        print(filename)
                
        np.save(os.path.join(results_path, output_folder,filename + "_scores.npy"), explained_var)
        np.save(os.path.join(results_path,output_folder, filename + "_model.npy"), models)
        np.save(os.path.join(results_path,output_folder, filename +"_correlations_ensemble.npy"), correlations_ensemble)
        np.save(os.path.join(results_path,output_folder, filename + "_model_labels.npy"), mdl_label)
        np.save(os.path.join(results_path, output_folder,filename + "_test_group_sizes.npy"), size_testgroup)

def run_regression_chaco_ll(X1, X2, Y, subIDs, inner_cv_id, outer_cv_id, model_tested, atlas, y_var, chaco_type, subset, save_models,results_path,crossval_type,nperms,null,output_folder,ensemble_atlas,chaco_model_tested,acute_data):
    print(acute_data)
    if atlas =='lesionload_m1':
        X1=np.array(X1).reshape(-1,1)
    elif atlas == 'lesionload_all':
        X1=np.array(X1)
    elif atlas == 'lesionload_all_2h':
        X1=np.array(X1)
    elif atlas == 'lesionload_slnm':
        X1=np.array(X1) 
    if acute_data:
        acute_Y = acute_data['acute_Y']
        if atlas =='lesionload_m1':
            acute_X1 =acute_data['acute_LL']
            acute_X1=np.array(acute_X1).reshape(-1,1)
        elif atlas == 'lesionload_all':
            acute_X1 =acute_data['acute_LL']
            acute_X1=np.array(acute_X1)
        elif atlas == 'lesionload_all_2h' or atlas == 'lesionload_slnm':
            acute_X1 =acute_data['acute_LL']
            acute_X1=np.array(acute_X1)

        acute_X2 = prepare_data(acute_data['acute_X'])
        
        acute_Y = acute_data['acute_Y']
        
    X2 = prepare_data(X2)
    
    print('\nRunning ensemble model!')
   
    outer_cv = create_outer_cv(outer_cv_id)

    outer_cv_splits = outer_cv.get_n_splits(X1, Y, subIDs)
    
    models = np.zeros((1, outer_cv_splits), dtype=object)
    explained_var  = np.zeros((1,outer_cv_splits), dtype=object)
    variable_importance  = []
    correlations_ensemble  = np.zeros((1,outer_cv_splits), dtype=object)
    mean_abs_error = np.zeros((1,outer_cv_splits), dtype=object)
    size_testgroup =[]
    
    for n in range(0,nperms):
        print('\n\n~ ~ ~ ~ ~ ~ ~ ~ ~ ~ PERMUTATION: {}/{} ~ ~ ~ ~ ~ ~ ~ ~ ~ \n\n'.format(n, nperms))
        
        for cv_fold, (train_id, test_id) in enumerate(outer_cv.split(X1, Y, subIDs)):
            inner_cv = create_inner_cv(inner_cv_id,n)

            print("------ Outer Fold: {}/{} ------".format(cv_fold + 1, outer_cv_splits))
            
            X1_train, X1_test = X1[train_id], X1[test_id]
            X2_train, X2_test = X2[train_id], X2[test_id]
            group_train, group_test = subIDs[train_id], subIDs[test_id]

            y_train, y_test = Y[train_id], Y[test_id]
            if acute_data:
                print('Acute data incorporated into training set.')
                X1_train = np.concatenate((X1_train, acute_X1),axis=0)
                X2_train = np.concatenate((X2_train, acute_X2),axis=0)
                group_train = np.concatenate((group_train,acute_Y), axis=0)
                y_train = np.concatenate((y_train, acute_Y),axis=0)
                
            print(X2_train.shape)

            print('Size of test group: {}'.format(group_test.shape[0]))
            print('Size of train group: {}'.format(group_train.shape[0]))
            print('Number of sites in test set: {}\n'.format(np.unique(group_test).shape[0]))            

            size_testgroup.append(group_test.shape[0])
            
            mdl_idx=0
            mdl, mdl_label1 = get_models('regression', model_tested) 
            
            # first model: X1 (lesion data)
            print('~~ Running model 1: lesion info ~~~')
   
            mdl1 = inner_loop(mdl, mdl_label1, X1_train, y_train, group_train, inner_cv, 10)  
            mdl1.fit(X1_train, y_train)
            y1_pred= mdl1.predict(X1_test)
                
            print('~~ Running model 2: chaco ~~~')
            # second model: X2 (chaco data)
            mdl, mdl_label2 = get_models('regression', chaco_model_tested)
     
            mdl = inner_loop(mdl, mdl_label2, X2_train, y_train, group_train, inner_cv, 10)
            mdl.fit(X2_train, y_train)
            y2_pred= mdl.predict(X2_test)
            
            print(X2.shape[1])
            if X2.shape[1] == 86:
                chacoatlas = 'fs86subj'
            elif X2.shape[1] == 268:
                chacoatlas= 'shen268'
            
            avg_pred = np.mean([y1_pred, y2_pred], axis=0)
            expl=explained_variance_score(y_test, avg_pred)
            filename = '{}_{}_{}_{}_{}_crossval{}_perm{}_ensemble_chacoLL_{}_{}'.format(atlas, y_var, chaco_type, subset, mdl_label1,crossval_type,n, ensemble_atlas,mdl_label2)
            
            #variable_importance.append(mdl.named_steps[mdl_label].coef_)
            correlations_ensemble[mdl_idx, cv_fold] = np_pearson_cor(y_test,avg_pred)[0]

            explained_var[mdl_idx, cv_fold] =explained_variance_score(y_test, avg_pred)

            print('\n')
            print('R^2 score (ensemble): {} '.format(np.round(explained_variance_score(y_test, avg_pred), 3)))
            print('Correlation (ensemble): {} '.format(np.round(np_pearson_cor(y_test,avg_pred)[0][0], 3)))
            print('\n')
            print('Corr lesion only: {} '.format(np.round(np_pearson_cor(y_test, y1_pred)[0][0], 3)))
            print('Corr ChaCo only: {} '.format(np.round(np_pearson_cor(y_test, y2_pred)[0][0], 3)))
            
            print('\n')
            explained_var[mdl_idx, cv_fold]=expl
            if save_models:
                models[mdl_idx, cv_fold] = mdl1
                
            mdl_idx += 1


        if null>0:
            print('NULL!')
            filename = filename + '_null_' + str(null)

        np.save(os.path.join(results_path, output_folder,filename + "_scores.npy"), explained_var)
        np.save(os.path.join(results_path,output_folder, filename + "_model.npy"), models)
        np.save(os.path.join(results_path,output_folder, filename +"_correlations_ensemble.npy"), correlations_ensemble)
        np.save(os.path.join(results_path,output_folder, filename + "_model_labels.npy"), mdl_label1)
        np.save(os.path.join(results_path, output_folder,filename + "_test_group_sizes.npy"), size_testgroup)


def run_regression_chaco_ll_demog(X1, X2, C, Y, subIDs, inner_cv_id, outer_cv_id, model_tested, atlas, y_var, chaco_type, subset, save_models,results_path,crossval_type,nperms,null,output_folder,ensemble_atlas,chaco_model_tested,acute_data):
    
    # X1 = lesion load 
    # X2 = chaco scores
    # X3 = C (demographic)
    if atlas =='lesionload_m1':
        X1=np.array(X1).reshape(-1,1)
    elif atlas == 'lesionload_all':
        X1=np.array(X1)
    elif atlas == 'lesionload_all_2h' or atlas == 'lesionload_slnm':
        X1=np.array(X1)
        
    if acute_data:
        acute_X1 = acute_data['acute_LL']
        if atlas =='lesionload_m1':
            acute_X1=np.array(acute_X1).reshape(-1,1)
        elif atlas == 'lesionload_all':
            acute_X1=np.array(acute_X1)
        elif atlas == 'lesionload_all_2h' or atlas == 'lesionload_slnm':
            acute_X1=np.array(acute_X1)
            
        acute_X2 = prepare_data(acute_data['acute_X'])
        
        acute_Y = acute_data['acute_Y']
    
        acute_C = acute_data['acute_C']
    X2 = prepare_data(X2)
    X3 = C
    
    print('\nRunning ensemble model!')
   
    outer_cv = create_outer_cv(outer_cv_id)

    outer_cv_splits = outer_cv.get_n_splits(X1, Y, subIDs)
    
    models = np.zeros((1, outer_cv_splits), dtype=object)
    explained_var  = np.zeros((1,outer_cv_splits), dtype=object)
    correlations_ensemble  = np.zeros((1,outer_cv_splits), dtype=object)
    mean_abs_error = np.zeros((1,outer_cv_splits), dtype=object)
    size_testgroup =[]
    
    for n in range(0,nperms):
        print('\n\n~ ~ ~ ~ ~ ~ ~ ~ ~ ~ PERMUTATION: {}/{} ~ ~ ~ ~ ~ ~ ~ ~ ~ \n\n'.format(n, nperms))
        
        for cv_fold, (train_id, test_id) in enumerate(outer_cv.split(X1, Y, subIDs)):
            inner_cv = create_inner_cv(inner_cv_id,n)

            print("------ Outer Fold: {}/{} ------".format(cv_fold + 1, outer_cv_splits))
            
            X1_train, X1_test = X1[train_id], X1[test_id]
            X2_train, X2_test = X2[train_id], X2[test_id]
            X3_train, X3_test = X3[train_id], X3[test_id]
            y_train, y_test = Y[train_id], Y[test_id]
            group_train, group_test = subIDs[train_id], subIDs[test_id]

            if acute_data:
                print('Acute data incorporated into training set.')
                X1_train = np.concatenate((X1_train, acute_X1))
                X2_train = np.concatenate((X2_train, acute_X2))
                X3_train = np.concatenate((X3_train, acute_C))
                group_train = np.concatenate((group_train, acute_Y))
                y_train = np.concatenate((y_train, acute_Y))            
                
                
            print(X1_train.shape[0])
            print(X1_train.shape[1])
            print(X2_train.shape[1])
            print('Size of test group: {}'.format(group_test.shape[0]))
            print('Size of train group: {}'.format(group_train.shape[0]))
            print('Number of sites in test set: {}\n'.format(np.unique(group_test).shape[0]))            

            size_testgroup.append(group_test.shape[0])
            
            mdl_idx=0
            mdl, mdl_label = get_models('regression', model_tested) 
                
            # first model: X1 (lesion data)
            print('~~ Running model 1: lesion info ~~~')
            mdl1 = inner_loop(mdl, mdl_label, X1_train, y_train, group_train, inner_cv, 10)  
            mdl1.fit(X1_train, y_train)
            y1_pred= mdl1.predict(X1_test)
                
            print('~~ Running model 2: chaco ~~~')
            # second model: X2 (chaco data)
            mdl, mdl_label2 = get_models('regression', chaco_model_tested)
            mdl = inner_loop(mdl, mdl_label2, X2_train, y_train, group_train, inner_cv, 10)
            mdl.fit(X2_train, y_train)
            y2_pred= mdl.predict(X2_test)
                
            print('~~ Running model 3: demographics ~~~')
            # third model: demographic data
            mdl, mdl_label3 = get_models('regression', 'linear_regression')
            mdl = inner_loop(mdl, mdl_label3, X3_train, y_train, group_train, inner_cv, 10)
            mdl.fit(X3_train, y_train)
            y3_pred= mdl.predict(X3_test)
                   
            if X2.shape[1] == 86:
                chacoatlas = 'fs86subj'
            elif X2.shape[1] == 268:
                chacoatlas= 'shen268'
            
            avg_pred = np.mean([y1_pred, y2_pred, y3_pred], axis=0)
            expl=explained_variance_score(y_test, avg_pred)
            filename = '{}_{}_{}_{}_{}_crossval{}_perm{}_ensemble_chacoLLdemog_{}_{}'.format(atlas, y_var, chaco_type, subset, mdl_label,crossval_type,n, ensemble_atlas,mdl_label2)
 
            #variable_importance.append(mdl.named_steps[mdl_label].coef_)
            correlations_ensemble[mdl_idx, cv_fold] = np_pearson_cor(y_test,avg_pred)[0]

            explained_var[mdl_idx, cv_fold] =explained_variance_score(y_test, avg_pred)

            print('\n')
            print('R^2 score (ensemble): {} '.format(np.round(explained_variance_score(y_test, avg_pred), 3)))
            print('Correlation (ensemble): {} '.format(np.round(np_pearson_cor(y_test,avg_pred)[0][0], 3)))
            print('\n')
            print('Corr lesion only: {} '.format(np.round(np_pearson_cor(y_test, y1_pred)[0][0], 3)))
            print('Corr ChaCo only: {} '.format(np.round(np_pearson_cor(y_test, y2_pred)[0][0], 3)))
            print('Corr demog only: {} '.format(np.round(np_pearson_cor(y_test, y3_pred)[0][0], 3)))
            print('\n')
            
            explained_var[mdl_idx, cv_fold]=expl
            if save_models:
                models[mdl_idx, cv_fold] = mdl1
                
            mdl_idx += 1


        if null>0:
            print('NULL!')
            filename = filename + '_null_' + str(null)


        np.save(os.path.join(results_path, output_folder,filename + "_scores.npy"), explained_var)
        np.save(os.path.join(results_path,output_folder, filename + "_model.npy"), models)
        np.save(os.path.join(results_path,output_folder, filename +"_correlations.npy"), correlations_ensemble)


def set_vars_for_ll(lesionload_type):
    if lesionload_type =='M1':
        atlas = 'lesionload_m1'
        model_tested = 'linear_regression'
        chaco_type = 'NA'
    if lesionload_type =='slnm':
        atlas = 'lesionload_slnm'
        model_tested = 'ridge_nofeatselect'
        chaco_type = 'NA'

    elif lesionload_type =='all':
        atlas = 'lesionload_all'
        model_tested= 'ridge_nofeatselect'
        chaco_type = 'NA'
        
    elif lesionload_type =='all_2h':
        atlas = 'lesionload_all_2h'
        model_tested= 'ridge_nofeatselect'
        chaco_type = 'NA' 
    return atlas, model_tested, chaco_type
        

def set_up_and_run_model(crossval, model_tested,lesionload,lesionload_type, X, Y, C, subIDs, atlas, y_var, chaco_type, subset, save_models, results_path, nperms, null, ensemble, output_folder,ensemble_atlas,chaco_model_tested,acute_data,final_model):
    # This function sets up the parameters for a machine learning model.
    # The function sets up the cross-validation method to be used based on the crossval input. 
    # Finally, it runs a machine learning regression using the specified parameters.
    
    if crossval == '1':
        print('1. Outer CV: Random partition fixed fold sizes, Inner CV: Random partition fixed fold sizes')
        outer_cv_id ='1'
        inner_cv_id = '1'
    elif crossval == '2':
        print('2. Outer CV: Leave-one-site-out, Inner CV: Random partition fixed fold sizes')
        outer_cv_id = '2'
        inner_cv_id ='2'

    elif crossval == '3':
        print('3. Outer CV: Group K-fold, Inner CV: Group K-fold')
        outer_cv_id ='3'
        inner_cv_id = '3'
        
    elif crossval == '4':
        print('4 Outer CV: GroupShuffleSplit, Inner CV:  Random partition fixed fold sizes')
        outer_cv_id = '4'
        inner_cv_id = '4'
        
    elif crossval == '5':
        print('5 Outer CV: GroupShuffleSplit, Inner CV:  GroupShuffleSplit')
        outer_cv_id = '5'
        inner_cv_id = '5'
    
    

    if ensemble == 'none':
        if lesionload_type == 'none':
            kwargs = {'x':X, 'Y':Y, 'subIDs':subIDs, 'model_tested':model_tested, 'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            if final_model=='true':
                print('afdkljasfd')
                run_regression_final(**kwargs)
            else:
               
                run_regression(**kwargs)
            
        elif lesionload_type =='M1':
            atlas = 'lesionload_m1'
            model_tested = 'linear_regression'
            chaco_type ='NA'
            kwargs = {'x':lesionload, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            run_regression(**kwargs)            
        elif lesionload_type =='all':
            atlas = 'lesionload_all'
            model_tested = 'ridge_nofeatselect'
            chaco_type ='NA'
            kwargs = {'x':lesionload, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            run_regression(**kwargs) 
        elif lesionload_type =='all_2h':
            atlas = 'lesionload_all_2h'
            model_tested = 'ridge_nofeatselect'
            chaco_type ='NA'
            kwargs = {'x':lesionload, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            run_regression(**kwargs) 
        elif lesionload_type =='slnm':
            atlas = 'lesionload_slnm'
            model_tested = 'ridge_nofeatselect'
            chaco_type ='NA'
            kwargs = {'x':lesionload, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            run_regression(**kwargs) 
            
    elif ensemble == 'demog':
        print('\n Running ensemble model with demog. \n')

        if lesionload_type == 'none':
            print('running demog')
            kwargs = {'X1':X, 'C':C, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            run_regression_ensemble(**kwargs)            
        elif lesionload_type =='M1':
            atlas = 'lesionload_m1'
            model_tested = 'linear_regression'
            chaco_type = 'NA'
            kwargs = {'X1':lesionload, 'C':C, 'Y':Y, 'subIDs':subIDs, 'model_tested':model_tested, 'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            run_regression_ensemble(**kwargs)
        elif lesionload_type =='all':
            atlas = 'lesionload_all'
            model_tested= 'ridge_nofeatselect'
            chaco_type ='NA'
            kwargs = {'X1':lesionload, 'C':C, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            run_regression_ensemble(**kwargs)
        elif lesionload_type =='all_2h':
            atlas = 'lesionload_all_2h'
            model_tested= 'ridge_nofeatselect'
            chaco_type ='NA'
            kwargs = {'X1':lesionload, 'C':C, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            run_regression_ensemble(**kwargs)
        elif lesionload_type =='slnm':
            atlas = 'lesionload_slnm'
            model_tested= 'ridge_nofeatselect'
            chaco_type ='NA'
            kwargs = {'X1':lesionload, 'C':C, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'acute_data':acute_data}
            run_regression_ensemble(**kwargs)
            
    elif ensemble == 'chaco_ll':
        print('\n Running ensemble model with ChaCo scores AND lesion loads.. \n')
        if lesionload_type =='M1':
            atlas = 'lesionload_m1'
            model_tested = 'linear_regression'
            chaco_type = 'NA'
            kwargs = {'X1':lesionload, 'X2':X, 'Y':Y, 'subIDs':subIDs, 'model_tested':model_tested, 'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'ensemble_atlas':ensemble_atlas, 'chaco_model_tested':chaco_model_tested,'acute_data':acute_data}
            run_regression_chaco_ll(**kwargs)
        elif lesionload_type =='all':
            atlas = 'lesionload_all'
            model_tested= model_tested
            chaco_type ='NA'
            kwargs = {'X1':lesionload, 'X2':X, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'ensemble_atlas':ensemble_atlas, 'chaco_model_tested':chaco_model_tested,'acute_data':acute_data}
            run_regression_chaco_ll(**kwargs)
        elif lesionload_type =='all_2h':
            atlas = 'lesionload_all_2h'
            model_tested= model_tested
            chaco_type ='NA'
            kwargs = {'X1':lesionload, 'X2':X, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'ensemble_atlas':ensemble_atlas, 'chaco_model_tested':chaco_model_tested,'acute_data':acute_data}
            run_regression_chaco_ll(**kwargs)
        elif lesionload_type =='slnm':
            atlas = 'lesionload_slnm'
            model_tested= model_tested
            chaco_type ='NA'
            kwargs = {'X1':lesionload, 'X2':X, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'ensemble_atlas':ensemble_atlas, 'chaco_model_tested':chaco_model_tested,'acute_data':acute_data}
            run_regression_chaco_ll(**kwargs)
            
    elif ensemble == 'chaco_ll_demog':
        print('\n Running ensemble model with ChaCo scores AND lesion loads AND demographics.. \n')
        if lesionload_type =='M1':
            atlas = 'lesionload_m1'
            model_tested = 'linear_regression'
            chaco_type = 'NA'
            kwargs = {'X1':lesionload, 'X2':X, 'C':C, 'Y':Y, 'subIDs':subIDs, 'model_tested':model_tested, 'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'ensemble_atlas':ensemble_atlas, 'chaco_model_tested':chaco_model_tested,'acute_data':acute_data}
            run_regression_chaco_ll_demog(**kwargs)
        elif lesionload_type =='all':
            atlas = 'lesionload_all'
            model_tested= 'ridge_nofeatselect'
            chaco_type ='NA'
            kwargs = {'X1':lesionload, 'X2':X, 'C':C, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'ensemble_atlas':ensemble_atlas, 'chaco_model_tested':chaco_model_tested,'acute_data':acute_data}
            run_regression_chaco_ll_demog(**kwargs)
        elif lesionload_type =='all_2h':
            atlas = 'lesionload_all_2h'
            model_tested= 'ridge_nofeatselect'
            chaco_type ='NA'
            kwargs = {'X1':lesionload, 'X2':X, 'C':C, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'ensemble_atlas':ensemble_atlas, 'chaco_model_tested':chaco_model_tested,'acute_data':acute_data}
            run_regression_chaco_ll_demog(**kwargs)
        elif lesionload_type =='slnm':
            atlas = 'lesionload_slnm'
            model_tested= 'ridge_nofeatselect'
            chaco_type ='NA'
            kwargs = {'X1':lesionload, 'X2':X, 'C':C, 'Y':Y, 'subIDs':subIDs,  'model_tested':model_tested,'inner_cv_id':inner_cv_id, 'outer_cv_id':outer_cv_id, 'atlas':atlas, 'y_var':y_var, 'chaco_type':chaco_type, 'subset':subset,\
                'save_models':save_models, 'results_path':results_path, 'crossval_type':crossval, 'nperms':nperms, 'null':null, 'output_folder':output_folder, 'ensemble_atlas':ensemble_atlas, 'chaco_model_tested':chaco_model_tested,'acute_data':acute_data}
            run_regression_chaco_ll_demog(**kwargs)
          
def save_model_outputs(results_path, output_folder, atlas, y_var, chaco_type, subset, model_tested, crossval, nperms, ensemble,n_outer_folds,ensemble_atlas,chaco_model_tested=None):
    # This function is a helper function for saving the outputs of a machine learning model. It takes a number of 
    # inputs, including results_path, output_folder, atlas, y_var, chaco_type, subset, model_tested, crossval, nperms, and ensemble. 
    # The function then sets up a number of arrays to store the outputs of the model, and then saves those outputs to files in the 
    # specified directory. The function is able to handle saving the outputs of different types of models, such as 
    # those using different atlases, cross-validation methods, and so on.
    
    #print('Saving model outputs to directory: {}'.format(os.path.join(results_path, output_folder)))
    
    mdl_label = model_tested

    rootname = os.path.join(results_path, output_folder,'{}_{}_{}_{}_{}_crossval{}'.format(atlas, y_var, chaco_type, subset, mdl_label,crossval))
    print(rootname)
    r2scores_allperms=np.zeros(shape=(nperms, n_outer_folds))
    correlation_allperms=np.zeros(shape=(nperms, n_outer_folds))
    
    if atlas == 'lesionload_all':
        mean_betas_allperms = np.zeros(shape=(nperms, 6))
        std_betas_allperms = np.zeros(shape=(nperms,6))
        betas_allperms = np.zeros(shape=(nperms,6))
    if atlas == 'lesionload_all_2h':
        mean_betas_allperms = np.zeros(shape=(nperms, 12))
        std_betas_allperms = np.zeros(shape=(nperms,12))
        betas_allperms = np.zeros(shape=(nperms,12))
    if atlas == 'lesionload_slnm':
        varimpts_allperms = np.zeros(shape=(nperms, 5))
        mean_betas_allperms = np.zeros(shape=(nperms, 5))
        std_betas_allperms = np.zeros(shape=(nperms,5))
        betas_allperms = np.zeros(shape=(nperms,5))
    if chaco_type=='chacoconn':
        if atlas == 'fs86subj':
            betas_allperms = np.empty(shape=(0, 86, 86))
        if atlas == 'shen268':
            betas_allperms = np.empty(shape=(0, 268, 268))
    elif chaco_type=='chacovol':
        if atlas == 'fs86subj':
            betas_allperms =np.zeros(shape=(100,5,86))


        if atlas == 'shen268':
            varimpts_allperms = np.empty(shape=(0, 268))
            betas_allperms = np.zeros(shape=(100,5,268))
            betas_allperms2 = np.zeros(shape=(nperms,268))

        
    correlation_allperms=np.zeros(shape=(nperms, n_outer_folds))


    for n in range(0, nperms): #
        # if ensemble model was run, the filename is different because i'm a silly billy. catch it here. 
        # don't care about feature weights for demographic information, and any lesion feature weights are the same as no-ensemble models.
        if ensemble =='demog':
            
            r2scores_ensemble=np.load(rootname +'_perm'+ str(n) + '_ensemble_demog'+ '_scores.npy',allow_pickle=True)
            correlation_ensemble = np.load(rootname +'_perm'+ str(n) + '_ensemble_demog'+ '_correlations_ensemble.npy',allow_pickle=True)
            #varimpts_ensemble=np.load(rootname +'_perm'+ str(n) +  '_ensemble'+ '_activation_weights.npy',allow_pickle=True)
            #mdl=np.load(rootname +'_perm'+ str(n) + '_ensemble'+  '_model.npy',allow_pickle=True)
            r2scores_allperms[n,] = r2scores_ensemble
            correlation_allperms[n,] = correlation_ensemble
            
        if ensemble =='chaco_ll':
            
            r2scores_ensemble=np.load(rootname +'_perm'+ str(n) + '_ensemble_chacoLL_' + ensemble_atlas + '_'+ chaco_model_tested + '_scores.npy',allow_pickle=True)
            correlation_ensemble = np.load(rootname +'_perm'+ str(n) + '_ensemble_chacoLL_' + ensemble_atlas +'_'+ chaco_model_tested + '_correlations_ensemble.npy',allow_pickle=True)
            #varimpts_ensemble=np.load(rootname +'_perm'+ str(n) +  '_ensemble'+ '_activation_weights.npy',allow_pickle=True)
            #mdl=np.load(rootname +'_perm'+ str(n) + '_ensemble'+  '_model.npy',allow_pickle=True)
            r2scores_allperms[n,] = r2scores_ensemble
            correlation_allperms[n,] = correlation_ensemble
        if ensemble =='chaco_ll_demog':
            
            r2scores_ensemble=np.load(rootname +'_perm'+ str(n) + '_ensemble_chacoLLdemog_' + ensemble_atlas + '_'+ chaco_model_tested +'_scores.npy',allow_pickle=True)
            correlation_ensemble = np.load(rootname +'_perm'+ str(n) + '_ensemble_chacoLLdemog_' + ensemble_atlas + '_'+ chaco_model_tested +'_correlations.npy',allow_pickle=True)
            #varimpts_ensemble=np.load(rootname +'_perm'+ str(n) +  '_ensemble'+ '_activation_weights.npy',allow_pickle=True)
            #mdl=np.load(rootname +'_perm'+ str(n) + '_ensemble'+  '_model.npy',allow_pickle=True)
            r2scores_allperms[n,] = r2scores_ensemble
            correlation_allperms[n,] = correlation_ensemble
            
        # no ensemble model.
        if ensemble =='none':
            r2scores=np.load(rootname +'_perm'+ str(n) + '_scores.npy',allow_pickle=True)
            correlation = np.load(rootname +'_perm'+ str(n) +'_correlations.npy',allow_pickle=True)
            betas=np.load(rootname +'_perm'+ str(n) + '_beta_coeffs.npy',allow_pickle=True)
            if atlas == 'lesionload_all' or atlas=='lesionload_all_2h' or atlas =='lesionload_slnm':
                # bc there is no feature selection, we can average the weights of the lesioad load CSTs together together.
                
                mean_betas_allperms[n,]=np.median(betas,axis=0)
                std_betas_allperms[n,]=np.std(betas,axis=0)
                betas_allperms[n,]=np.mean(betas,axis=0)
                
            if atlas == 'fs86subj' or atlas == 'shen268':
                # there is feature selection. so let's concatenate the outer loop features together and only look at features that are included in >50% of the outer folds

                betas_allperms[n,:,:]=betas

            mdl=np.load(rootname +'_perm'+ str(n) + '_model.npy',allow_pickle=True)
            
            r2scores_allperms[n,] = r2scores
            correlation_allperms[n,] = correlation
            
            if mdl_label == 'ridge':
                alphas=[]
                feats=[]
                
                for outer_fold in range(0,5):
                    alphas.append(mdl[outer_fold][mdl_label].alpha)
                    feats.append(mdl[outer_fold]['featselect'].k) 
                    
                np.savetxt(rootname +'_perm'+ str(n)  +'_alphas.txt', alphas)
                np.savetxt(rootname +'_perm'+ str(n)  +'_nfeats.txt', feats)
                
        
    #after data from all permutations collected
    # save the average feature weight from features included in 50%, 90%, or 99% of outer folds.
    if atlas == 'fs86subj' or atlas == 'shen268':
        
        

        n_outer_folds_total = nperms*n_outer_folds # 500 for k=5 and nperm=100
        
        threshold_50 = n_outer_folds_total-n_outer_folds_total/2 # 50%
        threshold_95 = n_outer_folds_total*0.95
        threshold_99 = n_outer_folds_total-n_outer_folds_total/100 # 99%
        threshold_100 = n_outer_folds_total
        
        mean_outer_folds = np.mean(betas_allperms ,axis=1) # 100x268 vector (mean over 5 outer folds)
        if atlas == 'shen268': 
            nonzero_outerfolds = np.count_nonzero(np.reshape(betas_allperms, [500, 268]),axis=0)
            np.save('/home/ubuntu/enigma/results/analysis_1/betas_allperms_shen.npy', betas_allperms)

        elif atlas =='fs86subj':
            nonzero_outerfolds = np.count_nonzero(np.reshape(betas_allperms, [500, 86]),axis=0)
            np.save('/home/ubuntu/enigma/results/analysis_1/betas_allperms_fs.npy', betas_allperms)

    
        
        mean_outer_folds = np.mean(betas_allperms ,axis=1) # 100x268 vector (mean over 5 outer folds)
        median_allpermutations = np.median(mean_outer_folds ,axis=0) # 1 vector (median over 100 perms))
        median_betas_allperms_0 = median_allpermutations
        median_betas_allperms_50 = median_allpermutations*(nonzero_outerfolds > threshold_50)
        median_betas_allperms_95 = median_allpermutations*(nonzero_outerfolds > threshold_95)
        median_betas_allperms_99 = median_allpermutations*(nonzero_outerfolds > threshold_99)
        np.savetxt(rootname +'_median_betas_allperms_0.txt', median_betas_allperms_0)
        np.savetxt(rootname +'_median_betas_allperms_50.txt', median_betas_allperms_50)
        np.savetxt(rootname +'_median_betas_allperms_95.txt', median_betas_allperms_95)
        np.savetxt(rootname +'_median_betas_allperms_99.txt', median_betas_allperms_99)


    if atlas =='lesionload_all' or atlas =='lesionload_all_2h' or atlas == 'lesionload_slnm':
        np.savetxt(rootname +'_meanbetas_allperms.txt', np.median(mean_betas_allperms,axis=0))   
        np.savetxt(rootname +'_stdbetas_allpearms.txt', np.median(std_betas_allperms,axis=0))   
        np.savetxt(rootname +'_betas.txt', betas_allperms)

    np.savetxt(rootname + '_r2_scores.txt', r2scores_allperms)
    np.savetxt(rootname +'_correlations.txt', correlation_allperms)   
          
    return r2scores_allperms, correlation_allperms


def check_if_files_exist(crossval,model_tested,atlas,chaco_type,results_path, ensemble, y_var, subset,ensemble_atlas,chaco_model_tested=None):
    # The function then searches through the specified results_path directory to see if any files with the specified parameters 
    # already exist. If it finds any such files, it returns True and the path to the directory where the files were found. 
    # If no such files are found, it returns False and the results_path directory. 
    
    # This function is used to avoid running the same machine learning model multiple times and overwriting the output files.
    
    # get list of subdirectories:
    subfolders = glob.glob(os.path.join(results_path, 'analysis_*'),recursive = False)
    for folder in subfolders:

        if ensemble == 'demog':
            filename = os.path.join(folder, '{}_{}_{}_{}_{}_crossval{}_perm99_ensemble_demog_scores.npy'.format(atlas, y_var, chaco_type, subset, model_tested,crossval))

            if os.path.exists(filename):
                #print('Files already exist in folder {}!'.format(folder))
                return True, folder
            
        elif ensemble == 'chaco_ll':
            filename = os.path.join(folder, '{}_{}_{}_{}_{}_crossval{}_perm99_ensemble_chacoLL_{}_{}_scores.npy'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, ensemble_atlas,chaco_model_tested))

            if os.path.exists(filename):
                #print('Files already exist in folder {}!'.format(folder))
                return True, folder
            
        elif ensemble == 'chaco_ll_demog':

            filename = os.path.join(folder, '{}_{}_{}_{}_{}_crossval{}_perm99_ensemble_chacoLLdemog_{}_{}_scores.npy'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, ensemble_atlas,chaco_model_tested))

            if os.path.exists(filename):
                #print('Files already exist in folder {}!'.format(folder))
                return True, folder
        else:
            filename = os.path.join(folder, '{}_{}_{}_{}_{}_crossval{}_perm99_beta_coeffs.npy'.format(atlas, y_var, chaco_type, subset, model_tested,crossval))
            
            if os.path.exists(filename):
                #print('File already exists in folder: {}'.format(folder))
                return True, folder 
             
    return False, results_path


def announce_runningmodel(lesionload_type, ensemble, atlas, chaco_type, crossval, override_rerunmodels,chaco_model_tested=None):
    
    print('Running machine learning model: \n')
    print('lesionload type: {}'.format(lesionload_type))
    print('ensemble type: {}'.format(ensemble))
    print('atlas type: {}'.format(atlas))
    print('chacotype: {}'.format(chaco_type))
    print('crossval type: {}'.format(crossval))
    print('override rerunmodels: {}'.format(override_rerunmodels))