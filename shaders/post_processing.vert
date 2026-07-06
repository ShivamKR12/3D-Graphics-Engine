#version 330 core

// A simple vertex shader for rendering a full-screen triangle.
// It passes through clip-space positions and calculates UV coordinates.

layout (location = 0) in vec3 in_position; // Vertex position in clip space

out vec2 uv_0; // UV coordinates for the fragment shader

void main() {
    // Pass clip-space position directly to the output
    gl_Position = vec4(in_position, 1.0);
    // Calculate UV coordinates from clip-space position [(-1, 1) -> (0, 1)]
    uv_0 = (in_position.xy + 1.0) * 0.5;
}