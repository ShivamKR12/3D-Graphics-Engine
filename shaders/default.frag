#version 330 core

// Fragment shader implementing Phong lighting with support for soft shadow sampling
// using PCF (Percentage-Closer Filtering). Gamma correction is also applied.

layout (location = 0) out vec4 fragColor; // Output color of the fragment

// Inputs from the vertex shader
in vec2 uv_0;             // UV coordinates for texture sampling
in vec3 normal;           // Surface normal
in vec3 fragPos;          // Fragment position in world space
in vec4 shadowCoord;      // Shadow coordinate for shadow map projection

// Light structure containing ambient, diffuse, and specular components
struct Light {
    vec3 position; // Light position in world space
    vec3 Ia;       // Ambient intensity
    vec3 Id;       // Diffuse intensity
    vec3 Is;       // Specular intensity
};

uniform Light light;
uniform sampler2D u_texture_0;     // Albedo/diffuse texture
uniform vec3 camPos;               // Camera position
uniform sampler2DShadow shadowMap; // Depth comparison texture for shadow mapping
uniform vec2 u_resolution;         // Shadow map resolution for PCF offset calculation

// Performs a shadow map depth comparison at an offset (ox, oy)
float lookup(float ox, float oy) {
    vec2 pixelOffset = 1 / u_resolution; // Convert pixel offset to texture space
    return textureProj(shadowMap, shadowCoord + vec4(
        ox * pixelOffset.x * shadowCoord.w,
        oy * pixelOffset.y * shadowCoord.w,
        0.0, 0.0));
}

// Basic 4-sample soft shadow using PCF and 2x2 rotated grid
float getSoftShadowX4() {
    float shadow;
    float swidth = 1.5; // Sampling spread
    vec2 offset = mod(floor(gl_FragCoord.xy), 2.0) * swidth;

    // Sample 4 neighboring points
    shadow += lookup(-1.5 * swidth + offset.x,  1.5 * swidth - offset.y);
    shadow += lookup(-1.5 * swidth + offset.x, -0.5 * swidth - offset.y);
    shadow += lookup( 0.5 * swidth + offset.x,  1.5 * swidth - offset.y);
    shadow += lookup( 0.5 * swidth + offset.x, -0.5 * swidth - offset.y);

    return shadow / 4.0;
}

// Medium-quality 4x4 grid soft shadow (16 samples)
float getSoftShadowX16() {
    float shadow;
    float swidth = 1.0;
    float endp = swidth * 1.5;

    // Loop through 4x4 sample area
    for (float y = -endp; y <= endp; y += swidth) {
        for (float x = -endp; x <= endp; x += swidth) {
            shadow += lookup(x, y);
        }
    }
    return shadow / 16.0;
}

// High-quality 8x8 grid soft shadow (64 samples)
float getSoftShadowX64() {
    float shadow;
    float swidth = 0.6;
    float endp = swidth * 3.0 + swidth / 2.0;

    // Loop through 8x8 sample area
    for (float y = -endp; y <= endp; y += swidth) {
        for (float x = -endp; x <= endp; x += swidth) {
            shadow += lookup(x, y);
        }
    }
    return shadow / 64.0;
}

// Single shadow sample (hard edge)
float getShadow() {
    return textureProj(shadowMap, shadowCoord);
}

// Computes lighting (Phong model) with shadowing applied
vec3 getLight(vec3 color) {
    vec3 Normal = normalize(normal);

    // Ambient component (constant)
    vec3 ambient = light.Ia;

    // Diffuse component (Lambert)
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;

    // Specular component (Blinn-Phong)
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32); // Shininess = 32
    vec3 specular = spec * light.Is;

    // Shadow calculation
    // Choose desired shadow quality function here:
    float shadow = getSoftShadowX16(); // 16-tap PCF

    // Combine lighting components, attenuated by shadow
    return color * (ambient + (diffuse + specular) * shadow);
}

void main() {
    float gamma = 2.2;

    // Sample and gamma-correct the base color (linearize)
    vec3 color = texture(u_texture_0, uv_0).rgb;
    color = pow(color, vec3(gamma));

    // Apply lighting
    color = getLight(color);

    // Gamma correction (encode for output)
    color = pow(color, 1.0 / vec3(gamma));

    fragColor = vec4(color, 1.0);
}
