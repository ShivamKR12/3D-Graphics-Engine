#version 330 core

/**
 * Fragment shader for shadow map rendering.
 * 
 * This shader is used when rendering the scene from the light's perspective 
 * to capture depth information only. Since only depth is required, 
 * no color output or computations are needed in the fragment stage.
 */

void main() {
    // No color output needed; depth is automatically written to the depth buffer.
}
