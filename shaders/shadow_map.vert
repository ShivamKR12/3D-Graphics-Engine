#version 330 core

/**
 * Vertex shader for shadow map generation.
 * 
 * This shader transforms world-space vertex positions into clip space from 
 * the light's perspective using a Model-View-Projection (MVP) matrix. 
 * The depth values output to the framebuffer are later used for shadow comparisons.
 */

layout (location = 2) in vec3 in_position; // Input vertex position from the mesh (attribute location 2)

uniform mat4 m_proj;        // Projection matrix (usually orthographic or perspective from light's POV)
uniform mat4 m_view_light;  // View matrix from the light's point of view
uniform mat4 m_model;       // Model matrix transforming object from local to world space

void main() {
    // Compute the Model-View-Projection matrix from light's perspective
    mat4 mvp = m_proj * m_view_light * m_model;

    // Transform vertex position into clip space for depth testing
    gl_Position = mvp * vec4(in_position, 1.0);
}
