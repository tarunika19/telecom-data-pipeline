import pytest
from telecom_pipeline.generate import generate
from telecom_pipeline.clean import clean


@pytest.fixture(scope="session")
def raw():
    return generate(n_devices=6, hours=24, seed=1, dirty=True)


@pytest.fixture(scope="session")
def cleaned(raw):
    return clean(raw)
