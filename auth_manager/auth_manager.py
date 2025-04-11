class AuthManager:
    def __init__(self, carrier_registry, token_store=None):
        self.carriers = carrier_registry
        self.token_store = token_store

    def initiate_auth(self, carrier: str, user_context: dict) -> str:
        return self.carriers[carrier].get_auth_url(user_context)

    def handle_callback(self, carrier: str, request_data: dict) -> dict:
        tokens = self.carriers[carrier].exchange_token(request_data)
        if self.token_store:
            self.token_store.save_tokens(request_data.get("user_id"), carrier, tokens)
        return tokens

    def refresh_token(self, carrier: str, refresh_token: str) -> str:
        return self.carriers[carrier].refresh_token(refresh_token)
