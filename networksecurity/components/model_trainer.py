import os
import sys
import dagshub
import mlflow
from urllib.parse import urlparse
from networksecurity.logging.logger import logging
from sklearn.metrics import f1_score,precision_score,recall_score
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.utils.main_utils.utils import save_object, load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.artifact_entity import ClassificationMetricArtifact 
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from mlflow.models.signature import infer_signature

# Initialize DagsHub
# dagshub.init(repo_owner='Sookchand', repo_name='Network_Security', mlflow=True)
#
dagshub.init(repo_owner='Sookchand', repo_name='Net_Security', mlflow=True) 


# dagshub.init(repo_owner='Sookchand', repo_name='Network_Security', mlflow=True)

# os.environ["MLFLOW_TRACKING_URI"]="https://dagshub.com/Sookchand/Network_Security.mlflow"
# os.environ["MLFLOW_TRACKING_USERNAME"]="Sookchand"
# os.environ["MLFLOW_TRACKING_PASSWORD"]="5fffcc6146291772ba8e06efd88b25d685ddc25a"

# print(os.environ.get("MLFLOW_TRACKING_URI"))
# print(os.environ.get("MLFLOW_TRACKING_USERNAME"))
# print(os.environ.get("MLFLOW_TRACKING_PASSWORD"))

# Set DagsHub tracking URI
# mlflow.set_tracking_uri("https://dagshub.com/Sookchand/Network_Security.mlflow")  # Use DagsHub URI
# mlflow.set_experiment("network_security_experiment")  # Explicitly set experiment name

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            logging.info("Initializing ModelTrainer...")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
            logging.info("ModelTrainer initialized successfully.")
        except Exception as e:
            logging.error(f"Error occurred during ModelTrainer initialization: {e}")
            raise NetworkSecurityException(e, sys)
        
    def track_mlflow(self, best_model, classificationmetric):
        """
        Logs metrics, model, and artifacts to MLflow.
        """
        try:
            with mlflow.start_run():
                f1_score= classificationmetric.f1_score
                precision_score=classificationmetric.precision_score
                recall_score=classificationmetric.recall_score
                
                # Log metrics to MLflow
                mlflow.log_metric("f1_score",f1_score)
                mlflow.log_metric("precision",precision_score)
                mlflow.log_metric("recall_score",recall_score)
                mlflow.sklearn.log_model(best_model,"model")

               # Model registry does not work with file store
                # if tracking_url_type_store != "file":

                #     # Register the model
                #     # There are other ways to use the Model Registry, which depends on the use case,
                #     # please refer to the doc for more information:
                #     # https://mlflow.org/docs/latest/model-registry.html#api-workflow
                #     mlflow.sklearn.log_model(best_model, "model", registered_model_name=best_model)
                # else:
                #     mlflow.sklearn.log_model(best_model, "model")


                # Log the preprocessor as an artifact
                mlflow.log_artifact(self.data_transformation_artifact.transformed_object_file_path, artifact_path="preprocessor")
        except Exception as e:
            logging.error(f"Error during MLflow tracking: {e}")
            raise NetworkSecurityException(e, sys)

    
    def train_model(self, x_train, y_train, x_test, y_test):
        logging.info("Starting model training process...")
        models = {
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier(),
        }
        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy', 'log_loss'],
            },
            "Random Forest": {
                'n_estimators': [8, 16, 32, 128, 256],
            },
            "Gradient Boosting": {
                'learning_rate': [.1, .01, .05, .001],
                'subsample': [0.6, 0.7, 0.75, 0.85, 0.9],
                'n_estimators': [8, 16, 32, 64, 128, 256],
            },
            "Logistic Regression": {},
            "AdaBoost": {
                'learning_rate': [.1, .01, .001],
                'n_estimators': [8, 16, 32, 64, 128, 256],
            }
        }

        try:
            logging.info("Evaluating models with provided training and test data...")
            model_report: dict = evaluate_models(
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
                y_test=y_test,
                models=models,
                param=params
            )
            logging.info(f"Model evaluation completed successfully. Report: {model_report}")

            # Get the best model name and score
            best_model_score = max(model_report.values())
            best_model_name = max(model_report, key=model_report.get)
            logging.info(f"Best model selected: {best_model_name} with score {best_model_score}")
            best_model = models[best_model_name]

            # Train the best model
            logging.info(f"Training best model: {best_model_name}...")
            best_model.fit(x_train, y_train)
            logging.info(f"Model {best_model_name} trained successfully.")

            # Evaluate on training and test data
            y_train_pred = best_model.predict(x_train)
            classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)
            logging.info(f"Training metrics: {classification_train_metric}")
            
            ## Track the experiements with mlflow
            self.track_mlflow(best_model, classification_train_metric) # Output: None

            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)
            logging.info(f"Training metrics: {classification_train_metric}")
            logging.info(f"Test metrics: {classification_test_metric}")

            ## Track the experiements with mlflow
            self.track_mlflow(best_model, classification_test_metric) # Output: None

            # Save the model and preprocessor
            logging.info("Loading preprocessor object...")
            preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)

            logging.info("Saving trained model and preprocessor object...")
            Network_Model = NetworkModel(preprocessor=preprocessor, model=best_model)
            save_object(self.model_trainer_config.trained_model_file_path, obj=Network_Model)
            logging.info("Model and preprocessor saved successfully.")

            # Save the best model to a specific directory - you can push this model into s3 biucket, etc from here
            logging.info("Saving the best model to final_model directory...")   
            save_object("final_model/model.pkl", best_model)  # Save the final model
            logging.info("Final model saved successfully.")
            # Save the model to a specific directory - you can push this model into s3 bucket, etc from here
            save_object("final_model/model.pkl",best_model)
            logging.info("Final model saved successfully.")
                        
            # Model Trainer Artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                trained_metric_artifact=classification_train_metric,  # Updated parameter
                test_metric_artifact=classification_test_metric      # Updated parameter
            )
            logging.info(f"Model Trainer Artifact created: {model_trainer_artifact}")
            return model_trainer_artifact

        except Exception as e:
            logging.error(f"Error occurred during model training: {e}")
            raise NetworkSecurityException(e, sys)

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        logging.info("Initiating model trainer...")
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            logging.info("Loading training and test data arrays...")
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1]
            )
            logging.info("Training and test data loaded successfully.")

            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            logging.info("Model training completed successfully.")
            return model_trainer_artifact

        except Exception as e:
            logging.error(f"Error occurred during model trainer initiation: {e}")
            raise NetworkSecurityException(e, sys)
