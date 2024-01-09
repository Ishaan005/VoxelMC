from settings import *
import moderngl as mgl
import pygame as pg
import sys
from shader_program import ShaderProgram
from scene import Scene
from player import Player
from textures import Textures

import pygame.freetype


class VoxelEngine:
    def __init__(self):
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)

        pg.display.set_mode(pg.display.get_desktop_sizes()[
                            0], flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.time = 0

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        self.is_running = True
        self.on_init()

    def on_init(self):
        self.textures = Textures(self)
        self.player = Player(self)
        self.shader_program = ShaderProgram(self)
        self.scene = Scene(self)

        #fps stuff
        pygame.freetype.init()
        self.font = pygame.freetype.Font(None, 24)

        # fps shader program
        self.fps_program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 texcoord;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                texcoord = in_texcoord;
            }
            """,
            fragment_shader="""
            #version 330
            uniform sampler2D tex;
            in vec2 texcoord;
            out vec4 out_color;
            void main() {
                out_color = texture(tex, texcoord);
            }
            """
        )

        #vertex buffer for fps
        self.fps_vbo = self.ctx.buffer(np.array([
            -0.98,  0.96, 0.0, 1.0,
            -0.96,  0.96, 1.0, 1.0,
            -0.96,  0.98, 1.0, 0.0,
            -0.98,  0.98, 0.0, 0.0,
        ], dtype='f4').tobytes())

        # certex array for fps  
        self.fps_vao = self.ctx.simple_vertex_array(self.fps_program, self.fps_vbo, 'in_vert', 'in_texcoord')

    def update(self):
        self.player.update()
        self.shader_program.update()
        self.scene.update()

        self.delta_time = self.clock.tick()
        self.time = pg.time.get_ticks() * 0.001

    def display_fps(self):
        #FPS text to a surface
        surface_fps, _ = self.font.render(f'{self.clock.get_fps() :.0f}', (255, 255, 255))

        # surface to a texture
        texture_data_fps = pygame.image.tostring(surface_fps, 'RGBA')
        texture_fps = self.ctx.texture(surface_fps.get_size(), 4, texture_data_fps)

        #texture to the screen
        self.fps_program['tex'].value = 3
        texture_fps.use(location=3)
        self.fps_vao.render(mgl.TRIANGLE_FAN)

    def render(self):
        self.ctx.clear(color=BG_COLOR)
        self.scene.render()
        self.display_fps()
        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.is_running = False
            self.player.handle_event(event=event)

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()

        pg.quit()
        sys.exit()

if __name__ == '__main__':
    app = VoxelEngine()
    app.run()
