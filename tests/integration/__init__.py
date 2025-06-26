import os
import pytest

if not os.environ.get('RUN_INTEGRATION_TESTS'):
    pytest.skip("Skipping integration tests (RUN_INTEGRATION_TESTS not set)", allow_module_level=True)
