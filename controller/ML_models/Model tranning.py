import time
import psutil
import tracemalloc
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, confusion_matrix
import pandas as pd
import numpy as np
import joblib

def train_and_save_model():
    print("Flow Training ...")

    tracemalloc.start()  # Start memory allocation tracking
    start_time = time.time()  # Start time tracking
    process = psutil.Process()  # Get current process for CPU and memory usage

    # Load the dataset
    flow_dataset = pd.read_csv('data1.csv')
    flow_dataset.dropna(inplace=True)
    flow_dataset.replace([np.inf, -np.inf], np.nan, inplace=True)
    flow_dataset.dropna(inplace=True)
    flow_dataset.iloc[:, 1:5] = flow_dataset.iloc[:, 1:5].replace('\.', '', regex=True).astype(float)

    X_flow = flow_dataset.iloc[:, :-1].values
    y_flow = flow_dataset.iloc[:, -1].values

    constant_filter = VarianceThreshold()
    X_flow_filtered = constant_filter.fit_transform(X_flow)

    selector = SelectKBest(score_func=f_classif, k=15)
    X_flow_selected = selector.fit_transform(X_flow_filtered, y_flow)
    selected_indices = selector.get_support(indices=True)
    selected_headers = flow_dataset.columns[selected_indices]

    if 'label' not in selected_headers:
        selected_headers = np.append(selected_headers, 'label')

    print("Top 15 Selected Features:")
    print(selected_headers)

    X_flow_train, X_flow_test, y_flow_train, y_flow_test = train_test_split(X_flow_selected, y_flow, test_size=0.25, random_state=0)
    scaler = StandardScaler()
    X_flow_train_scaled = scaler.fit_transform(X_flow_train)
    X_flow_test_scaled = scaler.transform(X_flow_test)

    classifier = GaussianNB()
    flow_model = classifier.fit(X_flow_train_scaled, y_flow_train)

    y_flow_pred = flow_model.predict(X_flow_test_scaled)

    print("------------------------------------------------------------------------------")
    print("Confusion matrix:")
    cm = confusion_matrix(y_flow_test, y_flow_pred)
    print(cm)
    acc = accuracy_score(y_flow_test, y_flow_pred)
    print("Success accuracy: {:.2f}%".format(acc * 100))
    print("Failure accuracy: {:.2f}%".format((1 - acc) * 100))
    print("------------------------------------------------------------------------------")

    joblib.dump(flow_model, 'flow_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')

    # Track execution time and memory usage
    end_time = time.time()
    execution_time = end_time - start_time

    # Track memory usage
    memory_usage = process.memory_info().rss / (1024 * 1024)  # Convert to MB
    peak_memory = tracemalloc.get_traced_memory()[1] / (1024 * 1024)  # Convert to MB
    tracemalloc.stop()

    # Track CPU and disk usage
    cpu_usage = process.cpu_percent(interval=1)
    disk_usage = psutil.disk_usage('/')

    print("\nPerformance Metrics:")
    print(f"Execution Time: {execution_time:.2f} seconds")
    print(f"CPU Usage: {cpu_usage}%")
    print(f"Memory Usage: {memory_usage:.2f} MB")
    print(f"Peak Memory Usage: {peak_memory:.2f} MB")
    print(f"Disk Usage: {disk_usage.percent}%")

train_and_save_model()
