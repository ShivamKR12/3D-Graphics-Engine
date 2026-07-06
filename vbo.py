import numpy as np
import moderngl as mgl
import pywavefront

class VBO:
    """
    VBO manager that initializes and stores multiple vertex buffer objects
    for different mesh types (cube, cat, skybox, etc.).
    """

    def __init__(self, ctx):
        """
        Initializes all mesh-specific VBOs.

        Args:
            ctx: The ModernGL context for GPU interaction.
        """
        self.vbos = {}
        self.vbos['cube'] = CubeVBO(ctx)
        self.vbos['cat'] = CatVBO(ctx)
        self.vbos['skybox'] = SkyBoxVBO(ctx)
        self.vbos['advanced_skybox'] = AdvancedSkyBoxVBO(ctx)

    def destroy(self):
        """Release all GPU resources associated with the VBOs."""
        [vbo.destroy() for vbo in self.vbos.values()]


class BaseVBO:
    """
    Abstract base class for VBOs. Handles common logic like VBO creation and cleanup.
    """

    def __init__(self, ctx):
        """
        Initialize a VBO using the provided rendering context.

        Args:
            ctx: ModernGL context.
        """
        self.ctx = ctx
        self.vbo = self.get_vbo()  # Create VBO from vertex data
        self.format: str = None  # Shader attribute format (e.g. '2f 3f 3f')
        self.attribs: list = None  # Attribute names expected by the shader

    def get_vertex_data(self):
        """
        Override this method in subclasses to return mesh vertex data.
        """
        ...

    def get_vbo(self):
        """Creates a GPU buffer from the vertex data."""
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def destroy(self):
        """Releases GPU memory for this VBO."""
        self.vbo.release()


class CubeVBO(BaseVBO):
    """
    VBO subclass for a cube mesh with position, normal, and texture coordinates.
    """

    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '2f 3f 3f'  # texcoord, normal, position
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

    @staticmethod
    def get_data(vertices, indices):
        """
        Converts indexed vertex data to flat arrays.

        Args:
            vertices: List of vertex tuples.
            indices: List of triangle index tuples.

        Returns:
            Numpy float32 array with flattened vertex data.
        """
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vertex_data(self):
        """
        Builds the cube vertex data including positions, normals, and texture coordinates.

        Returns:
            Combined vertex data as a float32 numpy array.
        """
        # Define cube vertices
        vertices = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                    (-1, 1, -1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]

        # Define cube triangle faces using vertex indices
        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]

        vertex_data = self.get_data(vertices, indices)

        # Texture coordinates for each face
        tex_coord_vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indices = [(0, 2, 3), (0, 1, 2),
                             (0, 2, 3), (0, 1, 2),
                             (0, 1, 2), (2, 3, 0),
                             (2, 3, 0), (2, 0, 1),
                             (0, 2, 3), (0, 1, 2),
                             (3, 1, 2), (3, 0, 1),]
        tex_coord_data = self.get_data(tex_coord_vertices, tex_coord_indices)

        # Normals per face, repeated for each triangle
        normals = [( 0, 0, 1) * 6,  # front
                   ( 1, 0, 0) * 6,  # right
                   ( 0, 0,-1) * 6,  # back
                   (-1, 0, 0) * 6,  # left
                   ( 0, 1, 0) * 6,  # top
                   ( 0,-1, 0) * 6]  # bottom
        normals = np.array(normals, dtype='f4').reshape(36, 3)

        # Combine texture, normals, and positions
        vertex_data = np.hstack([normals, vertex_data])
        vertex_data = np.hstack([tex_coord_data, vertex_data])
        return vertex_data


class CatVBO(BaseVBO):
    """
    VBO subclass that loads a 3D cat model from an OBJ file using PyWavefront.
    """

    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

    def get_vertex_data(self):
        """
        Loads and returns vertex data for the cat model from an OBJ file.

        Returns:
            Vertex data as a float32 numpy array.
        """
        objs = pywavefront.Wavefront('objects/cat/20430_Cat_v1_NEW.obj', cache=True, parse=True)
        obj = objs.materials.popitem()[1]
        vertex_data = obj.vertices
        vertex_data = np.array(vertex_data, dtype='f4')
        return vertex_data


class SkyBoxVBO(BaseVBO):
    """
    VBO subclass for a cube-based skybox (positions only, no texcoords or normals).
    """

    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f'
        self.attribs = ['in_position']

    @staticmethod
    def get_data(vertices, indices):
        """
        Flattens indexed geometry into raw vertex data.

        Args:
            vertices: List of vertex positions.
            indices: List of triangle indices.

        Returns:
            Numpy float32 array of vertex positions.
        """
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vertex_data(self):
        """
        Generates vertex data for a cube used as the skybox.

        Returns:
            Vertex position data as float32 numpy array.
        """
        vertices = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                    (-1, 1, -1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]
        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]

        vertex_data = self.get_data(vertices, indices)

        # Flip axes to correct winding order / skybox orientation
        vertex_data = np.flip(vertex_data, 1).copy(order='C')
        return vertex_data


class AdvancedSkyBoxVBO(BaseVBO):
    """
    VBO for advanced skybox rendering using a full-screen triangle in clip space.
    """

    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f'
        self.attribs = ['in_position']

    def get_vertex_data(self):
        """
        Returns the coordinates of a fullscreen triangle in clip space.

        Returns:
            A numpy float32 array of 3 vertices covering the screen.
        """
        z = 0.9999  # Push near far plane for correct depth
        vertices = [(-1, -1, z), (3, -1, z), (-1, 3, z)]  # Covers full screen triangle
        vertex_data = np.array(vertices, dtype='f4')
        return vertex_data
