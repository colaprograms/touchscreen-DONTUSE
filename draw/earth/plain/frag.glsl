#version 130

uniform sampler2D p3d_Texture0;
varying vec2 texture_coordinate;
varying vec4 texCoords;

out vec4 FragColor;

void main(void)
{
    vec4 color = texture(p3d_Texture0, texCoords.xy);
    FragColor = color;
}

