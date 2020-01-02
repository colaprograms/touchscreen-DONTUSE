uniform mat4 p3d_ModelViewProjectionMatrix;

varying vec4 texCoords;

void main(void) {
    vec4 test = gl_Vertex;

    //By adding 1 to z we move our grid to make a cube.
    //We do 1 instead of 0.5 to make all the math easy.
    test.z = test.z + 1.0;

    //While this simple normalizing works it causes some distortion near the edges
    //While less distoration than a standard sphere there are more ideal solutions
    //gl_Position = p3d_ModelViewProjectionMatrix * vec4(normalize(test.xyz), test.w);
    
    //The normalization creates almost no edge distortion
    //Proof: http://mathproofs.blogspot.com/2005/07/mapping-cube-to-sphere.html
    float x = test.x;
    float y = test.y;
    float z = test.z;
    test.x *= sqrt(1.0 - y * y * 0.5 - z * z * 0.5 + y * y * z * z / 3.0);
    test.y *= sqrt(1.0 - z * z * 0.5 - x * x * 0.5 + z * z * x * x / 3.0);
    test.z *= sqrt(1.0 - x * x * 0.5 - y * y * 0.5 + x * x * y * y / 3.0);
    gl_Position = p3d_ModelViewProjectionMatrix * test;

    gl_FrontColor = gl_Color;
    texCoords = gl_MultiTexCoord0;
}

