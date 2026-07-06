#version 330 core

/**
 * Fragment shader for rendering a skybox.
 * 
 * This shader samples a color from a cubemap texture based on a direction vector (`texCubeCoords`)
 * and outputs it as the final fragment color. It creates the illusion of a distant environment.
 */

out vec4 fragColor;              // Final output color of the fragment

in vec3 texCubeCoords;           // Direction vector used to sample from the cubemap

uniform samplerCube u_texture_skybox; // Cubemap texture representing the skybox

void main() {
    // Sample the skybox color using the direction vector and output it
    fragColor = texture(u_texture_skybox, texCubeCoords);
}
