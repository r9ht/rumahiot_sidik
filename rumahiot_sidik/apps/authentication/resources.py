
# resource for incoming email authentication request
# for easier error handling
class EmailAuthenticationRequest(object):
    def __init__(self,email,password):
        self.email = email
        self.password = password
