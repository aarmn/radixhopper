set shell := ["powershell.exe", "-c"]

# List available commands
default:
    @just --list

# Run linting
lint:
    ruff check .
    black --check .

# static type-check using mypy
typecheck:
    mypy .

# Run tests
test:
    pytest

# Update requirements.txt, for streamlit deploy to work
update-requirements:
    toml-to-req --toml-file pyproject.toml > requirements.txt

# Perform a patch update
patch:
    @just lint
    @just test
    hatch build
    @just update-requirements
    git add .
    $msg = Read-Host "Enter commit message"
    git commit -m $msg
    git push

# Publish the package to PyPI
publish:
    twine upload dist/*

# Publish the package to TestPyPI
publish-test:
    twine upload dist/* -r test

# Perform a patch update and publish
patch-and-publish:
    @just patch
    @just publish

# Clean up build artifacts
clean:
    if (Test-Path dist) { Remove-Item -Recurse -Force dist }
    if (Test-Path *.egg-info) { Remove-Item -Recurse -Force *.egg-info }

# Run the Streamlit app
run-app:
    streamlit run radixhopper/st.py

# Create a new virtual environment
create-venv:
    python -m venv .venv

# Activate the virtual environment
activate-venv:
    .\.venv\Scripts\Activate.ps1

# Install dependencies
install-deps:
    pip install -r requirements.txt

# Update all dependencies
update-deps:
    pip install --upgrade -r requirements.txt

# Run security checks
security-check:
    safety check

# Generate documentation
generate-docs:
    # need some serious work on
    pdoc --html --output-dir docs radixhopper 