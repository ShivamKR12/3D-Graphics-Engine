class ShaderProgram:
    """
    Handles the compilation and management of multiple shader programs.
    """

    def __init__(self, ctx):
        """
        Initialize and compile all shader programs used in the application.

        Args:
            ctx: The moderngl context for compiling shader programs.
        """
        self.ctx = ctx
        self.programs = {}

        # Load and compile the default shader program
        self.programs['default'] = self.get_program('default')

        # Load and compile the skybox shader program
        self.programs['skybox'] = self.get_program('skybox')

        # Load and compile the advanced skybox shader program
        self.programs['advanced_skybox'] = self.get_program('advanced_skybox')

        # Load and compile the shadow map shader program
        self.programs['shadow_map'] = self.get_program('shadow_map')

        # Load and compile the post-processing shader
        self.programs['post_processing'] = self.get_program('post_processing')

        # Load bloom shaders manually
        # These are fragment-only effects that can reuse the post_processing vertex shader.
        with open('shaders/post_processing.vert') as file:
            post_processing_vert = file.read()

        with open('shaders/bloom_brights.frag') as file:
            bloom_brights_frag = file.read()

        with open('shaders/bloom_blur.frag') as file:
            bloom_blur_frag = file.read()

        # Compile programs by pairing the common vertex shader with specific fragment shaders
        self.programs['bloom_brights'] = self.ctx.program(vertex_shader=post_processing_vert, fragment_shader=bloom_brights_frag)
        self.programs['bloom_blur'] = self.ctx.program(vertex_shader=post_processing_vert, fragment_shader=bloom_blur_frag)
        
    def get_program(self, shader_program_name):
        """
        Load and compile a shader program from .vert and .frag files.

        Args:
            shader_program_name (str): Name of the shader file (without extension).

        Returns:
            A compiled moderngl shader program.
        """
        # Read vertex shader source
        with open(f'shaders/{shader_program_name}.vert') as file:
            vertex_shader = file.read()

        # Read fragment shader source
        with open(f'shaders/{shader_program_name}.frag') as file:
            fragment_shader = file.read()

        # Compile the shader program
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program

    def destroy(self):
        """
        Release all shader programs and free GPU resources.
        """
        [program.release() for program in self.programs.values()]
