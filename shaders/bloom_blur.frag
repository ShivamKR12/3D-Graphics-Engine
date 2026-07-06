#version 330 core

// Performs a single pass of a 9-tap Gaussian blur.

out vec4 fragColor;
in vec2 uv_0;

uniform sampler2D u_source_texture; // Texture to be blurred
uniform bool u_horizontal;         // Direction of the blur

// The weights for a 9-tap Gaussian filter
float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

void main() {
    vec2 texel_size = 1.0 / vec2(textureSize(u_source_texture, 0));
    vec3 result = texture(u_source_texture, uv_0).rgb * weight[0]; // Current fragment

    if(u_horizontal) {
        for(int i = 1; i < 5; ++i) {
            result += texture(u_source_texture, uv_0 + vec2(texel_size.x * i, 0.0)).rgb * weight[i];
            result += texture(u_source_texture, uv_0 - vec2(texel_size.x * i, 0.0)).rgb * weight[i];
        }
    } else { // Vertical blur
        for(int i = 1; i < 5; ++i) {
            result += texture(u_source_texture, uv_0 + vec2(0.0, texel_size.y * i)).rgb * weight[i];
            result += texture(u_source_texture, uv_0 - vec2(0.0, texel_size.y * i)).rgb * weight[i];
        }
    }

    fragColor = vec4(result, 1.0);
}