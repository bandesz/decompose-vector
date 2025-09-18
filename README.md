# Decompose Vector

Decompose SVG or DXF paths into individual `<line>` and `<path>` segments.

- Input can be SVG (via `svgpathtools`) or DXF (via `ezdxf`).
- Output is always an SVG.
- Each segment becomes its own element (good for Cricut Design Space or Silhouette Studio).
- Duplicate straight lines are removed.
- Tiny "ghost" lines (from `closepath`) are skipped.

## Setup

This project uses a Python virtual environment managed with `direnv` and `make`.

1.  **Copy the `direnv` configuration file:**
    ```bash
    cp .envrc.dist .envrc
    ```

2.  **Allow `direnv` to create the virtual environment:**
    ```bash
    direnv allow
    ```
    This will create a virtual environment inside a `.direnv` directory.

3.  **Install the dependencies:**
    ```bash
    make install
    ```
    This will install the required Python packages into the virtual environment managed by `direnv`.

## Usage

Once the environment is set up, you can run the script directly. The virtual environment will be automatically activated if you are using `direnv`.

```bash
./decompose-vector.py input.svg output.svg
```

Or

```bash
./decompose-vector.py input.dxf output.svg
