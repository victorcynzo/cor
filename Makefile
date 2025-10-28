# Makefile for Cor Gaze Detection Library
# Provides convenient build targets for development

.PHONY: all build clean test install dev-install help

# Default target
all: build test

# Build the extension
build:
	@echo "Building Cor extension..."
	python setup.py build_ext --inplace

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.so" -delete
	find . -name "*.pyd" -delete

# Run tests
test: build
	@echo "Running tests..."
	python test_cor.py

# Install in development mode
dev-install:
	@echo "Installing development dependencies..."
	pip install -r requirements-dev.txt
	pip install -e .

# Regular install
install:
	@echo "Installing Cor library..."
	pip install -r requirements.txt
	pip install .

# Automated build and test
auto: 
	@echo "Running automated build and test..."
	python build_and_test.py

# Run example
example: build
	@echo "Running example usage..."
	python example_usage.py

# Check dependencies
check-deps:
	@echo "Checking dependencies..."
	@python -c "import cv2; print('OpenCV:', cv2.__version__)" || echo "OpenCV not found"
	@python -c "import numpy; print('NumPy:', numpy.__version__)" || echo "NumPy not found"
	@python -c "import matplotlib; print('Matplotlib:', matplotlib.__version__)" || echo "Matplotlib not found"

# Help target
help:
	@echo "Cor Gaze Detection Library - Build Targets"
	@echo "=========================================="
	@echo "all         - Build and test (default)"
	@echo "build       - Build the C extension"
	@echo "clean       - Clean build artifacts"
	@echo "test        - Run test suite"
	@echo "install     - Install the library"
	@echo "dev-install - Install with development dependencies"
	@echo "auto        - Run automated build and test script"
	@echo "example     - Run example usage script"
	@echo "check-deps  - Check required dependencies"
	@echo "help        - Show this help message"