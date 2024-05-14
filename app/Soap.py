import zeep
class SOAPClient:
    def __init__(self, service_url):
        self.client = zeep.Client(service_url)

    def call_method(self, method_name, **kwargs):
        try:
            method = getattr(self.client.service, method_name)
            response = method(**kwargs)
            return response
        except Exception as e:
            return str(e)
