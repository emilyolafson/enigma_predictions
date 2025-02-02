import argparse
from imp import reload
import run_regression_models
reload(run_regression_models)
from run_regression_models import run_models
from helper_functions_figures import *
import pprint

def main(args):
  run_models(**kwargs)
    

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Set up and run machine learning pipeline for lesion biomarker data.")

  # lesionmask_path: str, default ='/home/ubuntu/enigma/lesionmasks/', path to niftis
  #parser.add_argument("--lesionmask_path", default='/home/ubuntu/enigma/lesionmasks/',
  #  help="Absolute path where lesion masks are located, default='/home/ubuntu/enigma/lesionmasks/'")
  
  # nemo_path: str, default ='/home/ubuntu/enigma/lesionmasks/', path to niftis
  parser.add_argument("--nemo_path", default='/home/ubuntu/enigma/lesionmasks/',
    help="Absolute path where NeMo outputs (subjectID_*_mean.pkl files) are located, default='/home/ubuntu/enigma/lesionmasks/', where * is NeMo-generated suffix")
  
  # nemo_path: str, default ='/home/ubuntu/enigma/lesionmasks/', path to nemo outputs
  parser.add_argument("--nemo_settings", default=['1mm','sdstream'],type=lambda s: [item.replace(" ", "") for item in s.split(',')],
    help="Settings used in Network Modification Tool (used to access output files). Default=['1mm','sdstream'], Options: '1mm', '2mm', 'sdstream', 'ifod2act'. Must have resolution 1st and then deterministic/probabilistic choice second.")
  
  # yvar_colname: str, default ='NORMED_MOTOR'', 
  parser.add_argument("--yvar_colname", default='NORMED_MOTOR',
    help="Column name of outcome scores (to be predicted) in .csv file, default='NORMED_MOTOR'")
  
  # subid_colname: str, default ='BIDS_ID'', 
  parser.add_argument("--subid_colname", default='BIDS_ID',
    help="Column name of subject IDs in .csv file, default='BIDS_ID'")
  
  # site_colname: str, default ='SITE'',
  parser.add_argument("--site_colname", default='none',
    help="Column name of the sites variable in .csv file. If subjects are all from the same site, specify 'none' (default). Options: 'site', 'none', 'SITE', etc. default='none'")
  
  # chronicity_colname: str, default ='CHRONICITY'', 
  parser.add_argument("--chronicity_colname", default='none',
    help="Column name of chronicity variable in .csv file. Chronic subjects should have a value of 180, acute subjects should have value 90. If subjects are all of one type, specify 'none' (default). Default='none'")
  
  # csv_path: str, default ='/home/ubuntu/enigma/Behaviour_Information_ALL_April7_2022_sorted_CST_12_ll_slnm.csv', dependent variable in regression models
  parser.add_argument("--csv_path", default='/home/ubuntu/enigma/Behaviour_Information_ALL_April7_2022_sorted_CST_12_ll_slnm.csv',
    help="Absolute path where .csv file containing demographic/outcome scores is stored, default='/home/ubuntu/enigma/Behaviour_Information_ALL_April7_2022_sorted_CST_12_ll_slnm.csv'")
  
  #parser.add_argument("--calculate_lesion_load_only", default=False,help="Whether to calculate lesion load for lesion masks, default=False")
  
  # y_var: str, default ='normed_motor_scores', dependent variable in regression models
  parser.add_argument("--y_var", default='normed_motor_scores',
    help="Dependent variable in regression models (column name in .csv), default='normed_motor_scores'")

  # subsets: str, default = 'chronic', subset of data to use for analysis
  parser.add_argument("--subsets", default=['none'], type=lambda s: [item.replace(" ", "") for item in s.split(',')],
    help="Subset of data to use for analysis, options: 'acute', 'chronic', 'chronic', 'none' default=['chronic']. 'acutechronic' is used to enhance the traning data (but not test data) with acute subjects. ")

  # models_tested: list, default = ['ridge'], machine learning models to run
  parser.add_argument("--models_tested", default=['none'],type=lambda s: [item.replace(" ", "") for item in s.split(',')],
    help="Machine learning model used for ChaCo score-based prediction. Note that models for lesion load predictions are hard-coded. If running only lesion-load based predictions, specify ['none'], Default='none'")

  # verbose: bool, default = True, whether to print out verbose output
  parser.add_argument("--verbose", default=True,type=bool,
    help="Whether to print out verbose output, default=True")
  
  # verbose: generate_figures, default = False, whether to make boxplots
  parser.add_argument("--generate_figures", default=False,
    help=" Whether to make figures/boxplots, default=False")
  
  # covariates: list, default = [], covariates to include in model
  parser.add_argument("--covariates", default=[], type=lambda s: [item.replace(" ", "") for item in s.split(',')],
    help="Covariates to include in model, default=[]")

  # lesionload_types: list, default = [], lesion load types to use
  parser.add_argument("--lesionload_types", default=['none'], type=lambda s: [item.replace(" ", "") for item in s.split(',')],
    help="Lesion load types to use, Options, ['none', 'M1', 'all', 'all_2h'], default=['none]")

  # nperms: int, default = 1, number of permutations to run
  parser.add_argument("--nperms", type=int, default=1,
    help="Number of permutations to run, default=1")

  # save_models: bool, default = True, whether to save trained models
  parser.add_argument("--save_models", default=True,
    help="Whether to save trained models,  default=True")

  # ensembles: list, default = ['none'], what ensemble to run, "demog", "none", "chaco_ll", "chaco_ll_demog"
  parser.add_argument("--ensembles", default=['none'],type=lambda s: [item.replace(" ", "") for item in s.split(',')],
    help="What ensemble to run. Options: 'demog', 'none', 'chaco_ll', 'chaco_ll_demog', \n default=['none']")

  # atlases: list, default = ['fs86subj'], which atlas to use
  parser.add_argument("--atlases", default=['none'], type=lambda s: [item.replace(" ", "") for item in s.split(',')],
    help="Which atlas to use, 'none', 'fs86subj', 'shen268', default=['fs86subj']")

  # chaco_types: list, default = ['chacnoneovol'], regional or pairwise chaco type "chacovol", "chacoconn"
  parser.add_argument("--chaco_types", default=['none'], type=lambda s: [item.replace(" ", "") for item in s.split(',')],
    help="Regional or pairwise chaco type, Options: 'none', 'chacovol', 'chacoconn', default=['none']")

  # crossval_types: list, default = ['1'], which cross-validation scheme to use
  parser.add_argument("--crossval_types", default=['1'], type=lambda s: [item.replace(" ", "") for item in s.split(',')],
    help="Which cross-validation scheme to use, Options = ['1', '2', '3', '4', '6'], default=['1']")
  
  # null: int, default= -1, value to use for null entries in data
  parser.add_argument("--null", default=-1,
    help="Value to use for null entries in data, default=-1 (no null model)")
  
  # results_path: str, default = '/ubuntu/home/enigma/results/', where to save results
  parser.add_argument("--results_path", default='/home/ubuntu/enigma/results',
    help="Absolute path to save results (model outputs in .npy format), default='/home/ubuntu/enigma/results'")
  
  # output_folder: str, default = '/analysis_1', where to save files (npy, not figures)
  parser.add_argument("--output_folder", default='analysis_1',
    help="Directory below results_path to save outputs, for multiple analyses, default='/analysis_1'")
  
  # figs_only: bool, default = False, whether to only save figures, without data
  parser.add_argument("--figs_only", default=False,
    help="Whether to only save figures, without running models, default=False")
  
  # fig_path=: str, default = 'fig_path==', identifier for analysis
  parser.add_argument("--fig_path", default='analysis_1',
    help="Saves figures to this directory, default='fig_path'")
  
  # workbench_vis: bool, default = False, whether to generate visualizations using Workbench
  parser.add_argument("--workbench_vis", default=False,
    help="Whether to generate visualizations using Workbench, default=False")
  
  # scenesdir: str, default = '/wb_files', directory where Workbench scenes are saved
  parser.add_argument("--scenesdir", default='/home/ubuntu/enigma/motor_predictions/wb_files',
    help="If generating Workbench visualizations: directory where Workbench scenes are saved and where atlas parcellation files are stored, default='/home/ubuntu/enigma/motor_predictions/wb_files'")
  
  parser.add_argument("--hcp_dir", default= '/home/ubuntu/enigma/motor_predictions/wb_files/HCP_S1200_GroupAvg_v1',
    help="If generating Workbench visualizations: directory where HCP defaults are stored (i.e. midthickness gii files), default='/home/ubuntu/enigma/motor_predictions/wb_files/HCP_S1200_GroupAvg_v1'")
  
  # wbpath: str, default = '/workbench/bin_linux64/wb_command', 
  parser.add_argument("--wbpath", default='/home/ubuntu/enigma/motor_predictions/wb_files/workbench_ubuntu/bin_linux64',
    help="If generating Workbench visualizations: path to Workbench command-line interface, default='/home/ubuntu/enigma/motor_predictions/wb_files/workbench/bin_linux64'")
  
  # boxplots: bool, default = True, whether to generate boxplots of results
  parser.add_argument("--boxplots", default=False,
    help="Whether to generate boxplots of results, default=False")
  
  # ensemble_atlas: bool, default = 'fs86subj',Which ChaCo atlas to use, if running ensemble models with lesion data + ChaCo score
  parser.add_argument("--ensemble_atlas", default='none',
    help="Which ChaCo atlas to use, if running ensemble models with lesion data + ChaCo scores, options 'none','fs86subj', 'shen268', default='fs86subj")
  
  # override_rerunmodels: bool, default = False, whether to re-run models even if already run with same parameters
  parser.add_argument("--override_rerunmodels", default=False,
    help="Whether to re-run models even if already run with same parameters, default=False") 
  
  #final modle
  parser.add_argument("--final_model", default='false',
    help="Run a single 5-fold cross-validation and return the final model with its selected features.") 
  
      
  args = parser.parse_args()
    # check that parameters make sense.
  model_options= ['none', 'ridge', 'lasso', 'elastic_net', 'ridge_nofeatselect', 'linear_regression', 'svm', 'svr', 'ensemble_reg']
  if not set(args.models_tested).issubset(set(model_options)):
      raise RuntimeError('Warning! Unknown model option specified {} \n Only the following options are allowed {} \n'.format(args.models_tested, model_options))

  lesionload_options = ['M1', 'none', 'all', 'all_2h', 'slnm']
  if not set(args.lesionload_types).issubset(set(lesionload_options)):
      raise RuntimeError('Warning! Unknown lesion load type specified: {}\n Only the following options are allowed: {} \n'.format(args.lesionload_types, lesionload_options))

  ensemble_options =['none', 'demog', 'chaco_ll', 'chaco_ll_demog']
  if not set(args.ensembles).issubset(set(ensemble_options)):
      raise RuntimeError('Warning! Unknown ensemble type specified: {}\n Only the following options are allowed: {} \n'.format(args.ensembles, ensemble_options))

  atlas_options = ['none', 'fs86subj', 'shen268']
  if not set(args.atlases).issubset(set(atlas_options)):
      raise RuntimeError('Warning! Unknown atlas type specified: {}\n Only the following options are allowed: {} \n'.format(args.atlases, atlas_options))

  chaco_options = ['none', 'chacovol', 'chacoconn']
  if not set(args.chaco_types).issubset(set(chaco_options)):
      raise RuntimeError('Warning! Unknown atlas type specified: {}\n Only the following options are allowed: {} \n'.format(args.chaco_types, chaco_options))

  crossval_options = ['1', '2', '3', '4', '5']
  if not set(args.crossval_types).issubset(set(crossval_options)):
      raise RuntimeError('Warning! Unknown cross validation type specified: {}\n Only the following options are allowed: {} \n'.format(args.crossval_types, crossval_options))    

  if os.path.exists(os.path.join(args.results_path, args.output_folder)):
      print('Path {} exists. Potentially overwriting files.'.format(os.path.join(args.results_path, args.output_folder)))
  else:
      print('Path {} does not exist. Creating it now.'.format(os.path.join(args.results_path, args.output_folder)))
      os.makedirs(os.path.join(args.results_path, args.output_folder))

  if not os.path.exists(args.csv_path):
      raise RuntimeError('Warning! File {} does not exist or the path is not correctly specified.'.format(args.csv_path))
  
  nemo_settings_options = ['1mm', '2mm', 'sdstream', 'ifod2act']
  if not set(args.nemo_settings).issubset(set(nemo_settings_options)):
      raise RuntimeError('Warning! Unknown cross validation type specified: {}\n Only the following options are allowed: {} \n'.format(args.nemo_settings, nemo_settings_options))    

  if (not args.lesionload_types == ['none']) and (not args.atlases == ['none']) and (not args.chaco_types == ['none']):
      # if you specified running a lesion load model AND a chaco model but you only specified the parameters for both (not 'none' options)
      args.lesionload_types.append('none')
  
  if ('chacovol' in args.chaco_types ) and (not args.models_tested):
      raise RuntimeError('Error: please specify a machine learning model to use for ChaCo predictions.')
  
  if isinstance(args.override_rerunmodels, str):
    # anything else I'm assuming you meant false.
    args.override_rerunmodels = (args.override_rerunmodels =='True') or (args.override_rerunmodels == 'true') or (args.override_rerunmodels == 'T') or (args.override_rerunmodels == '1')
  
  if isinstance(args.figs_only, str):
    # anything else I'm assuming you meant false.
    args.figs_only = (args.figs_only =='True') or (args.figs_only == 'true') or (args.figs_only == 'T') or (args.figs_only == '1')
    
  if isinstance(args.generate_figures, str):
    # anything else I'm assuming you meant false.
    args.generate_figures = (args.generate_figures =='True') or (args.generate_figures == 'true') or (args.generate_figures == 'T') or (args.generate_figures == '1')
    
  if isinstance(args.override_rerunmodels, str):
    # anything else I'm assuming you meant false.
    args.override_rerunmodels = (args.override_rerunmodels =='True') or (args.override_rerunmodels == 'true') or (args.override_rerunmodels == 'T') or (args.override_rerunmodels == '1')
  
  if not isinstance(args.chronicity_colname,str):
    args.chronicity_colname = 'none'
  
  if ('chacovol' in args.chaco_types) and ('none' in args.atlases):
    raise RuntimeError('No atlas specified for ChaCo model. Either specify at atlas, or do not specify a ChaCo model (chaco_types = "none")')
  #if not os.path.exists(args.lesionmask_path):
  #    raise RuntimeError('Warning! Path {} does not exist.'.format(args.lesionmask_path))

  kwargs = vars(args)
  pprint.pprint(kwargs)
  print('precall')
  print(args.generate_figures)
    
  main(args)