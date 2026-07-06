import moderngl as mgl
import numpy as np
import glm


class BaseModel:
    """
    Base class for all renderable 3D models.

    Attributes:
        app: Reference to the main application.
        vao_name: Identifier for the vertex array object.
        tex_id: Texture ID used for the model.
        pos: Position of the model in world space.
        rot: Rotation angles (in degrees) for x, y, z axes.
        scale: Scale factors for x, y, z axes.
        m_model: Model transformation matrix.
        vao: VAO instance containing the geometry data.
        program: Shader program used for rendering.
        camera: Reference to the application's camera.
    """
    def __init__(self, app, vao_name, tex_id, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        self.app = app
        self.pos = pos
        self.vao_name = vao_name
        # Convert rotation from degrees to radians and store as glm.vec3
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale
        # Model matrix representing transformations
        self.m_model = self.get_model_matrix()
        self.tex_id = tex_id
        self.vao = app.mesh.vao.vaos[vao_name]
        self.program = self.vao.program
        self.camera = self.app.camera

    def update(self):
        """Override in child classes to update model behavior per frame."""
        ...

    def get_model_matrix(self):
        """Generate the model transformation matrix."""
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.pos)
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.scale(m_model, self.scale)
        return m_model

    def render(self):
        """Render the model using the associated VAO."""
        self.update()
        self.vao.render()


class ExtendedBaseModel(BaseModel):
    """
    An extended model class with full support for textures, lighting, and shadow rendering.

    Inherits from BaseModel and sets up additional uniforms required for:
    - Shadow mapping
    - Lighting (ambient, diffuse, specular)
    - Texture binding
    - Light-space transformations
    """

    def __init__(self, app, vao_name, tex_id, pos, rot, scale):
        """
        Initialize the extended model and prepare its resources.

        Args:
            app: Reference to the main application containing context, light, textures, and VAOs.
            vao_name: The name of the VAO representing this model's geometry.
            tex_id: Texture ID used to fetch the model's texture from the app's texture storage.
            pos: Tuple of (x, y, z) for the model's position.
            rot: Tuple of (x, y, z) for the model's rotation in degrees.
            scale: Tuple of (x, y, z) for the model's scale.
        """
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.on_init()  # Custom initialization for extended features

    def update(self):
        """
        Update the main shader uniforms every frame before drawing.

        Includes:
        - Activating the main texture
        - Updating camera and model matrices
        - Writing the camera position for lighting calculations
        """
        self.texture.use(location=0)  # Bind main texture to slot 0
        self.program['camPos'].write(self.camera.position)  # Camera world position for specular lighting
        self.program['m_view'].write(self.camera.m_view)  # Camera view matrix
        self.program['m_model'].write(self.m_model)  # Model transformation matrix

    def update_shadow(self):
        """
        Update uniforms for rendering to the shadow map.

        Only the model matrix is needed for transforming geometry into light space.
        """
        self.shadow_program['m_model'].write(self.m_model)

    def render_shadow(self):
        """
        Render the model into the shadow map.

        This is done using a separate shadow-specific shader and VAO.
        """
        self.update_shadow()
        self.shadow_vao.render()

    def on_init(self):
        """
        Initialize all shader resources, textures, and shadow-related data.

        This includes:
        - Binding light-space view matrices
        - Setting up resolution, depth texture, lighting parameters
        - Loading and binding textures and VAOs
        """
        # Set the light-space view matrix for shadow calculations
        self.program['m_view_light'].write(self.app.light.m_view_light)

        # Set screen resolution (can be used for post-processing or debugging)
        self.program['u_resolution'].write(glm.vec2(self.app.WIN_SIZE))

        # Shadow map setup: get and bind the depth texture
        self.depth_texture = self.app.mesh.texture.textures['depth_texture']
        self.program['shadowMap'] = 1  # Bind to texture unit 1
        self.depth_texture.use(location=1)

        # Retrieve the VAO used for shadow rendering
        self.shadow_vao = self.app.mesh.vao.vaos['shadow_' + self.vao_name]
        self.shadow_program = self.shadow_vao.program

        # Set the shadow shader's projection and light-view matrices
        self.shadow_program['m_proj'].write(self.camera.m_proj)
        self.shadow_program['m_view_light'].write(self.app.light.m_view_light)
        self.shadow_program['m_model'].write(self.m_model)

        # Load the model texture and bind to texture unit 0
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        self.texture.use(location=0)

        # Set model-view-projection matrices for rendering
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

        # Configure the directional/point light properties
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)  # Ambient light intensity
        self.program['light.Id'].write(self.app.light.Id)  # Diffuse light intensity
        self.program['light.Is'].write(self.app.light.Is)  # Specular light intensity


