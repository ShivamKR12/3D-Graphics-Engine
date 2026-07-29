# 3D-Graphics-Engine

A 3D graphics engine built from scratch in Python using ModernGL (a modern OpenGL wrapper) and Pygame for windowing and input handling. This project demonstrates several fundamental computer graphics techniques in a clear and well-structured application.

![screenshot](/screenshot/0.jpg)

## Features

*   **Modern OpenGL Rendering**: Utilizes `ModernGL` for efficient graphics programming with an OpenGL 3.3+ core profile.
*   **Phong Lighting Model**: Implements realistic per-fragment lighting with ambient, diffuse, and specular components.
*   **Dynamic Soft Shadows**: Renders high-quality dynamic soft shadows using Percentage-Closer Filtering (PCF) on a shadow map, adding depth and realism to the scene.
*   **First-Person Camera**: A classic first-person camera system with mouse-look for orientation and keyboard controls for movement.
*   **Scene Management**: A structured system for managing all objects within the scene, including loading models and procedural geometry.
*   **Model Loading**: Supports loading 3D models from `.obj` files (e.g., the cat model) via the `pywavefront` library.
*   **Advanced Skybox**: Features an efficient skybox implementation that renders a full-screen triangle and calculates view direction in the fragment shader using the inverse view-projection matrix.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

*   Python 3.8+
*   pip

### Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/ShivamKR12/3D-Graphics-Engine.git
    cd 3D-Graphics-Engine
    ```
2.  Install the required Python packages using the `requirements.txt` file:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the main application file from the root directory:
```sh
python main.py
```

### Controls
*   **W, A, S, D**: Move the camera forward, left, backward, and right.
*   **Q, E**: Move the camera up and down.
*   **Mouse**: Look around the scene.
*   **ESC**: Exit the application.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
