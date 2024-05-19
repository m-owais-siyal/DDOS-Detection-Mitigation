import joblib
from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import FeatureHasher
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.preprocessing import FunctionTransformer

from list_converter import ListConverter

class MachineLearning():
    def __init__(self):
        print("Loading dataset ...")
        self.flow_dataset = pd.read_csv('FlowStatsfile.csv')
        self.flow_dataset.iloc[:, 2] = self.flow_dataset.iloc[:, 2].str.replace('.', '')
        self.flow_dataset.iloc[:, 3] = self.flow_dataset.iloc[:, 3].str.replace('.', '')
        self.flow_dataset.iloc[:, 5] = self.flow_dataset.iloc[:, 5].str.replace('.', '')

    def flow_training(self):
        print("Flow Training ...")

        X_flow = self.flow_dataset.iloc[:, :-1]
        y_flow = self.flow_dataset.iloc[:, -1]

        X_flow_train, X_flow_test, y_flow_train, y_flow_test = train_test_split(
            X_flow, y_flow, test_size=0.25, random_state=0
        )

        # Preprocess categorical and numerical features separately
        categorical_features = ['flow_id', 'ip_src', 'ip_dst']
        numerical_features = list(set(X_flow.columns) - set(categorical_features))

        # Create pipeline for numerical features
        numerical_pipeline = Pipeline([
            ('scaler', StandardScaler())
        ])
        
        list_converter = ListConverter()
        categorical_pipeline = Pipeline([
            ('list_converter', FunctionTransformer(list_converter.transform, validate=False)),
            ('encoder', FeatureHasher(n_features=10, input_type='string'))
        ])

        # Combine both pipelines using ColumnTransformer
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_pipeline, numerical_features),
                ('cat', categorical_pipeline, categorical_features)
            ]
        )

        # Create final pipeline with Naive Bayes classifier
        classifier = GaussianNB()
        flow_model = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', classifier)
        ])

        flow_model.fit(X_flow_train, y_flow_train)

        y_flow_pred = flow_model.predict(X_flow_test)

        print("------------------------------------------------------------------------------")

        print("confusion matrix")
        cm = confusion_matrix(y_flow_test, y_flow_pred)
        print(cm)

        acc = accuracy_score(y_flow_test, y_flow_pred)

        print("success accuracy = {0:.2f} %".format(acc * 100))
        fail = 1.0 - acc
        print("fail accuracy = {0:.2f} %".format(fail * 100))
        print("------------------------------------------------------------------------------")

        x = ['TP', 'FP', 'FN', 'TN']
        plt.title("Naive Bayes")
        plt.xlabel('Classe predite')
        plt.ylabel('Nombre de flux')
        plt.tight_layout()
        plt.style.use("seaborn-darkgrid")
        y = [cm[0][0], cm[0][1], cm[1][0], cm[1][1]]
        plt.bar(x, y, color="#0000ff", label='NB')
        plt.legend()

        # Save the plot to a file
        plot_filename = 'naive_bayes_plot.png'
        plt.savefig(plot_filename)
        #print(f"Plot saved to {plot_filename}")

        # Do not display the plot
        # plt.show()

        return flow_model

def main():
    start = datetime.now()
    
    ml = MachineLearning()
    trained_model = ml.flow_training()

    model_filename = 'naive_bayes_model.joblib'
    joblib.dump(trained_model, model_filename)
   # print(f"Trained model saved to {model_filename}")
    print("Trained model saved to {}".format(model_filename))


    end = datetime.now()
    print("Training time: ", (end - start)) 

if __name__ == "__main__":
    main()

