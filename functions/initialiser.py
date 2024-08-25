import torch
import spacy
import os

from train_model.model import NeuralNet

def init_data():
    """load and return trained model data, to access the data, and specific parts of the data: data = init_data(), then you can do things like: input_size = data['input_size'] to retrieve value of input size and store it in a variable"""
    current_directory = os.path.dirname(__file__)
    data_file_path = os.path.abspath(os.path.join(current_directory, '..', 'train_model', 'data.pth'))
    data_file = data_file_path
    data = torch.load(data_file)
    return data

def init_model():
    """initialise and return model. To use, create an instance of the model like this: model = init_model(), then use model as you would normally"""
    data = init_data()
    input_size  = data['input_size']
    hidden_size = data['hidden_size']
    output_size = data['output_size']
    model_state = data['model_state']
    model = NeuralNet(input_size, hidden_size, output_size)
    model.load_state_dict(model_state)
    model.eval()
    return model

def init_nlp():
    """initialise and return en_core. To use, create an instance of nlp like this: nlp = init_nlp(), then use nlp as you would normally"""
    nlp = spacy.load("en_core_web_sm")
    return nlp
    
def init_device():
    """initialise and return gpu/cpu. To use, create an instance of device like this: device = init_device(), then use device as you would normally"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return device
