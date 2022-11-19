import yaml
from logging import config
with open('mambupy/utils/logging.yaml', "r") as f:
    configuration = yaml.full_load(f.read())
config.dictConfig(configuration)
