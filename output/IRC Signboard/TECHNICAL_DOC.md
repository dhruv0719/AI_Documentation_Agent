# IRC Signboard - Technical Documentation

## Architecture Overview

The project follows a modular design, with separate modules for handling GUI, API, sign generation, and utility functions, allowing for a clear separation of concerns and reusability of code. The architecture is centered around the generator_v2 module, which coordinates the rendering of road sign elements and applies sign configuration parameters. The project also utilizes a pipeline-like structure, where data flows from configuration modules to generation modules.

## Module Relationships

Modules depend on and interact with each other through imports and function calls, with the generator_v2 module being a central hub that coordinates the rendering of road sign elements. The sign_config module provides data structures for representing sign configurations, which are used by the generator_v2 module to generate signs. Utility modules, such as text_measurer and svg_parser, provide functions that are used by multiple modules to perform specific tasks.

## Design Patterns

- **Modular design**
- **Pipeline**
- **Factory**


---

## Module Reference


### `app.py`

**Purpose:** Provides a Flask-based web API for managing sign configuration data and generating sign graphics.

**Responsibilities:**
- Expose REST endpoints to retrieve and update design speed rules and layout configuration.
- Invoke the sign generation logic (generator_v2) to produce sign output based on provided parameters.
- Handle request/response serialization and CORS for client interactions.

**Key Components:**
- `Flask route functions (index, get_design_speed_rules, update_design_speed_rules, get_layout_config, update_layout_config, generate_sign, get_x_height)`
- `src.generator_v2 module for sign generation`
- `src.models.sign_config for configuration data handling`

**Dependencies:**
- `os`
- `json`
- `flask`
- `flask_cors`
- `src.generator_v2`
- `src.models.sign_config`

---

### `gui_app.py`

**Purpose:** Provides a PyQt6-based desktop GUI for generating IRC:67-2022 compliant road signs using configuration and generation logic from other modules.

**Responsibilities:**
- Manages user interface for road sign configuration
- Handles sign generation and output destination selection
- Displays standards rules and reference materials
- Coordinates interaction between GUI components and generation logic

**Key Components:**
- `MainWindow (central application window)`
- `main() (application entry point)`

**Dependencies:**
- `os`
- `sys`
- `PyQt6.QtWidgets`
- `PyQt6.QtCore`
- `PyQt6.QtGui`
- `PyQt6.QtSvgWidgets`
- `src.generator_v2`
- `src.models.sign_config`

---

### `main.py`

**Purpose:** Serves as the entry point for an application that generates content using a configured generator and handles errors.

**Responsibilities:**
- Initializes the application and execution flow
- Loads configuration settings from sign_config
- Coordinates content generation via generator_v2
- Handles errors through the errors module

**Key Components:**
- `main() function`
- `src.generator_v2`

**Dependencies:**
- `src.generator_v2`
- `src.models.sign_config`
- `src.utils.errors`

---

### `src\components\arrow.py`

**Purpose:** Generates and configures arrow elements for SVG output using predefined configurations and conversion utilities.

**Responsibilities:**
- Renders arrow graphics in SVG format
- Applies configuration settings from sign_config
- Converts measurement units using utility converters

**Key Components:**
- `Arrow class`
- `SVG rendering methods`

**Dependencies:**
- `svgwrite`
- `typing`
- `src.models.sign_config`
- `src.utils.converters`
- `src.utils.constants`

---

### `src\components\canvas.py`

**Purpose:** This module provides a Canvas class for generating and manipulating SVG graphics based on configuration settings.

**Responsibilities:**
- Rendering graphical elements using SVG format
- Handling configuration parameters for visual properties
- Converting data types for compatibility with SVG standards

**Key Components:**
- `Canvas class`
- `SVG element creation methods`
- `Configuration parameter handlers`

**Dependencies:**
- `svgwrite`
- `typing`
- `src.utils.constants`
- `src.utils.converters`
- `src.models.sign_config`

---

### `src\components\dimension_renderer.py`

**Purpose:** Renders dimensional data into SVG format for signage configurations

**Responsibilities:**
- Generates SVG elements representing dimensional measurements
- Applies sign configuration parameters from sign_config
- Converts measurement units using utility converters

