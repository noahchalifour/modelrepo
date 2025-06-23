"""
Tests for the helper functions in the modelrepo.repository._helpers module.

This module tests the functionality of repository helper functions, particularly
the dynamic repository factory loading mechanism that allows for flexible
repository selection based on configuration.
"""

from unittest.mock import Mock, patch, MagicMock
import pytest
from dependency_injector.providers import Configuration

from modelrepo.repository._helpers import get_repository_factory
from modelrepo.repository._model_repository import ModelRepository


def test_get_repository_factory_success():
    """
    Test successful repository factory loading with valid configuration.

    This test verifies that get_repository_factory can successfully load
    a repository class from a fully qualified path and return its factory
    method. It mocks the import mechanism to simulate a valid repository
    class with a get_repository_factory method.
    """
    # Create a mock configuration
    mock_config = Mock(spec=Configuration)
    mock_config.get.return_value = "modelrepo.repository.InMemoryModelRepository"
    
    # Create a mock repository class with get_repository_factory method
    mock_repository_class = Mock()
    mock_factory = Mock()
    mock_repository_class.get_repository_factory.return_value = mock_factory
    
    # Create a mock module
    mock_module = Mock()
    setattr(mock_module, "InMemoryModelRepository", mock_repository_class)
    
    with patch('modelrepo.repository._helpers.importlib.import_module', return_value=mock_module) as mock_import:
        result = get_repository_factory(mock_config)
            
        # Verify the configuration was accessed correctly
        mock_config.get.assert_called_once_with("class_path")
            
        # Verify the module was imported correctly
        mock_import.assert_called_with("modelrepo.repository")
            
        # Verify the factory method was called
        mock_repository_class.get_repository_factory.assert_called_once_with(mock_config)
            
        # Verify the correct factory was returned
        assert result == mock_factory
            

def test_get_repository_factory_import_error():
    """
    Test repository factory loading with ImportError.

    This test verifies that get_repository_factory properly handles and
    re-raises ImportError when the specified module cannot be imported.
    It also tests that the error is logged appropriately.
    """
    # Create a mock configuration
    mock_config = Mock(spec=Configuration)
    mock_config.get.return_value = "nonexistent.module.SomeRepository"
    
    with patch('modelrepo.repository._helpers.importlib.import_module', side_effect=ImportError("Module not found")):
        with pytest.raises(ImportError, match="Module not found"):
            get_repository_factory(mock_config)


                

