# Decompose Vector

Decompose SVG or DXF paths into individual `<line>` and `<path>` segments.

## Key Features

- **Input formats**: SVG or DXF
- **Output format**: Always SVG with individual elements
- **Path decomposition**: Converts complex paths into individual `<line>` and `<path>` segments
- **Duplicate removal**: Automatically removes duplicate line segments (including reversed duplicates)
- **Geometric support**: Handles lines, arcs, cubic Bézier curves, and quadratic Bézier curves
- **DXF features**: Supports LINE, ARC, and LWPOLYLINE entities with proper viewBox calculation
- **Cutting machine friendly**: Perfect for Cricut Design Space or Silhouette Studio

## Setup

This project uses a Python virtual environment managed with `direnv` and `make`.

### Basic Setup

1.  **Copy the `direnv` configuration file:**
    ```bash
    cp .envrc.dist .envrc
    ```

2.  **Allow `direnv` to create the virtual environment:**
    ```bash
    direnv allow
    ```
    This will create a virtual environment inside a `.direnv` directory.

3.  **Install the runtime dependencies:**
    ```bash
    make install
    ```

### Development Setup

For development work including testing and code quality tools:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional)
pre-commit install
```

**Development tools included:**
- `pytest` with coverage reporting
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking
- `pre-commit` for git hooks

## Usage

Once the environment is set up, you can run the script directly. The virtual environment will be automatically activated if you are using `direnv`.

### Processing SVG Files

```bash
./decompose-vector.py input.svg output.svg
```

### Processing DXF Files

```bash
./decompose-vector.py input.dxf output.svg
```

### Example with Sample File

```bash
./decompose-vector.py samples/Hexagon_box.dxf test_output.svg
```

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_svg_processing.py -v

# Run tests with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type check
mypy .

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Available Make Commands

```bash
# Install dependencies
make install

# Clean virtual environment
make clean

# Show available targets
make help
```

## Project Structure

This is a single-file application with the following key components:

- **`decompose-vector.py`**: Main application script
- **`decompose_svg()`**: Handles SVG input processing
- **`decompose_dxf()`**: Handles DXF input processing
- **Utility functions**: Point normalization, duplicate detection, geometric calculations

## Supported Features

### SVG Processing
- Line segments
- Arc segments
- Cubic Bézier curves
- Quadratic Bézier curves
- Complex path decomposition

### DXF Processing
- LINE entities
- ARC entities
- LWPOLYLINE entities (exploded into individual segments)
- Automatic viewBox calculation based on modelspace extents
- DXF unit preservation in SVG output

### Output Format
- Each decomposed segment gets a unique ID
- All elements use black stroke with no fill
- XML output is properly formatted
- Duplicate line segments are automatically removed
