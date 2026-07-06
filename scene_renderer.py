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

        # Get the VAO for post-processing
        self.post_processing_vao = self.app.mesh.vao.vaos['post_processing']

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
        self.app.ctx.screen.use() # Bind the default screen framebuffer

        # Bind the scene texture from the main render pass
        self.scene_texture.use(location=0)
        # Render the full-screen quad
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
        self.scene_fbo.release() # Free the scene framebuffer
