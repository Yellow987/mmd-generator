#!/usr/bin/env python
# coding: utf-8

import time
import os
import pymeshio.pmd.reader
import opengl.material
import opengl.texture
import opengl.vertexarray


def build(path):
    # load scenee
    print('read %s...' % path)
    t=time.time()
    model=pymeshio.pmd.reader.read_from_file(path)
    if not model:
        return
    print(time.time()-t, "sec")

    # build
    print('build vertexarray...')
    t=time.time()
    basedir=os.path.dirname(path)
    indexedVertexArray=opengl.vertexarray.IndexedVertexArray()
    for v in model.vertices:
        # left-handed y-up to right-handed y-up                
        indexedVertexArray.addVertex(
                (v.pos[0], v.pos[1], -v.pos[2], 1), 
                (v.normal[0], v.normal[1], -v.normal[2]), 
                (v.uv[0], v.uv[1]), 
                (1, 1, 1, 1),
                v.bone0, v.bone1, v.weight0)
    
    indexedVertexArray.setIndices(model.indices)

    # material
    textureMap={}
    for i, m in enumerate(model.materials):
        material=opengl.material.MQOMaterial()
        material.vcol=True
        material.rgba=(
                m.diffuse_color[0], 
                m.diffuse_color[1], 
                m.diffuse_color[2], 
                m.alpha)
        material.vertex_count=m.vertex_count
        texturefile=m.texture_file.decode('cp932')
        texturepath=os.path.join(basedir, texturefile)
        if os.path.isfile(texturepath):
            if not texturepath in textureMap:
                texture=opengl.texture.Texture(texturepath)
                textureMap[texturepath]=texture
            material.texture=textureMap[texturepath]
        indexedVertexArray.addMaterial(material)

    #indexedVertexArray.optimize()
    indexedVertexArray.create_vbo()
    return indexedVertexArray
