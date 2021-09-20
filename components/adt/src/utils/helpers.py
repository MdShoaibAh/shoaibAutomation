import json
from jsonschema import validate
from components.adt.src.utils.variables import payload


def get_question_request_payload(response_value, session_id):
    data_load = open(payload, 'r')
    data = json.load(data_load)
    data["NextQuestion"]["session_id"] = session_id
    data["NextQuestion"]["response"] = response_value
    updated_payload = open(payload, 'w')
    json.dump(data, updated_payload)
    return data


def get_student_report_payload(report, updated_session_id):
    data_load = open(payload, 'r')
    if updated_session_id is None:
        data = json.load(data_load)
        return data[report]
    else:
        data = json.load(data_load)
        data[report]['students'][0]['sessionId'] = updated_session_id
        updated_payload = open(payload, 'w')
        json.dump(data, updated_payload)
        return data[report]


def load_schema(file):
    with open(file) as schema_file:
        return json.loads(schema_file.read())


def assert_valid_schema(data, schema):
    schema = load_schema(schema)
    return validate(data, schema)
