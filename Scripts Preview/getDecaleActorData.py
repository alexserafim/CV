import unreal
import os
import math


path_file = 'g:/Shared drives/TechArt/Houdini_hda/Hafiatullov_RoadGen/data_file'
full_path_file = path_file + '/decal_data_from_ue.txt'
data_file = open(full_path_file, 'w')

data = ()
tag = 0
actors = unreal.EditorLevelLibrary.get_selected_level_actors()
# function which represent vector values from UE
def representVector(object_vector):
	represent_vec = str(object_vector.x), str(object_vector.y), str(object_vector.z)
	represent_vec = str(object_vector.x) + ',' + str(object_vector.y) + ',' + str(object_vector.z)
	return represent_vec
	# a = []
	# for i in represent_vec:
	# 	component = float(i)
	# 	a.append(component)
	# return a

def getDecaleTextureSize(decal_actor, ratio_sides):
	decal = decal_actor.decal
	decal_mat = decal.decal_material
	decal_name = decal_mat.get_full_name()
	decal_tex = decal_mat.texture_parameter_values[0].parameter_value
	# begin fix case with default textures
	decals_tex = decal_mat.texture_parameter_values
	
	decal_tex = 0
	if len(decals_tex) <= 2:
		decal_tex = decal_mat.texture_parameter_values[0].parameter_value
	else:
		decal_tex = decal_mat.texture_parameter_values[1].parameter_value
	print(decal_tex)
	# end fix

	sizeX = decal_tex.blueprint_get_size_x()
	sizeY = decal_tex.blueprint_get_size_y()
	
	max_size = max(sizeX, sizeY)
	u = ratio_sides.append(1/(max_size//sizeX))
	v = ratio_sides.append(1/(max_size//sizeY))
	
	
	#print(ratio_sides)
	res = (sizeX, sizeY)
	return str(res)

# searching file texture in source folder
current_folder = r'G:\Shared drives\_Stalker_2_Art\textures\decals' # path to folder with decales
searched_file_name = ''

def searchedFile(root, searched_file):
	textures = list()
	for rootdir, dirs, files in os.walk(current_folder):
		if rootdir.find('OLD') < 0 or rootdir.find('old') < 0:
			for file in files:
				file_name = os.path.splitext(file)[0]
				if file_name == searched_file:
					item = os.path.normpath(os.path.join(rootdir, file))
					textures.append(item)
				
		if len(textures):
			searched_path = textures[0]
			return searched_path

####################################################

for i, actor in enumerate(actors):
	actor_type = actors[i].get_class().get_path_name().split(".")[1]
	if actor_type == 'DecalActor':
		# get actor label
		label = actor.get_actor_label()
		# get actor path
		actor_path = actor.get_path_name()
		# get actor relative scale
		actor_rel_scale = actor.get_actor_relative_scale3d()
		# get actor decal size	
		actor_dec_size = unreal.DecalComponent(actor).decal_size
		# measure object scale
		actor_scale = str(representVector(actor_rel_scale * actor_dec_size * 0.01))
		# get actor material path
		actor_dec_mat = actor.get_decal_material().get_full_name()
		# make reference path to decale material instance
		mat_path = actor_dec_mat.split(' ')
		mat_ref_path = mat_path[0] + "'" + mat_path[1] + "'"
		# get texture size
		ratio_sides = []
		texture_size = getDecaleTextureSize(actor, ratio_sides)
		ratio = (str(ratio_sides[0]) + ',' + str(ratio_sides[1]))
		# get path to source file texture
		decal = actor.decal
		decal_mat = decal.decal_material
		decal_tex = decal_mat.texture_parameter_values[0].parameter_value
		searched_file_name = decal_tex.get_name()
		path_to_tex = searchedFile(current_folder, searched_file_name)
		# get decal
		actor_dec = actor.decal
		# get actor tag
		tag = actor_dec.component_tags
		
		if len(tag) > 0:
			ntag = str(tag[0]) + "_" + str(i)
			nntag = str(tag[0])
			if len(tag) == 1:
				data = data_file.write(ntag + ':' + 'DecalActor' + ':' + mat_ref_path + ':' + actor_scale + ':' + texture_size + ':' + ratio + ':' + nntag + ':' + path_to_tex + '\n')
			else:
				nnntag = str(tag[1])
			# add data to file
				data = data_file.write(ntag + ':' + 'DecalActor' + ':' + mat_ref_path + ':' + actor_scale + ':' + texture_size + ':' + ratio + ':' + nntag + ':' + path_to_tex + ':' + nnntag + '\n')
		else:
			print('You didnt set a tag for the DecalActor for:', label)

	elif actor_type == 'StaticMeshActor':
		# get actor label
		label = actor.get_actor_label()
		# get actor path
		mesh_path = actor.static_mesh_component.static_mesh.get_path_name()
		mesh_ref_path = 'StaticMesh' + "'" + mesh_path + "'"
		#get actor size
		half_size = actor.static_mesh_component.static_mesh.get_bounds().box_extent
		full_size = str(representVector(half_size * (0.02, 0.02, 0.02)))
		# get actor relative scale
		actor_scale = str(representVector(actor.get_actor_relative_scale3d()))
		# get actor tag
		tag = actor.tags
		
		if len(tag) > 0:
			ntag = str(tag[0]) + "_" + str(i)
			nntag = str(tag[0])
			# add data to file
			data = data_file.write(ntag + ':' + 'StaticMesh' + ':' + mesh_ref_path + ':' + full_size + ':' + nntag + '\n')
		else:
			print('You didnt set a tag for the actor:', label)
	
data_file.close()

# rename file
split_file_name = os.path.splitext(full_path_file)
new_file_name = split_file_name[0] + '_' + str(tag[0]) + split_file_name[1]
file_is = os.path.isfile(full_path_file) 
new_file = os.replace(full_path_file, new_file_name)
# check empty file
if bool(os.path.getsize(new_file_name)):
 	os.startfile(new_file_name)
else:
	print('File is empty!!!')
	pass