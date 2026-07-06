#version 330 core
// Fragment shader for rendering a full-screen advanced skybox using cube mapping and inverse projection-view transformation

// Output fragment color
out vec4 fragColor;

// Input clip space coordinates interpolated from the vertex shader
in vec4 clipCoords;

// Uniform cube map texture for the skybox
uniform samplerCube u_texture_skybox;

// Inverse of the projection * view matrix used to reconstruct world direction
uniform mat4 m_invProjView;

void main() {
    // Transform clip space coordinates back to world space using the inverse projection-view matrix
    vec4 worldCoords = m_invProjView * clipCoords;

    // Normalize the resulting world position to obtain a direction vector for sampling the cube map
    vec3 texCubeCoord = normalize(worldCoords.xyz / worldCoords.w);

    // Sample the cube map using the direction vector
    fragColor = texture(u_texture_skybox, texCubeCoord);
}