**Key Components:**
- `DimensionRenderer class`
- `SVG rendering methods`
- `sign_config integration`
- `unit conversion utilities`

**Dependencies:**
- `svgwrite`
- `src.models.sign_config`
- `src.utils.converters`

---

### `src\components\text_renderer.py`

**Purpose:** Renders text elements into visual formats like SVG or images based on configuration settings.

**Responsibilities:**
- Generates SVG text elements using provided configurations
- Converts text blocks to image representations with PIL
- Applies styling and layout rules from sign configurations
- Encodes output as base64 data URLs for embedding

**Key Components:**
- `TextRenderer class`
- `svg_text_generation method`
- `image_rendering pipeline`
- `configuration application logic`

**Dependencies:**
- `svgwrite`
- `base64`
- `io`
- `PIL`
- `typing`
- `src.models.text_block`
- `src.models.sign_config`
- `src.utils.converters`

---

### `src\config\config_loader.py`

**Purpose:** This module is intended to load and manage configuration settings for the application, but currently contains no implemented code.

**Responsibilities:**

**Key Components:**

---

### `src\generator.py`

**Purpose:** Generates road sign images using configured text, graphics, and layout parameters.

**Responsibilities:**
- Combines text rendering and graphical elements into complete road signs
- Applies sign configuration parameters to generated outputs
- Coordinates canvas rendering for final sign composition

**Key Components:**
- `RoadSignGenerator class`
- `sign_config model integration`

**Dependencies:**
- `os`
- `typing`
- `src.models.sign_config`
- `src.components.canvas`
- `src.components.text_renderer`
- `src.components.arrow`
- `src.utils.converters`
- `src.utils.text_measurer`

---

### `src\generator_v2.py`

**Purpose:** Generates road sign SVGs by composing components and applying layout configurations.

**Responsibilities:**
- Coordinates rendering of road sign elements (arrows, text, dimensions)
- Applies sign configuration parameters from sign_config
- Handles SVG structure assembly through canvas component
- Processes layout calculations for element positioning

**Key Components:**
- `RoadSignGenerator`
- `src.layout.block_renderer`

**Dependencies:**
- `os`
- `typing`
- `src.components.arrow`
- `src.components.canvas`
- `src.utils.constants`
- `src.utils.converters`
- `src.layout.calculator`
- `src.components.text_renderer`
- `src.models.sign_config`
- `src.layout.block_renderer`
- `src.components.dimension_renderer`
- `src.utils.svg_parser`

---

### `src\layout\block_renderer.py`

**Purpose:** Renders text and graphical blocks using OpenCV and SVG parsing for layout generation.

**Responsibilities:**
- Renders text blocks with OpenCV
- Parses SVG content for graphical elements
- Applies geometric transformations to layout elements
- Configures sign layouts based on provided settings

**Key Components:**
- `BlockContentRenderer class`
- `SVG parsing utilities`
- `geometry application functions`
- `render methods`

**Dependencies:**
- `typing`
- `cv2`
- `src.models.sign_config`
- `src.models.text_block`
- `src.utils.svg_parser`
- `src.utils.geometry`

---

### `src\layout\calculator.py`

**Purpose:** Calculates layout dimensions and positioning for sign elements using text and SVG measurements.

**Responsibilities:**
- Calculates text dimensions using text measurement utilities
- Processes SVG elements for layout integration
- Applies sign configuration parameters to layout calculations

**Key Components:**
- `LayoutCalculator class`
- `src.utils.text_measurer`
- `src.utils.svg_parser`

**Dependencies:**
- `src.utils.converters`
- `src.utils.text_measurer`
- `src.utils.svg_parser`
- `src.models.sign_config`
- `typing`

---

### `src\models\sign_config.py`

**Purpose:** This module defines data structures for representing sign configurations and their text components, likely used for processing or serializing sign data.

**Responsibilities:**
- Providing a structured representation of sign configurations
- Handling text block properties for signs
- Enabling JSON serialization/deserialization of sign data

**Key Components:**
- `SignConfig (dataclass with JSON conversion methods)`
- `TextBlock (dataclass for text content properties)`

**Dependencies:**
- `json`
- `dataclasses`
- `typing`
- `src.utils.speed_mapper`
- `src.utils.constants`

