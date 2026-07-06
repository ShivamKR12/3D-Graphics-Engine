class SceneRenderer:
    """
    Handles rendering the entire scene, including both shadow pass and main pass.

    Responsibilities:
    - Shadow map rendering to a depth texture (first pass)
    - Main scene rendering using lighting and shadows (second pass)
    - Managing framebuffers and draw calls for all objects and the skybox
    """

    def __init__(self, app):
        """
        Initialize the SceneRenderer.

        Args:
            app: The main application instance, containing references to context,
                 mesh data, scene graph, and other global resources.
        """
        self.app = app
        self.ctx = app.ctx  # OpenGL context
        self.mesh = app.mesh  # Mesh manager (contains textures, VAOs, etc.)
        self.scene = app.scene  # Scene containing all objects and the skybox

        # Create the depth framebuffer for shadow mapping
        self.depth_texture = self.mesh.texture.textures['depth_texture']
        self.depth_fbo = self.ctx.framebuffer(depth_attachment=self.depth_texture)

        # Create the main scene framebuffer for post-processing
        self.scene_texture = self.mesh.texture.textures['scene_texture']
        self.scene_fbo = self.ctx.framebuffer(
            color_attachments=[self.scene_texture],
            depth_attachment=self.ctx.depth_renderbuffer(self.app.WIN_SIZE)
        )

        # --- Bloom Setup ---
        self.bloom_texture_1 = self.mesh.texture.textures['bloom_texture_1']
        self.bloom_texture_2 = self.mesh.texture.textures['bloom_texture_2']

        self.bloom_fbo_1 = self.ctx.framebuffer(color_attachments=[self.bloom_texture_1])
        self.bloom_fbo_2 = self.ctx.framebuffer(color_attachments=[self.bloom_texture_2])

        # Get VAO and programs for post-processing
        self.post_processing_vao = self.app.mesh.vao.vaos['post_processing']
        self.pp_program = self.app.mesh.vao.program.programs['post_processing']
        self.brights_program = self.app.mesh.vao.program.programs['bloom_brights']
        self.blur_program = self.app.mesh.vao.program.programs['bloom_blur']

        # Number of blur passes. More passes = softer glow.
        self.blur_passes = 10

    def render_shadow(self):
        """
        Render the scene from the light's point of view to populate the shadow map.

        This uses a depth-only framebuffer and updates only depth values.
        """
        self.depth_fbo.clear()  # Clear previous depth values
        self.depth_fbo.use()  # Bind the depth framebuffer

        # Render shadow pass for each object in the scene
        for obj in self.scene.objects:
            obj.render_shadow()

    def main_render(self):
        """
        Render the full scene to the screen using standard shaders.

        Includes textured and lit objects, as well as the skybox.
        """
        self.scene_fbo.clear() # Clear the scene framebuffer
        self.scene_fbo.use() # Bind the scene framebuffer

        # self.app.ctx.screen.use()  # Bind the default screen framebuffer

        # Render each object in the scene using lighting and shadows
        for obj in self.scene.objects:
            obj.render()

        # Render the skybox last to ensure it's in the background
        self.scene.skybox.render()

    def post_processing(self):
        """
        Apply post-processing effects by rendering the scene texture to the screen.
        """
        # --- Pass 1: Extract bright areas ---
        self.bloom_fbo_1.use()
        self.scene_texture.use(location=0)
        self.brights_program['u_scene_texture'] = 0
        self.brights_program['u_threshold'] = 100.0  # Set high to disable bloom for testing
        self.post_processing_vao.render()

        # --- Pass 2: Blur the bright areas (ping-pong) ---
        is_horizontal = True
        for i in range(self.blur_passes):
            # Alternate between FBOs
            if is_horizontal:
                self.bloom_fbo_2.use()
                self.bloom_texture_1.use(location=0)
            else:
                self.bloom_fbo_1.use()
                self.bloom_texture_2.use(location=0)

            self.blur_program['u_source_texture'] = 0
            self.blur_program['u_horizontal'] = is_horizontal
            self.post_processing_vao.render()
            is_horizontal = not is_horizontal

        # --- Pass 3: Composite scene and bloom ---
        self.app.ctx.screen.use() # Bind the default screen framebuffer

        # Bind the original scene texture and the final blurred bloom texture
        self.scene_texture.use(location=0)
        # The final blurred result is in bloom_texture_1 if blur_passes is even, else bloom_texture_2
        if self.blur_passes % 2 == 0:
            self.bloom_texture_1.use(location=1)
        else:
            self.bloom_texture_2.use(location=1)

        self.pp_program['u_scene_texture'] = 0
        self.pp_program['u_bloom_texture'] = 1
        self.post_processing_vao.render()

    def render(self):
        """
        The main render entry point called once per frame.

        Executes:
        - Scene update (animations, transforms)
        - Shadow rendering pass
        - Main rendering pass
        """
        self.scene.update()      # Update scene logic and transformations
        self.render_shadow()     # Pass 1: depth map for shadows
        self.main_render()       # Pass 2: main render with lighting and shadows
        self.post_processing()   # Pass 3: render scene texture to screen

    def destroy(self):
        """
        Clean up and release GPU resources when the renderer is destroyed.
        """
        self.depth_fbo.release()  # Free the depth framebuffer
        self.scene_fbo.release()  # Free the scene framebuffer
        self.bloom_fbo_1.release()
        self.bloom_fbo_2.release()
