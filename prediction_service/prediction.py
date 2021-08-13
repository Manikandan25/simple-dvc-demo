import yaml
import os
import json
import joblib
import numpy as np


params_path = "params.yaml"
schema_path = os.path.join("prediction_service", "schema_in.json")

class NotInRange(Exception):
    def __init__(self, message="Values entered are not in expected range"):
        self.message = message
        super().__init__(self.message)

class NotInCols(Exception):
    def __init__(self, message="Not in cols"):
        self.message = message
        super().__init__(self.message)



def read_params(config_path=params_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config

def predict(data):
    print("came in")
    config = read_params(params_path)
    print(1)
    model_dir_path = config["webapp_model_dir"]
    print(2)
    model = joblib.load(model_dir_path)
    print("going to predict")
    prediction = model.predict(data).tolist()[0]
    print(prediction)
    try:
        if 3 <= prediction <= 8:
            return prediction
        else:
            raise NotInRange
    except NotInRange:
        return "Unexpected result"


def get_schema(schema_path=schema_path):
    with open(schema_path) as json_file:
        schema = json.load(json_file)
    return schema

def validate_input(dict_request):
    def _validate_cols(col):
        schema = get_schema()
        actual_cols = schema.keys()
        if col not in actual_cols:
            raise NotInCols

    def _validate_values(col, val):
        schema = get_schema()

        if not (schema[col]["min"] <= float(dict_request[col]) <= schema[col]["max"]) :
            raise NotInRange

    for col, val in dict_request.items():
        _validate_cols(col)
        _validate_values(col, val)
    
    return True


def form_response(dict_request):
    print(dict_request)
    if validate_input(dict_request):
        print("valid")
        data = dict_request.values()
        data = [list(map(float, data))]
        print(data)
        response = float(predict(data))
        print(response)
        return response

def api_response(dict_request):
    print(dict_request)
    try:
        if validate_input(dict_request):
            print("valid")
            data = np.array([list(dict_request.values())])
            print(data)
            response = float(predict(data))
            print(response)
            response = {"response": response}
            return response
            
    except NotInRange as e:
        response = {"the_exected_range": get_schema(), "response": str(e) }
        return response

    except NotInCols as e:
        response = {"the_exected_cols": get_schema().keys(), "response": str(e) }
        return response


    except Exception as e:
        response = {"response": str(e) }
        return response