---

### `src\models\text_block.py`

**Purpose:** Defines data structures for text elements and their font configurations in an application.

**Responsibilities:**
- Modeling font configuration parameters
- Representing text elements with associated styling
- Providing data transfer objects for text rendering components

**Key Components:**
- `FontConfig (font styling parameters)`
- `TextElement (text content with styling references)`

**Dependencies:**
- `dataclasses`
- `typing`

---

### `src\utils\constants.py`

**Purpose:** This module defines a class to hold application-wide constant values for easy access and maintenance.

**Responsibilities:**
- Centralized storage of constant values
- Providing a single source of truth for configuration parameters
- Improving code readability and maintainability

**Key Components:**
- `Constants class`
- `constant variables`

---

### `src\utils\converters.py`

**Purpose:** This module provides functionality for converting measurements between different units using predefined constants.

**Responsibilities:**
- Perform unit conversions (e.g., temperature, length, volume)
- Utilize constants from the constants module for accurate conversion factors
- Provide reusable conversion methods via the UnitConverter class

**Key Components:**
- `UnitConverter class with conversion methods`
- `Constants import for reference values`

**Dependencies:**
- `src.utils.constants`

---

### `src\utils\errors.py`

**Purpose:** This module defines custom exception classes for handling specific error scenarios in the application.

**Responsibilities:**
- Provide a FontLoadError exception for font-related loading failures
- Provide a SpeedMappingError exception for speed mapping configuration issues
- Centralize custom error types for consistent error handling across the codebase

**Key Components:**
- `FontLoadError`
- `SpeedMappingError`

---

### `src\utils\geometry.py`

**Purpose:** This module provides functions to calculate polygon coordinates for map arrow shapes, likely used for visualizing directions or markers on maps.

**Responsibilities:**
- Generating arrow polygon coordinates based on center points and dimensions
- Handling different units (pixel vs. abstract lengths) for arrow stem width
- Supporting both standard and advanced arrow polygon calculations

**Key Components:**
- `calculate_map_arrow_polygon`
- `calculate_map_advance_arrow_polygon`

**Dependencies:**
- `typing`

---

### `src\utils\speed_mapper.py`

**Purpose:** Maps design speeds to corresponding values, likely for configuration or data processing.

**Responsibilities:**
- Loading speed data from JSON files
- Mapping design speeds to specific values
- Handling errors related to invalid speed inputs

**Key Components:**
- `DesignSpeedMapper`
- `errors`

**Dependencies:**
- `json`
- `pathlib`
- `typing`
- `src.utils.errors`

---

### `src\utils\svg_parser.py`

**Purpose:** Extracts the aspect ratio from an SVG file for use in maintaining proportional scaling.

**Responsibilities:**
- Parses SVG files to locate aspect ratio definitions
- Handles different SVG aspect ratio specification formats (e.g., viewBox, width/height)
- Returns calculated aspect ratio as a string

**Key Components:**
- `get_svg_aspect_ratio function`
- `xml.etree.ElementTree parser`

**Dependencies:**
- `re`
- `xml.etree.ElementTree`

---

### `src\utils\text_measurer.py`

**Purpose:** Measures text dimensions and properties for layout calculations, likely using PIL for image/text rendering.

**Responsibilities:**
- Calculating text width/height for given fonts
- Handling text measurement errors through custom exceptions
- Providing metrics for text rendering in graphical contexts

**Key Components:**
- `TextMeasurer class`
- `PIL.ImageFont integration`

**Dependencies:**
- `PIL`
- `src.utils.errors`

---

### `test.py`

**Purpose:** This module appears to be a test or demonstration script for the text_measurer utility, likely used to measure text properties.

**Responsibilities:**
- Initialize and execute text measurement operations
- Interface with the text_measurer utility for processing
- Provide a main entry point for execution

**Key Components:**
- `main() function`
- `src.utils.text_measurer import`

**Dependencies:**
- `src.utils.text_measurer`

---


## Development Guidelines

[Add coding standards, contribution guidelines, etc.]

## Testing

[Add testing instructions]

---

*This technical documentation was automatically generated by the Code Documentation Agent.*
