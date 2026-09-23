"""Smoke test for Member 3 Experience structure."""

from pathlib import Path


def test_experience_directory_layout():
    """Verify that training, frontend, and gateway subdirectories exist."""
    root = Path(__file__).resolve().parent.parent
    assert (root / "training").is_dir(), "training directory missing in member3-experience"
    assert (root / "frontend").is_dir(), "frontend directory missing in member3-experience"
    assert (root / "gateway").is_dir(), "gateway directory missing in member3-experience"
