from alef_ml_utilities import get_config
from components.adt.src.utils.requests import APIRequest
from components.adt.src.utils.helpers import get_question_request_payload, get_student_report_payload
from components.adt.src.host_handler import HostHandler
config = get_config('../../adt/src/config.yml')
host = HostHandler()
pod_ip = host.get_pod_ip('adt-service')
base_url = f'http://{pod_ip}:' + config["tests"]["adt"]["adt_port"]


class RequestHandler:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + config['tests']['adt']['jwt']
        }

    def get_question_response(self, response_value, session_id):
        request = APIRequest()
        payload = get_question_request_payload(response_value, session_id)['NextQuestion']
        request_url = base_url+config["tests"]["adt"]["adt_predict"]
        response = request.post(request_url, payload, self.headers)
        return response

    def get_student_report_response(self, report_for, session_id):
        request = APIRequest()
        request_url = base_url+config["tests"]["adt"]["adt_explain"]
        payload = get_student_report_payload(report_for, session_id)
        response = request.post(request_url, payload, self.headers)
        return response
