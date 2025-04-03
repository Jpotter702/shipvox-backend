from abc import ABC, abstractmethod

class BaseAuth(ABC):
    @abstractmethod
    def get_token(self) -> str:
        """Returns valid access token, refreshing if necessary"""
        pass

    @abstractmethod
    def _is_token_valid(self) -> bool:
        """Check if current token is valid"""
        pass

    @abstractmethod
    def _refresh_token(self) -> None:
        """Refresh the access token"""
        pass
