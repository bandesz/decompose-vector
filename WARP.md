# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Decompose Vector is a Python utility that decomposes SVG or DXF paths into individual `<line>` and `<path>` segments. The tool is designed for use with cutting machines like Cricut Design Space or Silhouette Studio.

**Key Features:**
- Input: SVG (via `svgpathtools`) or DXF (via `ezdxf`) files
- Output: Always SVG format
- Duplicate straight line removal
- Skips tiny "ghost" lines from closepath operations
- Supports various geometric primitives (lines, arcs, Bézier curves)

## Code Architecture

This is a single-file application with a straightforward architecture:

**Main Components:**
- `decompose_svg()`: Handles SVG input processing using `svgpathtools`
- `decompose_dxf()`: Handles DXF input processing using `ezdxf`
- Shared utilities for geometric operations and duplicate detection

**Data Flow:**
1. Input file format detection (.svg vs .dxf)
2. Path/entity extraction and decomposition
3. Geometric primitive processing (Line, Arc, CubicBezier, QuadraticBezier)
4. Duplicate line detection and filtering
5. SVG output generation with prettified XML

**Key Processing Logic:**
- Lines shorter than 1 unit are filtered out as "ghost" lines
- Duplicate detection uses normalized point coordinates with 6-decimal precision
- DXF files include viewBox calculation based on modelspace extents
- DXF units are preserved in SVG output dimensions

## Development Environment

This project uses `direnv` for Python virtual environment management:

### Setup Commands
```bash
# Copy environment configuration
cp .envrc.dist .envrc

# Allow direnv to create virtual environment
direnv allow

# Install dependencies
make install
```

### Dependencies
- `svgpathtools`: SVG path processing
- `ezdxf`: DXF file handling

## Common Commands

### Running the Application
```bash
# Process SVG file
./decompose-vector.py input.svg output.svg

# Process DXF file
./decompose-vector.py input.dxf output.svg
```

### Development Tasks
```bash
# Install dependencies
make install

# Clean virtual environment
make clean

# Show available make targets
make help
```

### Testing Sample Files
```bash
# Test with included sample
./decompose-vector.py samples/Hexagon_box.dxf test_output.svg
```

## Key Implementation Details

**Geometric Processing:**
- Uses complex numbers for 2D point representation
- Arc processing converts DXF angles to SVG arc commands
- Polylines are exploded into individual line/arc segments

**Output Format:**
- Each decomposed segment gets a unique ID (`path{idx}_seg{idx}` for SVG, `dxf_seg{idx}` for DXF)
- All elements use black stroke with no fill
- XML output is prettified using minidom

**DXF-Specific Handling:**
- Supports LINE, ARC, and LWPOLYLINE entities
- Handles DXF unit codes and coordinate systems
- Processes both simple entities and polyline virtual entities

## File Structure Context

- **Single-file application**: `decompose-vector.py` contains all logic
- **Configuration**: `.envrc.dist` template for direnv setup
- **Dependencies**: Minimal `requirements.txt` with two packages
- **Build system**: Simple Makefile with install/clean targets
- **Samples**: Test files in `samples/` directory
