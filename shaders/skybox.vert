#version 330 core

/**
 * Vertex shader for rendering a skybox.
 *
 * This shader transforms the input cube vertex positions using the projection and view matrices,
 * discards translation from the view matrix to make the skybox appear infinitely far,
 * and passes texture coordinates to the fragment shader for cubemap sampling.
 */

layout (location = 0) in vec3 in_position; // Input vertex position of the skybox cube

out vec3 texCubeCoords; // Output direction vector used for sampling the cubemap in the fragment shader

uniform mat4 m_proj;    // Projection matrix
uniform mat4 m_view;    // View matrix (translation should be removed before passed in)

void main() {
    texCubeCoords = in_position; // Pass the direction vector to fragment shader (used as lookup into cubemap)

    vec4 pos = m_proj * m_view * vec4(in_position, 1.0); // Transform the vertex to clip space

    // Force the depth (z and w) to be equal so the skybox is always drawn at the farthest depth
    gl_Position = pos.xyww;

    // Slight depth tweak to prevent z-fighting or artifacts with depth testing
    gl_Position.z -= 0.0001;
}
