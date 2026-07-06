#version 330 core

// Extracts bright pixels from the scene texture.

out vec4 fragColor;
in vec2 uv_0;

uniform sampler2D u_scene_texture;
uniform float u_threshold = 1.0; // Brightness threshold

void main() {
    vec3 color = texture(u_scene_texture, uv_0).rgb;

    // A common way to calculate brightness (luminance)
    float brightness = dot(color, vec3(0.2126, 0.7152, 0.0722));

    // If the pixel is not bright enough, discard it (output black)
    if(brightness < u_threshold) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        fragColor = vec4(color, 1.0);
    }
}