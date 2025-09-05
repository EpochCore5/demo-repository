"""
Tests for the icon generation script.
"""

import sys
import tempfile
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import generate_icons  # noqa: E402


class TestIconGeneration:
    """Test cases for icon generation functionality."""

    def test_clean_assets_creates_directory(self):
        """Test that clean_assets creates the icons directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assets_dir = Path(tmpdir)
            generate_icons.clean_assets(assets_dir)
            assert (assets_dir / "icons").exists()
            assert (assets_dir / "icons").is_dir()

    def test_clean_assets_removes_existing_icons(self):
        """Test that clean_assets removes existing icons for idempotency."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assets_dir = Path(tmpdir)
            icons_dir = assets_dir / "icons"
            icons_dir.mkdir(parents=True, exist_ok=True)

            # Create a dummy file
            dummy_file = icons_dir / "dummy.png"
            dummy_file.write_text("dummy content")
            assert dummy_file.exists()

            # Clean assets should remove everything
            generate_icons.clean_assets(assets_dir)
            assert icons_dir.exists()
            assert not dummy_file.exists()

    def test_generate_icon_creates_file(self):
        """Test that generate_icon creates a PNG file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_icon.png"
            generate_icons.generate_icon(32, output_path)

            assert output_path.exists()
            assert output_path.suffix == ".png"
            assert output_path.stat().st_size > 0

    def test_generate_icon_different_sizes(self):
        """Test that generate_icon works with different sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sizes = [16, 64, 128]
            for size in sizes:
                output_path = Path(tmpdir) / f"icon_{size}.png"
                generate_icons.generate_icon(size, output_path)
                assert output_path.exists()

    def test_main_function_success(self, monkeypatch, tmp_path):
        """Test that main function completes successfully."""
        # Create a temporary script file that points to our temp directory
        script_dir = tmp_path / "scripts"
        script_dir.mkdir()
        script_file = script_dir / "generate_icons.py"
        script_file.write_text("# dummy")

        # Monkeypatch __file__ to point to our temp script
        monkeypatch.setattr("generate_icons.__file__", str(script_file))

        result = generate_icons.main()
        assert result == 0

        # Check that icons were generated
        assets_dir = tmp_path / "assets" / "icons"
        assert assets_dir.exists()

        expected_icons = [
            "icon-16x16.png",
            "icon-32x32.png",
            "icon-64x64.png",
            "icon-128x128.png",
            "icon-256x256.png",
        ]
        for icon_name in expected_icons:
            icon_path = assets_dir / icon_name
            assert icon_path.exists(), f"Expected icon {icon_name} was not created"


def test_repository_structure():
    """Test that the repository has the expected structure."""
    repo_root = Path(__file__).parent.parent

    # Check that required directories exist
    assert (repo_root / "scripts").exists()
    assert (repo_root / "tests").exists()

    # Check that required files exist
    assert (repo_root / "scripts" / "generate_icons.py").exists()
    assert (repo_root / "requirements.txt").exists()


def test_requirements_file_content():
    """Test that requirements.txt contains expected dependencies."""
    repo_root = Path(__file__).parent.parent
    requirements_file = repo_root / "requirements.txt"

    content = requirements_file.read_text()

    # Check for required packages
    assert "pytest" in content
    assert "flake8" in content
    assert "black" in content
    assert "Pillow" in content
