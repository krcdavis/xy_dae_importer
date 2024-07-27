import os
import bpy
import mathutils

#today's folder
folder = "12 rt11"

pathto = os.path.join("C:\\Users\\Kat\\0xwhy\\a041 stuff",folder)
#C:\\Users\\Kat\\0xwhy\\a041 stuff

# put the location to the folder where the objs are located here in this fashion
# this line will only work on windows ie C:\objects

# get list of all files in directory
file_list = sorted(os.listdir(pathto))
# get a list of files ending in 'dae'
daelist = [item for item in file_list if item.endswith('.dae')]
# loop through the strings in obj_list and add the files to the scene
mats = ""
for item in daelist:
    path_to_file = os.path.join(pathto, item)
    #create collection and derive location from filename, accounting for enc files...
    loc = item[:-4]#no .dae
    colname = ""
    if loc[-1] == 'c':#enc
        colname = loc
        loc = loc[:-4]#no _enc
    else:
        colname = loc
    loc = loc[-5:]
    collection = bpy.data.collections.new(name=colname)
    scene_collection = bpy.context.scene.collection
    scene_collection.children.link(collection)
    #loc is now xx_yy, really just 0x_0y or 1x_1y
    xval = int(loc[1])*720
    yval = int(loc[4])*-720
    bpy.ops.wm.collada_import(filepath = path_to_file)
    #bpy.ops.transform.translate moves selected, do outside loop
    bpy.ops.transform.translate(value=(xval, yval, 0.0))
    # if heavy importing is expected 
    # you may want use saving to main file after every import
    #bpy.ops.wm.save_mainfile(filepath = "S:\\Godisfabriken_Unity_2019_01\\OARS\\Gavle100k_10--2019-01-09.blend")
    
    #apparently all imported items are already selected, so...
    for ob in bpy.context.selected_objects:
      collection.objects.link(ob)
      #sometimes you need this, sometimes you don't... i don't get it
      bpy.data.collections['Collection'].objects.unlink(ob)
      
      #ob.location = ob.location + mathutils.Vector((xval,yval,0))
      
      #mehtoriels
      #bpy.context.active_object.data.materials.items() workls
      if ob.type == 'MESH':#no armatures, no turpenes
          m = ob.data.materials.items()[0][0]#there shouldn't be anything else...
          #all names end in _mat. if ends in .001, .002 etc, truncate to get name of
          #"real" material and reassign... somehow
          if m[-3] == '0':
              #look for existing mat and replace if found
              mm = m[:-4]
              mat = bpy.data.materials.get(mm)
              if mat is None:#it shouldn't be, but...
                  print("error "+m)
              else:
                  ob.data.materials[0] = mat
          else:
            #add material name to some sort of list for later use
            
            #and ...
            #first: attempt to find texture by material name.
            im = m[:-4] + ".png"
            #if not in folder, try subfolders, if there move up... somehow
            imgp = ""#need to declare it up here
            if os.path.isfile( os.path.join(pathto, im) ):
                imgp = os.path.join(pathto, im)
            else:#... i'll do it later
                dirs = [name for name in os.listdir(pathto)
                        if os.path.isdir(os.path.join(pathto, name))]
                for d in dirs:
                    if os.path.isfile( os.path.join(pathto, d, im) ):
                        imgp = os.path.join(pathto, d, im)
                        break#no need to search any other dirs... there shouldn't be more anyway

            if imgp:
                #mats
                img = bpy.data.images.load( imgp )
                mats += m + " found\n"
                #and set up the material.
                mat = ob.data.materials.items()[0][1]
                mat.blend_method = 'CLIP'#IT'S WORKING
                
                # Get the nodes
                nodes = mat.node_tree.nodes
                #nuke the nodes
                nodes.clear()
                
                # Add back the Principled Shader node that i just nuked because it's easier than finding the existing one I guess
                node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
                node_principled.location = 0,0
                
                # Add the Image Texture node
                node_tex = nodes.new('ShaderNodeTexImage')
                # Assign the image
                node_tex.image = img
                node_tex.location = -400,0
                
                # Add the Output node
                node_output = nodes.new(type='ShaderNodeOutputMaterial')   
                node_output.location = 400,0

                # Link all nodes
                links = mat.node_tree.links
                link = links.new(node_tex.outputs["Color"], node_principled.inputs["Base Color"])
                #alpha...
                link = links.new(node_tex.outputs["Alpha"], node_principled.inputs["Alpha"])
                link = links.new(node_principled.outputs["BSDF"], node_output.inputs["Surface"])
                
                
            else:
                mats += m + " !!!NOT FOUND!!!\n"
                          

    for m in mats:
        #im = m[] + ".png"
        #img = bpy.data.images.load( os.path.join(pathto, im) )
        #folder, mat name replacing _mat with .png...
        pass
    file = open(pathto + "\\mats.txt", 'w', encoding = 'utf8')
    print(mats, file=file)
    file.close()

##
