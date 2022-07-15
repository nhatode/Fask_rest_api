from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import os

# Azure Key Vault Config
#secret_client = SecretClient(vault_url=os.environ.get("KEY_VAULT_URL"),
#                             credential=DefaultAzureCredential())


class Config(object):
    """Base config, uses staging database server."""
    DEBUG = False
    TESTING = False
    server_name = "Main.Dev.ED.IT.SQL"
    #username = secret_client.get_secret("sql-username").value
    #password = secret_client.get_secret("sql-password").value
    username = 'SQ-ED_KS'
    password = 'v8Dga7k&OZcFLv5Fpm;ADxk'
    database_name = 'Reports'
    port = '1433'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"mssql+pyodbc://" \
               f"{self.username}:{self.password}@{self.server_name}:{self.port}/{self.database_name}?" \
               f"driver=ODBC Driver 17 for SQL Server"


class DevelopmentConfig(Config):
    server_name = "Main.Dev.ED.IT.SQL"


class BetaConfig(Config):
    server_name = "Main.Beta.ED.IT.SQL"


class ProductionConfig(Config):
    server_name = "Main.Prod.ED.IT.SQL"
