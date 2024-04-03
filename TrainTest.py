import xgboost as xgb
from sklearn.metrics import confusion_matrix, matthews_corrcoef, classification_report, roc_auc_score, precision_recall_curve, auc
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import joblib
import os
import numpy as np



def run_xgboost_classification_v2(cartesian_similarity_df, test_mark=None, include_all_for_train_test=False, result_path = 'test_result'):
    """
    Trains and evaluates an XGBoost model on specified subsets of the dataframe.

    Args:
        cartesian_similarity_df (pd.DataFrame): The dataframe containing the data.
        train_marks (list): A list of 'Mark' values to include in the training set.
        test_mark (str): The 'Mark' value to use for the test set.
        result_path (str): Directory path to save the evaluation results and plots.
    """
    # Ensure required directories exist
    os.makedirs(result_path, exist_ok=True)
    
    # Split the dataset
    if include_all_for_train_test:
        # Use all data for both training and testing
        X = cartesian_similarity_df.select_dtypes(exclude=['object', 'string']).drop(columns=['Class', 'Mark', 'DOBSimilarity', 'strAddressSimilarity'], errors='ignore')
        y = cartesian_similarity_df['Class']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    else:
        # Split the dataset based on test_mark
        test_df = cartesian_similarity_df[cartesian_similarity_df['StandardizedMark'] == test_mark]
        train_df = cartesian_similarity_df[cartesian_similarity_df['StandardizedMark'] != test_mark]
        
        X_train = train_df.select_dtypes(exclude=['object', 'string']).drop(columns=['Class', 'Mark', 'DOBSimilarity', 'strAddressSimilarity'], errors='ignore')
        y_train = train_df['Class']
        X_test = test_df.select_dtypes(exclude=['object', 'string']).drop(columns=['Class', 'Mark', 'DOBSimilarity', 'strAddressSimilarity'], errors='ignore')
        y_test = test_df['Class']
    
    # Initialize and fit the model
    print('Len X_train:', len(X_train), 'Len X_test:', len(X_test), 'Len y_test:', len(y_test), 'Test mark:', test_mark)
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    print("Unique values in y_test:", np.unique(y_test), test_mark)
    print("Unique values in y_pred:", np.unique(y_pred), test_mark)
    mcc = matthews_corrcoef(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    precision, recall, thresholds = precision_recall_curve(y_test, model.predict_proba(X_test)[:, 1])
    pr_auc = auc(recall, precision)
    
    # Save evaluation metrics and figures
    save_evaluation_results(mcc, y_test, y_pred, roc_auc, precision, recall, pr_auc, cm, model, test_mark, result_path)
    # metrics_df = pd.DataFrame(columns=['Test Mark', 'MCC', 'ROC-AUC', 'Precision', 'Recall', 'PR-AUC'])


    # metrics_dict = {
    #     'Test Mark': test_mark,
    #     'MCC': mcc,
    #     'ROC-AUC': roc_auc,
    #     'Precison': precision,
    #     'recall': recall,
    #     'Precision-Recall AUC': pr_auc
    #     # Add other metrics you're interested in
    # }

        # After model evaluation, save the model
    model_filename = f'test_result/{result_path}/{test_mark}_xgboost_model.joblib'
    joblib.dump(model, model_filename)

    return test_mark, mcc, roc_auc, precision, recall, pr_auc

def save_evaluation_results(mcc, y_test, y_pred, roc_auc, precision, recall, pr_auc, cm, model, test_mark, result_path):
    """
    Utility function to save the evaluation results and plots.
    
    Args:
        mcc (float): Matthews Correlation Coefficient.
        y_test (pd.Series): Actual target values.
        y_pred (np.array): Predicted target values.
        roc_auc (float): ROC-AUC Score.
        precision (np.array): Precision for each threshold.
        recall (np.array): Recall for each threshold.
        pr_auc (float): Precision-Recall AUC.
        cm (np.array): Confusion matrix.
        model (xgboost.XGBClassifier): Trained XGBoost model.
        test_mark (str): The 'Mark' value used for the test set.
        result_path (str): Base directory path to save the evaluation results and plots.
    """
    # Ensure the specified directory exists
    os.makedirs(f'test_result/{result_path}', exist_ok=True)

    with open(f'test_result/{result_path}/{test_mark}_model_evaluation_results.txt', 'w') as f:
        f.write(f"Matthews Correlation Coefficient: {mcc}\n\n")
        f.write(f"Classification Report:\n{classification_report(y_test, y_pred)}\n\n")
        f.write(f"ROC-AUC Score: {roc_auc}\n\n")
        f.write(f"Precision-Recall AUC: {pr_auc}\n")

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted Labels')
    plt.ylabel('True Labels')
    plt.savefig(f'test_result/{result_path}/{test_mark}_confusion_matrix.png')
    plt.close()

    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, marker='.', label='Precision-Recall Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend()
    plt.title('Precision-Recall Curve')
    plt.savefig(f'test_result/{result_path}/{test_mark}_precision_recall_curve.png')
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 8))
    xgb.plot_importance(model, ax=ax, importance_type='gain', show_values=True, title='Feature Importance')
    fig.savefig(f'test_result/{result_path}/{test_mark}_feature_importance.png')
    plt.close()


# Example usage:
# cartesian_similarity_df = pd.read_csv('path_to_your_dataframe.csv')
# test_mark = ['Obs1-Obs2', 'Obs1-Obs3', 'Obs2-Obs3', 'Obs2-Original', 'Obs3-Original', 'Obs1-Original', 'Original-Original']

# test_marks = ['Obs1-Obs2', 'Obs1-Obs3', 'Obs2-Obs3', 'Obs2-Original', 'Obs3-Original', 'Obs1-Original', 'Original-Original', 'All-Data']
# for mark in test_marks:
#     if mark == 'All-Data':
#         # When we want to use the entire dataset for both training and testing
#         run_xgboost_classification_v2(cartesian_similarity_df, include_all_for_train_test=True, result_path='test_result_all_data')
#     else:
#         # For specific mark-based splits
#         result_folder = f'test_result_{mark}'  # Creates a separate folder for each test mark
#         run_xgboost_classification_v2(cartesian_similarity_df, test_mark=mark, result_path=result_folder)

