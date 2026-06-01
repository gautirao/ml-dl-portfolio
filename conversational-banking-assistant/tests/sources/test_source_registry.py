from datetime import date, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from cba.domain.enums import (
    DocumentType,
    IntegrityStatus,
    ProductArea,
    RiskLevel,
    SourceType,
    StalePolicy,
)
from cba.sources.registry import SourceRegistry

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
REGISTRY_FIXTURES = FIXTURES_DIR / "source_registry"
DOC_FIXTURES = FIXTURES_DIR / "documents"


def test_load_valid_registry() -> None:
    registry_path = REGISTRY_FIXTURES / "valid_sources.yaml"
    sources = SourceRegistry.load_from_yaml(registry_path)
    assert len(sources) == 2
    assert sources[0].source_id == "test-valid-doc"
    assert sources[1].risk_level == RiskLevel.HIGH


def test_missing_required_fields() -> None:
    registry_path = REGISTRY_FIXTURES / "invalid_missing_required.yaml"
    with pytest.raises(ValidationError):
        SourceRegistry.load_from_yaml(registry_path)


def test_path_traversal_validation() -> None:
    registry_path = REGISTRY_FIXTURES / "invalid_path_traversal.yaml"
    with pytest.raises(ValidationError) as excinfo:
        SourceRegistry.load_from_yaml(registry_path)
    assert "Path traversal" in str(excinfo.value)


def test_kebab_case_validation() -> None:
    # Test with invalid ID directly through model if possible, or a temp yaml
    from cba.domain.models import Source

    with pytest.raises(ValidationError) as excinfo:
        Source(
            source_id="Invalid_ID",
            bank="test",
            title="test",
            source_type=SourceType.PUBLIC_PDF,
            product_area=ProductArea.CURRENT_ACCOUNTS,
            document_type=DocumentType.TERMS_CONDITIONS,
            url="https://example.com",
            citation_label="[T]",
            retrieved_at=date.today(),
            local_path="data/raw/test.pdf",
            content_hash="hash",
            freshness_threshold_days=30,
            allowed_for_demo=False,
            risk_level=RiskLevel.MEDIUM,
            stale_policy=StalePolicy.WARN_ONLY,
        )
    assert "kebab-case" in str(excinfo.value)


def test_risk_level_validation_high_risk_missing_boundary() -> None:
    from cba.domain.models import Source

    with pytest.raises(ValidationError) as excinfo:
        Source(
            source_id="test-id",
            bank="test",
            title="test",
            source_type=SourceType.PUBLIC_PDF,
            product_area=ProductArea.CURRENT_ACCOUNTS,
            document_type=DocumentType.TERMS_CONDITIONS,
            url="https://example.com",
            citation_label="[T]",
            retrieved_at=date.today(),
            local_path="data/raw/test.pdf",
            content_hash="hash",
            freshness_threshold_days=30,
            allowed_for_demo=False,
            risk_level=RiskLevel.HIGH,  # High risk
            # financial_advice_boundary missing
            stale_policy=StalePolicy.WARN_ONLY,
        )
    assert "financial_advice_boundary" in str(excinfo.value)


def test_risk_level_validation_low_risk_for_fee_info() -> None:
    from cba.domain.models import Source

    with pytest.raises(ValidationError) as excinfo:
        Source(
            source_id="test-id",
            bank="test",
            title="test",
            source_type=SourceType.PUBLIC_PDF,
            product_area=ProductArea.CURRENT_ACCOUNTS,
            document_type=DocumentType.FEE_INFORMATION,  # Fee info
            url="https://example.com",
            citation_label="[T]",
            retrieved_at=date.today(),
            local_path="data/raw/test.pdf",
            content_hash="hash",
            freshness_threshold_days=30,
            allowed_for_demo=False,
            risk_level=RiskLevel.LOW,  # Should not be low
            stale_policy=StalePolicy.WARN_ONLY,
        )
    assert "cannot be low" in str(excinfo.value)


def test_integrity_check_ok() -> None:
    registry_path = REGISTRY_FIXTURES / "valid_sources.yaml"
    # We need to set the base path for local_path resolution
    # In the valid_sources.yaml, local_path is 'tests/fixtures/documents/sample-policy.txt'
    # The project root is where we run tests from.
    sources = SourceRegistry.load_from_yaml(registry_path)
    source = sources[0]

    # Simulate project root as current directory
    status = SourceRegistry.verify_integrity(source, project_root=Path("."))
    assert status == IntegrityStatus.OK


def test_integrity_check_missing() -> None:
    from cba.domain.models import Source

    source = Source(
        source_id="test-missing",
        bank="test",
        title="test",
        source_type=SourceType.PUBLIC_PDF,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        document_type=DocumentType.TERMS_CONDITIONS,
        url="https://example.com",
        citation_label="[T]",
        retrieved_at=date.today(),
        local_path="data/raw/non_existent.pdf",
        content_hash="hash",
        freshness_threshold_days=30,
        allowed_for_demo=False,
        risk_level=RiskLevel.MEDIUM,
        stale_policy=StalePolicy.WARN_ONLY,
    )
    status = SourceRegistry.verify_integrity(source, project_root=Path("."))
    assert status == IntegrityStatus.MISSING_FILE


def test_integrity_check_hash_mismatch() -> None:
    registry_path = REGISTRY_FIXTURES / "valid_sources.yaml"
    sources = SourceRegistry.load_from_yaml(registry_path)
    source = sources[0]
    source.content_hash = "wrong-hash"

    status = SourceRegistry.verify_integrity(source, project_root=Path("."))
    assert status == IntegrityStatus.HASH_MISMATCH


def test_staleness_flag() -> None:
    from cba.domain.models import Source

    # Not stale
    source_fresh = Source(
        source_id="test-fresh",
        bank="test",
        title="test",
        source_type=SourceType.PUBLIC_PDF,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        document_type=DocumentType.TERMS_CONDITIONS,
        url="https://example.com",
        citation_label="[T]",
        retrieved_at=date.today() - timedelta(days=5),
        local_path="data/raw/test.pdf",
        content_hash="hash",
        freshness_threshold_days=10,
        allowed_for_demo=False,
        risk_level=RiskLevel.MEDIUM,
        stale_policy=StalePolicy.WARN_ONLY,
    )
    assert SourceRegistry.is_stale(source_fresh) is False

    # Stale
    source_stale = Source(
        source_id="test-stale",
        bank="test",
        title="test",
        source_type=SourceType.PUBLIC_PDF,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        document_type=DocumentType.TERMS_CONDITIONS,
        url="https://example.com",
        citation_label="[T]",
        retrieved_at=date.today() - timedelta(days=15),
        local_path="data/raw/test.pdf",
        content_hash="hash",
        freshness_threshold_days=10,
        allowed_for_demo=False,
        risk_level=RiskLevel.MEDIUM,
        stale_policy=StalePolicy.WARN_ONLY,
    )
    assert SourceRegistry.is_stale(source_stale) is True