class Cube(ExtendedBaseModel):
    """
    Basic cube model with support for lighting, shadows, and texturing.

    Inherits from ExtendedBaseModel which sets up shaders, uniforms, and shadow maps.
    Can be used as a static or dynamic object in the 3D scene.
    """

    def __init__(self, app, vao_name='cube', tex_id=0,
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        """
        Initialize the cube model.

        Args:
            app: Reference to the main application object containing shared context and assets.
            vao_name: Identifier for the cube's VAO (default is 'cube').
            tex_id: ID of the texture used by the cube. Can be an int or string depending on the texture dictionary.
            pos: Position of the cube in 3D space as a tuple (x, y, z).
            rot: Rotation of the cube in degrees as a tuple (x, y, z).
            scale: Scale of the cube as a tuple (x, y, z).
        """
        super().__init__(app, vao_name, tex_id, pos, rot, scale)  # Initialize cube using base logic


class MovingCube(Cube):
    """
    Cube that updates its model matrix every frame, allowing movement or rotation animation.

    Inherits from Cube, which itself inherits from ExtendedBaseModel.
    This class recalculates the model matrix before rendering to allow dynamic transformations.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the MovingCube with positional arguments passed to the Cube constructor.
        """
        super().__init__(*args, **kwargs)

    def update(self):
        """
        Recalculate the model matrix each frame.

        This allows for animations or movement based on changes to position, rotation, or scale.
        """
        self.m_model = self.get_model_matrix()  # Recompute transformation matrix
        super().update()  # Update shader uniforms and bind texture


class Cat(ExtendedBaseModel):
    """
    A static cat model placed in the 3D world.

    This class represents a predefined model with baked texture and shadows.
    It uses a default orientation correction of -90 degrees on the X-axis to face upright.
    """

    def __init__(self, app, vao_name='cat', tex_id='cat',
                 pos=(0, 0, 0), rot=(-90, 0, 0), scale=(1, 1, 1)):
        """
        Initialize the Cat model.

        Args:
            app: Reference to the main application.
            vao_name: The name of the VAO containing cat mesh data.
            tex_id: Texture ID used for this cat.
            pos: Position in 3D space.
            rot: Rotation in degrees (default -90 on X-axis to stand upright).
            scale: Scale vector for size adjustment.
        """
        super().__init__(app, vao_name, tex_id, pos, rot, scale)


class SkyBox(BaseModel):
    """
    Standard skybox rendered around the scene.

    This implementation creates a cubemap that follows the camera's rotation 
    but not its position, giving the illusion of an infinitely distant background.
    It uses the standard view-projection matrix setup, but strips the translation 
    from the view matrix so that the skybox doesn't appear to move when the camera does.
    """

    def __init__(self, app, vao_name='skybox', tex_id='skybox',
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        """
        Initialize the SkyBox object.

        Args:
            app: Reference to the main application.
            vao_name: Name of the vertex array object for the skybox geometry.
            tex_id: Texture ID for the skybox cubemap.
            pos: World position of the skybox (usually (0, 0, 0)).
            rot: Rotation of the skybox in degrees (x, y, z).
            scale: Scale of the skybox geometry (usually large but not critical).
        """
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.on_init()  # Set up texture binding and shader uniforms

    def update(self):
        """
        Update the view matrix uniform every frame.

        The translation component is removed from the camera view matrix 
        so the skybox remains stationary in world space (i.e., it doesn't
        move when the player moves).
        """
        # Extract rotation only from the camera view matrix
        self.program['m_view'].write(glm.mat4(glm.mat3(self.camera.m_view)))

    def on_init(self):
        """
        Perform one-time initialization:
        - Bind the cubemap texture to the shader.
        - Set up projection and view matrices.
        """
        # Load the cubemap texture from the texture manager
        self.texture = self.app.mesh.texture.textures[self.tex_id]

        # Tell the shader which texture unit to use (unit 0)
        self.program['u_texture_skybox'] = 0
        self.texture.use(location=0)

        # Set projection matrix (typically stays constant)
        self.program['m_proj'].write(self.camera.m_proj)

        # Set initial view matrix without translation (rotation only)
        self.program['m_view'].write(glm.mat4(glm.mat3(self.camera.m_view)))



class AdvancedSkyBox(BaseModel):
    """
    Skybox using inverse projection-view matrix for fragment shader sampling.
    
    This version of the skybox is rendered using a shader that computes ray 
    directions in world space by multiplying the inverse of the combined 
    projection and view matrix (`m_invProjView`) with the screen-space position 
    of each fragment. This technique is often used for atmospheric scattering, 
    procedural skies, or cube map lookups in screen-space.
    """
    
    def __init__(self, app, vao_name='advanced_skybox', tex_id='skybox',
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        """
        Initialize the AdvancedSkyBox model.

        Args:
            app: Reference to the main application.
            vao_name: Name of the VAO for the skybox geometry.
            tex_id: ID of the skybox cubemap texture.
            pos: Position of the model (default is origin).
            rot: Rotation of the model in degrees (x, y, z).
            scale: Scale of the model (default is 1, 1, 1).
        """
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.on_init()  # Set up the shader and bind the skybox texture

    def update(self):
        """
        Update shader uniforms before rendering each frame.

        Specifically writes the inverse of the projection-view matrix to the
        shader so that the fragment shader can reconstruct view directions
        from screen-space coordinates.
        """
        # Extract rotation only (no translation) from the view matrix
        m_view = glm.mat4(glm.mat3(self.camera.m_view))

        # Write inverse of (projection * view) to shader uniform
        self.program['m_invProjView'].write(glm.inverse(self.camera.m_proj * m_view))

    def on_init(self):
        """
        Perform initialization routines:
        - Bind the cubemap texture to texture unit 0.
        - Set shader uniform for sampler.
        """
        # Get the cubemap texture from the texture manager
        self.texture = self.app.mesh.texture.textures[self.tex_id]

        # Bind the texture to location 0 in the shader
        self.program['u_texture_skybox'] = 0
        self.texture.use(location=0)
