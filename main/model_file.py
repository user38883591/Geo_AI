import torch
import torch.nn as nn
import torch.nn.functional as F

class CNNModel(nn.Module):
    def __init__(self, num_classes):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.fc1 = nn.Linear(64 * 56 * 56, 512)
        self.fc2 = nn.Linear(512, num_classes)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 56 * 56) 
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

def load_model(model_path):
    model = CNNModel(num_classes=9)
    model.load_state_dict(torch.load(model_path))
    model.eval() 
    return model

import os
import pickle

# Define paths to your model and scaler files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'main/savedmodels/model.pkl')
MINMAX_SCALER_PATH = os.path.join(BASE_DIR, 'main/savedmodels/minmaxscaler.pkl')
STAND_SCALER_PATH = os.path.join(BASE_DIR, 'main/savedmodels/standscaler.pkl')

# Load the model and scalers
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

with open(MINMAX_SCALER_PATH, 'rb') as f:
    minmax_scaler = pickle.load(f)

with open(STAND_SCALER_PATH, 'rb') as f:
    stand_scaler = pickle.load(f)

def make_prediction(data):
    # Scale and standardize input data
    data_minmax_scaled = minmax_scaler.transform([data])
    data_standardized = stand_scaler.transform(data_minmax_scaled)
    
    # Make a prediction
    prediction = model.predict(data_standardized)
    return prediction

