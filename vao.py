from vbo import VBO
from shader_program import ShaderProgram

class VAO:
    """
    Manages Vertex Array Objects (VAOs) for different models and rendering modes.
    Links Vertex Buffer Objects (VBOs) with appropriate shader programs.
    """

    def __init__(self, ctx):
        """
        Initialize all VAOs required by the renderer.

        Args:
            ctx: The ModernGL context used for rendering.
        """
        self.ctx = ctx

        # Load all vertex buffers
        self.vbo = VBO(ctx)

        # Load all compiled shader programs
        self.program = ShaderProgram(ctx)

        # Dictionary to store all VAOs
        self.vaos = {}

        # Create VAO for a textured and lit cube using the default shader
        self.vaos['cube'] = self.get_vao(
            program=self.program.programs['default'],
            vbo=self.vbo.vbos['cube']
        )

        # Create VAO for the cube using the shadow map shader (used during shadow rendering pass)
        self.vaos['shadow_cube'] = self.get_vao(
            program=self.program.programs['shadow_map'],
            vbo=self.vbo.vbos['cube']
        )

        # Create VAO for the cat model with default shader
        self.vaos['cat'] = self.get_vao(
            program=self.program.programs['default'],
            vbo=self.vbo.vbos['cat']
        )

        # Create VAO for the cat model using shadow shader
        self.vaos['shadow_cat'] = self.get_vao(
            program=self.program.programs['shadow_map'],
            vbo=self.vbo.vbos['cat']
        )

        # Create VAO for rendering a basic skybox
        self.vaos['skybox'] = self.get_vao(
            program=self.program.programs['skybox'],
            vbo=self.vbo.vbos['skybox']
        )

        # Create VAO for rendering an advanced skybox (e.g. with lighting/reflection)
        self.vaos['advanced_skybox'] = self.get_vao(
            program=self.program.programs['advanced_skybox'],
            vbo=self.vbo.vbos['advanced_skybox']
        )

    def get_vao(self, program, vbo):
        """
        Create a VAO using the given shader program and VBO.

        Args:
            program: A compiled ModernGL shader program.
            vbo: A custom VBO object containing vertex data and metadata.

        Returns:
            A ModernGL vertex array object (VAO).
        """
        # Construct and return the VAO, linking vertex buffer with shader attributes
        vao = self.ctx.vertex_array(
            program,
            [(vbo.vbo, vbo.format, *vbo.attribs)],
            skip_errors=True  # Allows VAO creation to proceed even if some attributes are missing
        )
        return vao

    def destroy(self):
        """
        Clean up GPU resources by releasing VBOs and shader programs.
        """
        self.vbo.destroy()
        self.program.destroy()
