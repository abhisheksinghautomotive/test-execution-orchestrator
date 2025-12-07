from importlib import reload
import pytest


def test_factory_defaults_to_memory(tmp_path, monkeypatch):
    monkeypatch.delenv("ORCHESTRATOR_PERSISTENCE", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    import orchestrator.config as cfg
    import orchestrator.repository.factory as fmod

    reload(cfg)
    reload(fmod)
    rrepo, erepo = fmod.get_repositories()
    assert rrepo is not None
    assert erepo is not None


def test_factory_raises_when_postgres_missing_url(monkeypatch):
    monkeypatch.setenv("ORCHESTRATOR_PERSISTENCE", "postgres")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    import orchestrator.config as cfg
    import orchestrator.repository.factory as fmod

    reload(cfg)
    reload(fmod)
    with pytest.raises(ValueError):
        fmod.get_repositories()


def test_factory_selects_dynamodb(monkeypatch):
    monkeypatch.setenv("ORCHESTRATOR_PERSISTENCE", "dynamodb")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    # don't invoke actual boto3 in CI; expect runtime error if boto3 missing
    import orchestrator.config as cfg
    import orchestrator.repository.factory as fmod

    reload(cfg)
    reload(fmod)
    rrepo, erepo = fmod.get_repositories()
    assert rrepo is not None

    assert erepo is not None


def test_factory_selects_postgres_with_url(monkeypatch):
    """Test factory creates postgres repos when URL provided."""
    from unittest.mock import patch, MagicMock

    monkeypatch.setenv("ORCHESTRATOR_PERSISTENCE", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
    import orchestrator.config as cfg
    import orchestrator.repository.factory as fmod

    reload(cfg)
    reload(fmod)

    # Mock SQLAlchemy create_engine to avoid actual DB connection
    with patch("orchestrator.repository.postgres.repo.create_engine") as mock_engine:
        mock_engine.return_value = MagicMock()

        rrepo, erepo = fmod.get_repositories()

        # Verify repos were created (they will fail to connect but factory path covered)
        assert rrepo is not None
        assert erepo is not None
        # Verify create_engine was called (meaning postgres path was taken)
        assert mock_engine.call_count >= 2  # Once for each repo
