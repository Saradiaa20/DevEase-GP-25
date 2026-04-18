import os
import pytest
from unittest.mock import patch, mock_open, MagicMock

# Import the module components to test
from app.services.file_handler import FileHandler, analyze_file

class TestFileHandler:
    
    @patch('os.makedirs')
    def test_ensure_storage_folder_on_init(self, mock_makedirs):
        """Test that initializing FileHandler creates the directory."""
        handler = FileHandler(storage_folder="test_project_files")
        
        mock_makedirs.assert_called_with("test_project_files", exist_ok=True)
        assert handler.storage_folder == "test_project_files"

    @patch('builtins.input', return_value="test_code.py")
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_user_input_file_valid_python(self, mock_makedirs, mock_exists, mock_input):
        """Test user input accepts valid Python files."""
        handler = FileHandler()
        result = handler.user_input_file()
        
        assert result == "test_code.py"

    @patch('builtins.input', return_value="missing_file.py")
    @patch('os.path.exists', return_value=False)
    @patch('os.makedirs')
    def test_user_input_file_not_found(self, mock_makedirs, mock_exists, mock_input):
        """Test FileNotFoundError is raised when file doesn't exist."""
        handler = FileHandler()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            handler.user_input_file()
            
        assert "File not found" in str(exc_info.value)

    @patch('builtins.input', return_value="script.js")
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_user_input_file_unsupported_extension(self, mock_makedirs, mock_exists, mock_input):
        """Test ValueError is raised for unsupported file extensions."""
        handler = FileHandler()
        
        with pytest.raises(ValueError) as exc_info:
            handler.user_input_file()
            
        assert "Unsupported file type" in str(exc_info.value)

    @patch('os.makedirs')
    def test_read_file(self, mock_makedirs):
        """Test reading file content."""
        handler = FileHandler()
        mock_file_content = "print('Hello, DevEase!')"
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mocked_file:
            content = handler.read_file("dummy_path.py")
            
            mocked_file.assert_called_once_with("dummy_path.py", 'r', encoding='utf-8')
            assert content == mock_file_content

    @patch('shutil.copy')
    @patch('os.makedirs')
    def test_save_to_local_folder(self, mock_makedirs, mock_copy):
        """Test saving a file to the local storage folder."""
        handler = FileHandler(storage_folder="test_project_files")
        source_path = "/path/to/source/script.py"
        expected_destination = os.path.join("test_project_files", "script.py")
        
        result = handler.save_to_local_folder(source_path)
        
        mock_copy.assert_called_once_with(source_path, expected_destination)
        assert result == expected_destination

    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_get_saved_path_exists(self, mock_makedirs, mock_exists):
        """Test retrieving a valid saved file path."""
        handler = FileHandler(storage_folder="test_project_files")
        result = handler.get_saved_path("script.py")
        
        expected_path = os.path.join("test_project_files", "script.py")
        assert result == expected_path

    @patch('os.path.exists', return_value=False)
    @patch('os.makedirs')
    def test_get_saved_path_not_exists(self, mock_makedirs, mock_exists):
        """Test FileNotFoundError is raised when retrieving a non-existent saved file."""
        handler = FileHandler()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            handler.get_saved_path("missing.py")
            
        assert "No such file saved" in str(exc_info.value)


class TestAnalyzeFile:

    @pytest.fixture
    def mock_dependencies(self):
        """Pytest fixture to provide mock handler and parser for analysis tests."""
        handler = MagicMock()
        handler.SUPPORTED_EXTENSIONS = ['.java', '.py']
        parser = MagicMock()
        return handler, parser

    @patch('os.path.exists', return_value=False)
    def test_analyze_file_not_found(self, mock_exists, mock_dependencies):
        """Test analysis workflow fails gracefully if file is missing."""
        handler, parser = mock_dependencies
        result = analyze_file("fake_file.py", handler, parser)
        
        assert result is False
        handler.read_file.assert_not_called()

    @patch('os.path.exists', return_value=True)
    def test_analyze_file_unsupported_ext(self, mock_exists, mock_dependencies):
        """Test analysis workflow fails gracefully on unsupported extensions."""
        handler, parser = mock_dependencies
        result = analyze_file("fake_file.txt", handler, parser)
        
        assert result is False
        handler.read_file.assert_not_called()

    @patch('os.path.exists', return_value=True)
    def test_analyze_file_success(self, mock_exists, mock_dependencies):
        """Test successful analysis workflow."""
        handler, parser = mock_dependencies
        
        handler.read_file.return_value = "print('test')"
        parser.parse_file.return_value = {
            "ast_nodes": 10,
            "code_smells": [],
            "quality_score": 95,
            "ml_complexity": {"features": {"loc": 10}}
        }
        
        result = analyze_file("valid_file.py", handler, parser)
        
        assert result is True
        handler.read_file.assert_called_once_with("valid_file.py")
        parser.parse_file.assert_called_once_with("valid_file.py")