import os
import importlib
import pytest
from pathlib import Path
from unittest.mock import patch

# Import the module itself rather than specific variables 
# so we can reload it during testing.
from app.core import config

class TestConfig:
    def test_default_types_and_values(self):
        """Test that configuration variables have the correct types and default values."""
        assert isinstance(config.API_HOST, str)
        assert isinstance(config.API_PORT, int)
        assert isinstance(config.API_RELOAD, bool)
        assert isinstance(config.CORS_ORIGINS, list)
        assert isinstance(config.MAX_UPLOAD_SIZE, int)
        
        # Test specific hardcoded values
        assert isinstance(config.ALLOWED_EXTENSIONS, list)
        assert '.py' in config.ALLOWED_EXTENSIONS
        assert '.js' in config.ALLOWED_EXTENSIONS
        
        # Check that base dir is a valid Path object
        assert isinstance(config.BASE_DIR, Path)

    def test_directories_are_created_on_import(self):
        """Test that the os.makedirs calls successfully created the directories."""
        assert os.path.exists(config.UPLOAD_DIR)
        assert os.path.exists(config.STORAGE_FOLDER)
        assert os.path.exists(Path(config.LOG_FILE).parent)
        
        # Ensure they are actually directories, not files
        assert os.path.isdir(config.UPLOAD_DIR)
        assert os.path.isdir(config.STORAGE_FOLDER)
        assert os.path.isdir(Path(config.LOG_FILE).parent)

    def test_custom_environment_variables_parsing(self):
        """Test that env vars are correctly parsed into ints, bools, and lists."""
        custom_env = {
            "API_HOST": "192.168.1.1",
            "API_PORT": "9090",
            "API_RELOAD": "false",
            "CORS_ORIGINS": "http://localhost:3000,https://mywebsite.com",
            "MAX_UPLOAD_SIZE": "5120", # 5KB
            "LOG_LEVEL": "DEBUG"
        }
        
        # Patch the environment variables
        with patch.dict(os.environ, custom_env):
            # Reload the module so it re-evaluates os.getenv with our mocked variables
            importlib.reload(config)
            
            assert config.API_HOST == "192.168.1.1"
            assert config.API_PORT == 9090
            assert config.API_RELOAD is False
            assert config.CORS_ORIGINS == ["http://localhost:3000", "https://mywebsite.com"]
            assert config.MAX_UPLOAD_SIZE == 5120
            assert config.LOG_LEVEL == "DEBUG"

        # Teardown: Reload the module again without the mock to restore the original 
        # environment for any subsequent tests.
        importlib.reload(config)

    def test_api_reload_truthy_values(self):
        """Ensure API_RELOAD properly handles the string 'true'."""
        with patch.dict(os.environ, {"API_RELOAD": "TrUe"}):
            importlib.reload(config)
            assert config.API_RELOAD is True
            
        importlib.reload(config)