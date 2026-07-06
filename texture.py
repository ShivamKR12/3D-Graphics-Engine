import pygame as pg
import moderngl as mgl
import glm

class Texture:
    """
    Manages all textures used in the application, including 2D textures,
    cubemaps for skyboxes, and depth textures for shadow mapping.
    """

    def __init__(self, app):
        """
        Initialize the texture manager and load all required textures.

        Args:
            app: The main application instance.
        """
        self.app = app
        self.ctx = app.ctx
        self.textures = {}

        # Load 2D textures with numeric keys
        self.textures[0] = self.get_texture(path='textures/img.png')
        self.textures[1] = self.get_texture(path='textures/img_1.png')
        self.textures[2] = self.get_texture(path='textures/img_2.png')

        # Load a specific texture for the cat model
        self.textures['cat'] = self.get_texture(path='objects/cat/20430_cat_diff_v1.jpg')

        # Load a cubemap texture for the skybox
        self.textures['skybox'] = self.get_texture_cube(dir_path='textures/skybox1/', ext='png')

        # Create a depth texture used for shadow mapping
        self.textures['depth_texture'] = self.get_depth_texture()

        # Create a color texture for the main scene framebuffer (for post-processing)
        self.textures['scene_texture'] = self.get_scene_texture()

        # Create textures for the bloom effect (at half resolution)
        self.textures['bloom_texture_1'] = self.get_scene_texture(scale_factor=0.5)
        self.textures['bloom_texture_2'] = self.get_scene_texture(scale_factor=0.5)

    def get_depth_texture(self):
        """
        Create a depth texture for shadow mapping.

        Returns:
            A depth texture object.
        """
        depth_texture = self.ctx.depth_texture(self.app.WIN_SIZE)

        # Disable texture repeating (clamp to edge)
        depth_texture.repeat_x = False
        depth_texture.repeat_y = False

        return depth_texture

    def get_scene_texture(self, scale_factor=1.0):
        """
        Create a color texture to render the main scene to.

        Args:
            scale_factor (float): Factor to scale the texture size relative to the window.

        Returns:
            A 2D texture object.
        """
        size = (int(self.app.WIN_SIZE[0] * scale_factor), int(self.app.WIN_SIZE[1] * scale_factor))
        texture = self.ctx.texture(size, 4, dtype='f2') # Use 16-bit float (2 bytes) for HDR
        texture.filter = (mgl.LINEAR, mgl.LINEAR)
        return texture

    def get_texture_cube(self, dir_path, ext='png'):
        """
        Load a cubemap texture from a directory containing 6 images.

        Args:
            dir_path (str): Directory path where cube face textures are stored.
            ext (str): Image file extension.

        Returns:
            A compiled cube map texture.
        """
        # Define the cube map face order
        faces = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]

        textures = []
        for face in faces:
            # Load texture image
            texture = pg.image.load(dir_path + f'{face}.{ext}').convert()

            # Flip based on orientation
            if face in ['right', 'left', 'front', 'back']:
                texture = pg.transform.flip(texture, flip_x=True, flip_y=False)
            else:
                texture = pg.transform.flip(texture, flip_x=False, flip_y=True)

            textures.append(texture)

        size = textures[0].get_size()

        # Create an empty cubemap texture
        texture_cube = self.ctx.texture_cube(size=size, components=3, data=None)

        # Write each face into the cubemap
        for i in range(6):
            texture_data = pg.image.tostring(textures[i], 'RGB')
            texture_cube.write(face=i, data=texture_data)

        return texture_cube

    def get_texture(self, path):
        """
        Load a 2D texture from an image file and apply filtering.

        Args:
            path (str): Path to the image file.

        Returns:
            A ModernGL texture object.
        """
        # Load and vertically flip the image
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)

        # Create the ModernGL texture
        texture = self.ctx.texture(
            size=texture.get_size(),
            components=3,
            data=pg.image.tostring(texture, 'RGB')
        )

        # Enable mipmapping for smoother transitions at distance
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()

        # Enable anisotropic filtering for higher quality at oblique angles
        texture.anisotropy = 32.0

        return texture

    def destroy(self):
        """
        Release all GPU texture resources.
        """
        [tex.release() for tex in self.textures.values()]
