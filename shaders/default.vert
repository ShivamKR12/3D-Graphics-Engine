#version 330 core

// Vertex shader for transforming vertex data into clip space,
// computing world position, normal vector, texture coordinates, 
// and generating coordinates for shadow mapping.

layout (location = 0) in vec2 in_texcoord_0; // UV coordinates from vertex buffer
layout (location = 1) in vec3 in_normal;     // Vertex normal
layout (location = 2) in vec3 in_position;   // Vertex position in model space

out vec2 uv_0;           // Pass UVs to fragment shader
out vec3 normal;         // Pass transformed normal to fragment shader
out vec3 fragPos;        // World-space position of the fragment
out vec4 shadowCoord;    // Coordinates used for shadow map lookup

// Uniform transformation matrices
uniform mat4 m_proj;         // Projection matrix
uniform mat4 m_view;         // View matrix (camera)
uniform mat4 m_view_light;   // View matrix from light's perspective
uniform mat4 m_model;        // Model matrix (object space to world space)

// Shadow bias matrix maps from clip space [-1, 1] to texture space [0, 1]
mat4 m_shadow_bias = mat4(
    0.5, 0.0, 0.0, 0.0,
    0.0, 0.5, 0.0, 0.0,
    0.0, 0.0, 0.5, 0.0,
    0.5, 0.5, 0.5, 1.0
);

void main() {
    // Pass through the UV coordinates
    uv_0 = in_texcoord_0;

    // Compute fragment world-space position
    fragPos = vec3(m_model * vec4(in_position, 1.0));

    // Transform the normal vector properly by the inverse transpose of model matrix
    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);

    // Standard MVP transform for rendering to screen
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);

    // Compute shadow matrix (from light's point of view)
    mat4 shadowMVP = m_proj * m_view_light * m_model;

    // Project position into light-space and bias into [0,1] range for shadow map sampling
    shadowCoord = m_shadow_bias * shadowMVP * vec4(in_position, 1.0);

    // Apply small offset to Z to reduce shadow acne
    shadowCoord.z -= 0.0005;
}
