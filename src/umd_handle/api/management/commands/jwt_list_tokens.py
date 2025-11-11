from django.core.management.base import BaseCommand
from umd_handle.api.models import JWTToken

class Command(BaseCommand):
    help = "Lists the JWT tokens that are available for use."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        jwt_tokens = self.get_jwt_tokens()
        self.list_tokens(jwt_tokens)

    def get_jwt_tokens(self):
        """
        Returns a list of all JWTTokens
        """
        return JWTToken.objects.all()

    def list_tokens(self, jwt_tokens):
        """
        Prints a comma-separated list of tokens to STDOUT
        """
        if jwt_tokens:
            for jwt_token in jwt_tokens:
                token = jwt_token.token
                description = jwt_token.description
                created = jwt_token.created
                self.stdout.write(f"{token},{description},{created}")
        else:
            self.stdout.write("No token entries found!")

