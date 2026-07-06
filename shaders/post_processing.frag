#version 330 core

// A basic fragment shader for post-processing.
// It samples a color from the input scene texture and outputs it.

out vec4 fragColor; // Final pixel color

in vec2 uv_0; // Texture coordinates from the vertex shader

uniform sampler2D u_scene_texture;  // The texture containing the rendered scene
uniform sampler2D u_bloom_texture;  // The texture with the blurred bright spots
uniform float u_exposure = 1.0;     // Exposure control

void main() {
    vec3 scene_color = texture(u_scene_texture, uv_0).rgb;
    vec3 bloom_color = texture(u_bloom_texture, uv_0).rgb;

    // Additive blending
    vec3 final_color = scene_color + bloom_color;

    // Simple tonemapping and exposure control
    final_color = vec3(1.0) - exp(-final_color * u_exposure);

    fragColor = vec4(final_color, 1.0);
}