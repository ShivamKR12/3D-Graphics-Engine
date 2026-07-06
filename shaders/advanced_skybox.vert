#version 330 core
// Vertex shader for rendering a full-screen triangle in clip space,
// passing the clip-space position to the fragment shader for skybox sampling.

layout (location = 0) in vec3 in_position; // Vertex position input (already in clip space)

// Output to fragment shader: clip-space coordinates
out vec4 clipCoords;

void main() {
    // Directly assign clip-space position to gl_Position (no transformation needed)
    gl_Position = vec4(in_position, 1.0);

    // Pass clip-space coordinates to the fragment shader
    clipCoords = gl_Position;
}
