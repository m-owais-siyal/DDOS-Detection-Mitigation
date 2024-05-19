# DDoS Detection and Mitigation Framework

This project is a comprehensive framework for detecting and mitigating Distributed Denial of Service (DDoS) attacks using network simulation on Mininet and an SDN controller. The framework includes custom topology generation, traffic generation (both benign and malicious), data collection, machine learning model training, and a graphical user interface for monitoring and analysis.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [For Improvements](#for-improvements)
  - [hping3 Commands](#hping3-commands)
- [Acknowledgments](#acknowledgments)
- [Final Report](#final-report)

## Introduction
This project leverages Mininet for network simulation and an SDN controller for traffic management to create a robust system for DDoS detection and mitigation. Traffic is generated using custom scripts and collected for analysis. A machine learning model is trained to classify traffic as benign or malicious, and this model is used by the SDN controller to mitigate DDoS attacks in real-time. 

## Features
- **Custom Network Topology**: Generate network topologies to simulate realistic traffic scenarios.
- **Traffic Generation**: Create both benign and malicious traffic using custom scripts and `hping3` commands.
- **Data Collection**: Collect network traffic data for training and evaluation.
- **Machine Learning Model**: Train a model using combined Kaggle and custom datasets for accurate DDoS detection.
- **Graphical User Interface**: Monitor current network traffic and visualize historical data through graphs and tables.
- **Admin and Terminal Dashboards**: Manage and control the framework using intuitive dashboards.

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/m-owais-siyal/DDOS-Detection-Mitigation.git
    cd DDOS-Detection-Mitigation
    ```
2. Set up the Mininet environment:
    ```sh
    sudo python mininet/topology.py
    ```
3. Install dependencies manually as needed.

4. Start the SDN controller:
    ```sh
    ryu-manager controller/controller.py
    ```

5. Run the backend:
    ```sh
    cd website/backend
    python3 server.py
    ```

6. Run the frontend:
    ```sh
    cd website/dashboard
    npm install
    npm start
    ```

## Usage
### For Improvements
1. Generate traffic:
    ```sh
    sudo python mininet/dataset_genration/generate_benign_traffic.py
    sudo python mininet/dataset_genration/generate_ddos_traffic.py
    ```
2. Collect data:
    ```sh
    sudo python controller/dataset_collection/collect_benign_traffic.py
    sudo python controller/dataset_collection/collect_ddos_traffic.py
    ```
3. Train the model:
    ```sh
    python controller/ML_models/model_tranning.py
    ```

**Note**: For generating and collecting traffic, the scripts `generate_benign_traffic.py` and `collect_benign_traffic.py` should be run simultaneously in two different terminals. The same applies to DDoS traffic generation and collection.

### hping3 Commands
To use Mininet, you have to run these `hping3` commands from an xterm terminal to generate traffic:
- **ICMP flood**:
    ```sh
    hping3 -1 -V -d 120 -w 64 -p 80 --rand-source --flood <ip>
    ```
- **SYN flood**:
    ```sh
    hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood <ip>
    ```
- **UDP flood**:
    ```sh
    hping3 -2 -V -d 120 -w 64 -p 80 --rand-source --flood <ip>
    ```

## Acknowledgments
- **Kaggle Datasets**: Utilized datasets from Kaggle for initial model training.
  - [DDoS Datasets by devendra416](https://www.kaggle.com/datasets/devendra416/ddos-datasets)
- **Custom Dataset**: Additional dataset available at:
  - [DDoS Dataset by Muhammad Owais Siyal](https://www.kaggle.com/datasets/mowaissiyal/ddos-dataset-made-with-mininet)

## Final Report
For more detailed information, please refer to the [Final Report](Final%20Report.pdf).

---

Feel free to explore the directories and scripts for a deeper understanding of the framework. Contributions and feedback are welcome!

**Note**: The topology provided in Mininet is very limited and can be a potential area for improvement.
