import requests
import fnmatch
from alef_ml_utilities import get_config
config = get_config('../../adt/src/config.yml')


class HostHandler:
    def __init__(self):
        self.header = {
            'Authorization': 'Bearer ' + config['tests']['adt']['auth_token_k8']
        }

    def get_pod_service_name(self, service_name):
        """
         input: service_name e.g adt-service
         output: it will return service name from pod e.g adt-service-66f89d677b-7zjrj
         """
        url_k8dashboard = config["tests"]["adt"]["k8_dashboard_url"]
        response = requests.get(url_k8dashboard, headers=self.header)
        pods = response.json()['items']
        for elem in pods:
            pod_service = elem['metadata']['name']
            match = fnmatch.fnmatch(pod_service, service_name+"-*")
            if match:
                return pod_service

    def get_pod_ip(self, service):
        """ It will return POD IP"""
        service_id = self.get_pod_service_name(service)
        url_k8dashboard = f'{config["tests"]["adt"]["k8_dashboard_url"]}/{service_id}'
        response = requests.get(url_k8dashboard, headers=self.header)
        return response.json()['status']['podIP']
