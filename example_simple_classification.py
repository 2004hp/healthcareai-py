"""This file is used to create and compare two models on a particular dataset.
It provides examples of reading from both csv and SQL Server. Note that this
example can be run as-is after installing healthcare.ai. After you have
found that one of the models works well on your data, move to Example2
"""
import time
import pandas as pd
from healthcareai.simple_mode import SimpleDevelopSupervisedModel
import healthcareai.common.file_io_utilities as io


def main():
    t0 = time.time()

    # CSV snippet for reading data into dataframe
    dataframe = pd.read_csv('healthcareai/tests/fixtures/DiabetesClincialSampleData.csv', na_values=['None'])

    # Drop columns that won't help machine learning
    dataframe.drop(['PatientID', 'InTestWindowFLG'], axis=1, inplace=True)

    # Look at the first few rows of your dataframe after the data preparation
    print(dataframe.head())

    # Step 1: Setup healthcareai for developing a model. This prepares your data for model building
    hcai = SimpleDevelopSupervisedModel(
        dataframe=dataframe,
        predicted_column='ThirtyDayReadmitFLG',
        model_type='classification',
        grain_column='PatientEncounterID',
        impute=True,
        verbose=False)

    # Step 2: Compare two models

    # Run the KNN model
    # hcai.knn()

    # Run the random forest model
    random_forest = hcai.random_forest()
    print('Model trained in {} seconds\n'.format(time.time() - t0))
    print('type: {}'.format(type(random_forest)))

    # Once you are happy with the result of the trained model, it is time to save the model.
    saved_model_filename = 'random_forest_2017-05-01.pkl'

    # Save the trained model
    random_forest.save(saved_model_filename)

    # TODO swap out fake data for real databaes sql
    prediction_dataframe = pd.read_csv('healthcareai/tests/fixtures/DiabetesClincialSampleData.csv', na_values=['None'])

    # Drop columns that won't help machine learning
    columns_to_remove = ['PatientID', 'InTestWindowFLG']
    prediction_dataframe.drop(columns_to_remove, axis=1, inplace=True)

    # Load the saved model and print out the metrics
    trained_model = io.load_saved_model(saved_model_filename)

    # TODO swap this out for testing
    trained_model = random_forest

    print('\n\n')
    print('Trained Model Loaded\n   Type: {}\n   Model type: {}\n   Metrics: {}'.format(type(trained_model),
                                                                                        type(trained_model.model),
                                                                                        trained_model.metrics()))

    # Make some predictions
    predictions = trained_model.make_predictions(prediction_dataframe)
    print('\n\n-------------------[ Predictions ]----------------------------------------------------\n')
    print(predictions[0:5])

    # Get the important factors
    factors = trained_model.make_factors(prediction_dataframe, number_top_features=1)
    print('\n\n-------------------[ Factors ]----------------------------------------------------\n')
    print(factors.head())
    print(factors.dtypes)

    # Get predictions with factors
    predictions_with_factors_df = trained_model.make_predictions_with_k_factors(prediction_dataframe,
                                                                                number_top_features=1)
    print('\n\n-------------------[ Predictions + factors ]----------------------------------------------------\n')
    print(predictions_with_factors_df.head())
    print(predictions_with_factors_df.dtypes)

    # Get original dataframe with predictions and factors
    original_plus_predictions_and_factors = trained_model.make_original_with_predictions_and_features(
        prediction_dataframe, number_top_features=1)
    print('\n\n-------------------[ Original + predictions + factors ]-------------------------------------------\n')
    print(original_plus_predictions_and_factors.head())
    print(original_plus_predictions_and_factors.dtypes)

    # Get original dataframe with predictions and factors
    # catalyst_dataframe = trained_model.create_catalyst_dataframe(prediction_dataframe)
    # print('\n\n-------------------[ Catalyst SAM ]----------------------------------------------------\n')
    # print(catalyst_dataframe.head())
    # print(catalyst_dataframe.dtypes)

    # Save results to csv
    # predictions.to_csv('foo.csv')

    # Save results to db
    # TODO Save results to db


    # Look at the RF feature importance rankings
    # TODO this is broken
    # hcai.get_advanced_features().plot_rffeature_importance(save=False)

    # Create ROC plot to compare the two models
    # TODO this is broken - it might look like tools.plot_roc(models=[random_forest, linear, knn])
    # hcai.plot_roc()

    # Run 4 built in algorithms to see which one looks best at first
    # TODO ensemble is broken
    # hcai.ensemble()


if __name__ == "__main__":
    main()
