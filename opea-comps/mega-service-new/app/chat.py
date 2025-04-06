from comps import ServiceOrchestrator, MicroService, ServiceRoleType
from comps.cores.proto.api_protocol import ChatCompletionResponse, ChatCompletionRequest
from fastapi import Request

class Chat:
    def __init__(self):
        print('init')
        self.megaservice = ServiceOrchestrator()
        self.endpoint = '/james-is-great'
        self.host = '0.0.0.0'
        self.port = 8000
    def add_remote_services(self):
        print('add_remote_services')
    def start(self):
        print('start')
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=ChatCompletionResponse,
        )

        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])

        self.service.start()

    def handle_request(self, request:ChatCompletionRequest):
        print('handle_request')
   

if __name__ == '__main__':
    print('main')
    chat = Chat()
    chat.add_remote_services()
    chat.start()        