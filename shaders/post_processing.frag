#version 330 core

// A basic fragment shader for post-processing.
// It samples a color from the input scene texture and outputs it.

out vec4 fragColor; // Final pixel color

in vec2 uv_0; // Texture coordinates from the vertex shader

uniform sampler2D u_scene_texture; // The texture containing the rendered scene

void main() {
    fragColor = texture(u_scene_texture, uv_0);
}