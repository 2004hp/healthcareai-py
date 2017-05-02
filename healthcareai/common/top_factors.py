import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression

from healthcareai.common.file_io_utilities import save_object_as_pickle
from healthcareai.common.healthcareai_error import HealthcareAIError


def top_cols(row):
    """
    Sorts (descending) the columns of a dataframe by value or a single row
    :param row: a row of a pandas data frame
    :return: an array of column names
    """
    return row.sort_values(ascending=False).index.values


def top_k_features(dataframe, linear_model, k=3):
    """
    Get lists of top features based on an already-fit linear model

    Args:
        dataframe (pandas.core.frame.DataFrame): The dataframe for which to score top features 
        linear_model (sklearn.base.BaseEstimator): A pre-fit scikit learn model instance that has linear coefficients.
        k (int): k lists of top features (the first list is the top features, the second list are the #2 features, etc)

    Returns:
        pandas.core.frame.DataFrame: The top features for each row in dataframe format 

    """
    # Basic validation for number of features vs column count
    max_model_features = len(linear_model.coef_)
    if k > max_model_features:
        raise HealthcareAIError('You requested {} top features, which is more than the {} features from the original'
                                ' model. Please choose {} or less.'.format(k, max_model_features, max_model_features))

    # Multiply the values with the coefficients from the trained model
    step1 = pd.DataFrame(dataframe.values * linear_model.coef_, columns=dataframe.columns)
    step2 = step1.apply(top_cols, axis=1)

    results = list(step2.values[:, :k])
    return results


def prepare_fit_model_for_factors(model_type, x_train, y_train):
    """
    Given a model type, train and test data
    Args:
        model_type:
        x_train:
        y_train:

    Returns:
        A fit model. Also saves it as a pickle file.
    """

    if model_type == 'classification':
        algorithm = LogisticRegression()
    elif model_type == 'regression':
        algorithm = LinearRegression()
    else:
        algorithm = None

    if algorithm is not None:
        algorithm.fit(x_train, y_train)
        save_object_as_pickle('factorlogit.pkl', algorithm)

    return algorithm


def find_top_three_factors(trained_model, x_test, debug=False):
    # TODO deprecate this once get_top_k_factors is complete
    """
    Given a trained model and an x_test set, reverse engineer the top three feature importances
    Args:
        trained_model:
        x_test:
        debug:

    Returns:
        A tuple of the top three factors
    """
    # Populate X_test array of ordered column importance;
    # Start by multiplying X_test values by coefficients
    multiplied_factors = x_test.values * trained_model.coef_
    feature_columns = x_test.columns.values

    # initialize the empty factors
    first_factor = []
    second_factor = []
    third_factor = []

    # TODO: switch 2-d lists to numpy array
    # (although would always convert back to list for ceODBC/PyODBC/whatever db
    for i in range(0, len(multiplied_factors[:, 1])):
        list_of_index_rankings = np.array((-multiplied_factors[i]).argsort().ravel())
        first_factor.append(feature_columns[list_of_index_rankings[0]])
        second_factor.append(feature_columns[list_of_index_rankings[1]])
        third_factor.append(feature_columns[list_of_index_rankings[2]])

    if debug:
        print('Coefficients before multiplication to determine top 3 factors')
        print(trained_model.coef_)
        print('X_test before multiplication')
        print(x_test.loc[:3, :])
        print_multiplied_factors(multiplied_factors)
        print_top_factors(first_factor, second_factor, third_factor, 5)

    return first_factor, second_factor, third_factor


def print_multiplied_factors(multiplied_factors):
    # TODO deprecate this once get_top_k_factors is complete
    """ Given a set of multiplied factors, unwrap and print them """
    print('Multilplied factors:')
    for i in range(0, 3):
        print(multiplied_factors[i, :])


def print_top_factors(first_factor, second_factor, third_factor, number_to_print):
    # TODO deprecate this once get_top_k_factors is complete
    """Given factors, unwrap and print them nicely"""
    print('Top three factors for top {} rows:'.format(number_to_print))
    # pretty-print using a dataframe
    print(pd.DataFrame({
        'first': first_factor[:number_to_print],
        'second': second_factor[:number_to_print],
        'third': third_factor[:number_to_print]}))


def write_feature_importances(importance_attr, col_list):
    """
    This function prints an ordered list of rf-related feature importance.

    Parameters
    ----------
    importance_attr (attribute) : This is the feature importance atribute
    from a scikit-learn method that represents feature importances
    col_list (list) : Vector holding list of column names

    Returns
    -------
    Nothing. Simply prints feature importance list to console.
    """
    indices = np.argsort(importance_attr)[::-1]
    print('\nVariable importance:')

    for f in range(0, len(col_list)):
        print("%d. %s (%f)" % (f + 1, col_list[indices[f]], importance_attr[indices[f]]))


if __name__ == "__main__":
    pass
