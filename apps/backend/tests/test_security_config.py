import os
from pathlib import Path


def test_docker_compose_uses_env_vars_for_credentials() -> None:
    """Regression test: Ensure docker-compose.yml uses environment variables for credentials.
    
    This test prevents accidental commits of hardcoded credentials.
    """
    docker_compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    
    if not docker_compose_path.exists():
        # Skip test if docker-compose.yml doesn't exist
        return
    
    content = docker_compose_path.read_text()
    
    # Check for hardcoded passwords in environment sections
    hardcoded_patterns = [
        "POSTGRES_PASSWORD: support_password",
        "POSTGRES_PASSWORD:support_password",
        'POSTGRES_PASSWORD: "support_password"',
        "POSTGRES_USER: support_user",
        "POSTGRES_USER:support_user",
        'POSTGRES_USER: "support_user"',
    ]
    
    for pattern in hardcoded_patterns:
        assert pattern not in content, f"Found hardcoded credential pattern: {pattern}"
    
    # Ensure environment variable syntax is used
    assert "${POSTGRES_USER:-" in content or "${POSTGRES_USER}" in content, \
        "POSTGRES_USER should use environment variable syntax"
    assert "${POSTGRES_PASSWORD:-" in content or "${POSTGRES_PASSWORD}" in content, \
        "POSTGRES_PASSWORD should use environment variable syntax"


def test_env_example_has_placeholders_not_real_credentials() -> None:
    """Regression test: Ensure env.example uses placeholder values, not real credentials."""
    env_example_path = Path(__file__).parent.parent / "env.example"
    
    if not env_example_path.exists():
        # Skip test if env.example doesn't exist
        return
    
    content = env_example_path.read_text()
    
    # Check for obviously real credentials (common patterns)
    real_password_patterns = [
        "password=123456",
        "password=admin",
        "password=root",
        "password=changeme",
        "password=secret",
    ]
    
    for pattern in real_password_patterns:
        assert pattern not in content.lower(), f"Found potentially real credential pattern: {pattern}"
    
    # Ensure placeholder values are used
    assert "your-secret-key" in content or "change-in-production" in content, \
        "SECRET_KEY should use placeholder value"
    assert "user:password" in content or "support_user" in content, \
        "Database credentials should use placeholder values"


def test_config_has_secure_defaults() -> None:
    """Regression test: Ensure config.py has secure default values."""
    from app.core.config import Settings
    
    # Create a settings instance without environment overrides
    settings = Settings(_env_file=None)
    
    # DEBUG should default to False for security
    assert settings.DEBUG is False, "DEBUG should default to False for security"
    
    # SECRET_KEY should not be the placeholder in production-like scenarios
    # (This is already enforced in Settings.__init__, but we test the default)
    assert settings.SECRET_KEY == "your-secret-key-change-in-production", \
        "SECRET_KEY default should be a placeholder requiring override"
