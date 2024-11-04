# Atomization-of-Four-point-Bending-of-RC-Beam-modelling-in-ABAQUS-Using-Python
- This project contains Python scripts for creating a 3D concrete beam model in Abaqus with reinforced plates, rebar, and stirrups, and setting up a dynamic analysis step. The model leverages Abaqus' Python API for geometry creation, material assignments, and assembly.
- This project contains Python scripts for creating a 3D concrete beam model in Abaqus with reinforced plates, rebar, and stirrups, and setting up a dynamic analysis step. The model leverages Abaqus' Python API for geometry creation, material assignments, and assembly.

## Table of Contents
  1. Introduction
  2. Features
  3. Getting Started
  4. Usage
  5. Functions
  6. Contributing
  7. License

## Introduction
- This repository includes Python scripts to automate the creation of a concrete beam model with reinforcement in Abaqus. The model is customized with concrete properties, steel reinforcement, and configured for dynamic analysis. The scripts simplify tasks such as model initialization, geometry creation, material assignment, and instance patterning.

## Features
- Define a 3D concrete beam with customizable dimensions
- Automatically set up material properties for concrete and steel
- Add plates at specific locations on the beam
- Create and pattern reinforcement bars and stirrups
- Set up an Explicit Dynamics Step for dynamic analysis
- Automatically clean up instances after Boolean operations

## Getting Started
**Prerequisites**

  - **Abaqus:** Ensure you have Abaqus CAE installed, as this script uses Abaqus’ python API.
  - **Python:** Scripts should be run within Abaqus' Python environment.
  - **Installation**
    1. Clone the repository:
        ```sh
          git clone https://github.com/yourusername/ConcreteBeamAbaqus.git
        ```
    2. Navigate to the project directory:
         ```sh
          cd ConcreteBeamAbaqus
        ```
         
    3. Open the script in Abaqus and run it in Abaqus CAE's Python environment. (See the attached Video)

## Usage
**Initialize the Model:**  The script begins with model initialization using NameOfModel to set a name for the model.Define Geometry and Material Properties: Use beam_size and platesize functions to set up the geometry, including dimensions and material properties for concrete and steel plates.
**Define Reinforcements:** Call total_bar_numbers with desired parameters to define bottom and top rebar, along with stirrups.
**Run Analysis:** The script configures an explicit dynamics step for analysis. Execute the script within Abaqus to create the model, set materials, and run the analysis.

## Functions

### Initializes a model in Abaqus with a specified name.Below are the prameters
- **_NameOfModel(Name='')_**
> - **Name (str):** Base name for the model.
> - **beam_size** (width, depth, length, cover, point_load_distance)

### Defines the beam's geometry and material properties.Below are the prameters
> - **width (float):** Width of the beam.
> - **depth (float):** Depth of the beam.
> - **length (float):** Length of the beam.
> - **cover (float):** Concrete cover for reinforcement.
> - **point_load_distance (float):** Location for the point load.
> - **platesize(plate_depth, plate_length, spacing_from_edge)**

### Creates plates on the beam with specified dimensions and material properties.Parameters:
> - **plate_depth (float):** Depth of the plate.
> - **plate_length (float):** Length of the plate.
> - **spacing_from_edge (float):** Distance from the beam's edge.
> - **total_bar_numbers(no_of_bottom_bars, no_of_top_bars, diameter_of_bottom_bars, diameter_of_top_bars, Dia_of_stirrups, spacing_of_stirrups, end_distance_of_stirrups_from_bar_edge)**

### Sets up reinforcement bars and stirrups for the beam.Parameters:
> - **no_of_bottom_bars (int):** Number of bottom reinforcement bars.
> - **no_of_top_bars (int):** Number of top reinforcement bars.
> - **diameter_of_bottom_bars (float):** Diameter of bottom bars.
> - **diameter_of_top_bars (float):** Diameter of top bars.
> - **Dia_of_stirrups (float):** Diameter of stirrups.
> - **spacing_of_stirrups (float)**: Spacing of stirrups along the beam.
> - **end_distance_of_stirrups_from_bar_edge (float):** Edge distance for stirrups.

### Main Execution Flow
> - **Model Setup:** Initializes a named model.
> - **Geometry Creation:** Sets up beam dimensions and material properties.
> - **Plate Creation:** Adds steel plates at specified positions.
> - **Reinforcement Setup:** Configures bottom, top rebar, and stirrups.
> - **Dynamics Step Creation:** Adds an explicit dynamics step for the analysis.
> - **Cleanup:** Deletes unnecessary instances for clean assembly.

### Example
An example script execution for a beam
> - Define a beam with specific parameters
```beam_size(width=150, depth=150, length=1300, cover=25, point_load_distance=450)```
> - Add plates to the beam
```platesize(plate_depth=10, plate_length=40, spacing_from_edge=30)```
> - Add reinforcement bars and stirrups
```total_bar_numbers(2, 2, 12, 10, 8, 80, 50)```


## Contributing:
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License. 

## Closure
This documentation provides a complete overview of the repository, how to get started, and the function definitions. The setup is ready for GitHub, enabling users to understand and contribute effectively.
