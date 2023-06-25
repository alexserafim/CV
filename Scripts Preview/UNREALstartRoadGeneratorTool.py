from typing import List, Any
import unreal
import os

# houActorFolderPath = "RoadGeneratorHDA"
slowTaskDisplay = "Importing splines to Houdini!"


# Create array with actors by class BP_SplineRoad_C
def getRoadSplineBP():
    bp_actors = []
    all_actors = unreal.EditorActorSubsystem().get_all_level_actors()
    for a in all_actors:
        check_is_BP_class = a.get_class().get_name()
        if check_is_BP_class == 'BP_SplineRoad_C':
            bp_actors.append(a)
        else:
            continue
    return bp_actors


# reformat correct property SelectedRoadMeshType
def enumNameConvert(enum_name):
    name_list = enum_name.split('_')
    new_enum_name_list = []
    for n in name_list:
        if len(n) != 1:
            temp_part_name = n.capitalize()
            new_enum_name_list.append(temp_part_name)
    splitter = ''
    new_enum_name = splitter.join(new_enum_name_list)
    return new_enum_name


# function for rename label of BP_SplineRoad
def renameRoadSplineBP(bp_actors):
    old_name = ''
    correct_name = ''
    enumPropertysNames = ('MainRoad', 'AdditionalRoad', 'DirtRoad', 'TrailRoad', 'RailwayRoad')
    for i, bp in enumerate(bp_actors):
        old_name = bp.get_actor_label()
        # get sufix stored road type
        splitted_old_name = old_name.split('_')[-2]
        # check actor label is renamed
        if splitted_old_name in enumPropertysNames:
            unreal.log('Lable of this actor is correct!')
            break
        else:
            enum_property = bp.get_editor_property('SelectedRoadMeshType')
            if not enum_property:
                unreal.log_error('This BP, dont have %s property!', str(enum_property))
            else:
                enum_name = enum_property.name
                correct_enum_name = enumNameConvert(enum_name)
                correct_name = '_'.join((old_name, correct_enum_name)) + '_' + str(i)
                bp.set_actor_label(correct_name, mark_dirty=True)
                unreal.log(correct_name)


# get data from actors BP_SplineRoad and create txt file
def getRoadSplineData(bp_actors):
    work_path_env = 'Techart'
    path_file_env = ''
    if not os.environ[work_path_env]:
        unreal.log_error('Environment variable %s is not define!' % work_path_env)
    else:
        path_file_env = os.environ.get(work_path_env)

    path_file = os.path.join(path_file_env, 'Hafiatullov_RoadGen/data_file')
    file_pn = '/data_from_ue.txt'
    data_file = open(path_file + file_pn, 'w')
    actors = bp_actors

    for actor in actors:
        # get unique name_id actors from editor
        actor_path = actor.get_path_name()
        splited_path_actor = actor_path.split('.')
        splited_path_actor.reverse()
        non_clear_name_id = splited_path_actor[0]
        temp_ac_name_id = non_clear_name_id.split("'")
        actor_unique_id = temp_ac_name_id[0]
        # get label actors from editor
        actor_label = actor.get_actor_label()
        # add data to file
        data = data_file.write(actor_unique_id + ':' + actor_label + '\n')
    data_file.close()
    os.startfile(path_file + file_pn)
    unreal.log('File with RoadSpline data from UE for Houdini is done!')


def get_roadGen_hda_path():
    # return '/Game/_Stalker_2/HDA/Road_Generator/oh__RoadGenerator_LD__2_0.oh__RoadGenerator_LD__2_0'
    return '/Game/_Stalker_2/HDA/Road_Generator/oh__RoadGenerator__2_0.oh__RoadGenerator__2_0'


def get_roadGen_hda():
    asset = unreal.EditorAssetLibrary.does_asset_exist(get_roadGen_hda_path())
    if not asset:
        return unreal.log_error('Asset RoadGenerator located on %s isn`t found!' % (get_roadGen_hda_path()))
    else:
        return unreal.load_object(None, get_roadGen_hda_path(), )


def get_api():
    api = unreal.HoudiniPublicAPIBlueprintLib.get_api()
    return api

# function for activate AdjustToLandscape after deformation of splines
def auto_adjust_landscape_activate(bp_actors):
    actors = bp_actors
    for actor in actors:
        activate = actor.get_editor_property('setNewSplineComponent')
        live_landscape_change = actor.get_editor_property('LiveLandscapeChange')
        if not live_landscape_change:
            actor.set_editor_property('LiveLandscapeChange', True)
            unreal.log_warning('LiveLandscapeChange is activated!')
        if not activate:
            actor.set_editor_property('setNewSplineComponent', True)
            unreal.log_warning('Auto adjust to landscape to spline is activated!')
    return True

def get_post_cooking_result(in_wrapper):
    comp = in_wrapper.get_houdini_asset_component()
    child_count = comp.get_num_children_components()
    if child_count > 0:
        return True
    else:
        return False


def on_pre_instantiation(in_wrapper):
    unreal.log('on_pre_instantiation')
    # Unbind from the delegate
    in_wrapper.on_pre_instantiation_delegate.remove_callable(on_pre_instantiation)
    unreal.log('set_parameters')
    # set parameters
    in_wrapper.set_int_parameter_value('cells_mode', 0)
    in_wrapper.set_int_parameter_value('cell_num', 1)
    # in_wrapper.set_int_parameter_value('cells_mode', 1)
    # in_wrapper.set_int_parameter_value('intrange_range_cells', 0, 0)
    # in_wrapper.set_int_parameter_value('intrange_range_cells', 17, 1)
    in_wrapper.set_bool_parameter_value('switch_geo_type', True)
    # in_wrapper.set_bool_parameter_value('manual_select', True)
    in_wrapper.set_int_parameter_value('geo_type', 1)
    # unreal.log('Parameters {}, {}, {}, is setting!'.format('cells_mode', 'intrange_range_cells', 'geo_type'))
    # Cook the HDA (not PDG yet)
    in_wrapper.recook()


def on_post_instantiation(in_wrapper):
    print('on_post_instantiation')
    print('configure_inputs')
    # Unbind from the delegate
    in_wrapper.on_post_instantiation_delegate.remove_callable(on_post_instantiation)
    # Get some actors
    # actors = getRoadSplineBP()
    # Create a world input
    world_input = in_wrapper.create_empty_input(unreal.HoudiniPublicAPIWorldInput)
    # Get some actors
    actors = getRoadSplineBP()
    # Set the input objects/assets for this input
    world_input.set_input_objects(actors)
    # copy the input data to the HDA as node input 0
    in_wrapper.set_input_at_index(0, world_input)
    # Cook the HDA (not PDG yet)
    in_wrapper.recook()


def on_post_process(in_wrapper):
    print('on_post_process')
    # Unbind from the delegate
    in_wrapper.on_post_processing_delegate.remove_callable(on_post_process)

    # Iterate over all PDG/TOP networks and nodes and log them
    print('TOP networks:')
    for network_path in in_wrapper.get_pdgtop_network_paths():
        print('\t{}'.format(network_path))
        for node_path in in_wrapper.get_pdgtop_node_paths(network_path):
            print('\t\t{}'.format(node_path))

    # Enable PDG auto-bake (auto bake TOP nodes after they are cooked)
    # in_wrapper.set_pdg_auto_bake_enabled(True)
    # unreal.log_warning('Auto bake is enabled!')
    # Cook the specified TOP node
    cooking_is = in_wrapper.pdg_cook_node('HE_topnet_road_gen', '_output')
    #
    # cooking_is = in_wrapper.pdg_cook_outputs_for_network('HE_topnet_road_gen')
    if cooking_is:
        unreal.log_warning('Cooking is started')


def on_post_cook(in_wrapper, success):
    # Unbind from the delegate
    in_wrapper.on_post_pdgtop_network_cook_delegate.remove_callable(on_post_cook)
    # Bake all outputs to actors
    unreal.log('cook complete ... {}'.format('success' if success else 'failed'))
    # get count cooked components of HoudiniAsset
    # post_cook_result = get_post_cooking_result(in_wrapper)
    if success:
        # baked_is = in_wrapper.pdg_bake_all_outputs()
        # bake only selected output node of current top network
        baked_is = in_wrapper.pdg_bake_all_outputs_with_settings(
            bake_option=unreal.HoudiniEngineBakeOption.TO_ACTOR,
            bake_selection=unreal.PDGBakeSelectionOption.SELECTED_NETWORK,
            bake_replacement_mode=unreal.PDGBakePackageReplaceModeOption.REPLACE_EXISTING_ASSETS,
            recenter_baked_actors=False)
        unreal.log('baking all outputs to actors')
        if baked_is:
            unreal.log('Baking is started!')
        else:
            unreal.log_warning('Baking doesnt started!')


def show_message():
    header = unreal.Text.cast("Road Generation")
    mess = unreal.Text.cast("Generation is over!")
    return unreal.EditorDialog.show_message(header, mess, unreal.AppMsgType.OK, unreal.AppReturnType.OK)

def on_post_pdg_bake(in_wrapper, success):
    # Unbind from the delegate
    in_wrapper.on_post_pdg_bake_delegate.remove_callable(on_post_pdg_bake)
    print('bake complete ... {}'.format('success' if success else 'failed'))
    bp_actors = getRoadSplineBP()
    # activate AdjustLandscape after deformation of splines after baking geometry
    activate = auto_adjust_landscape_activate(bp_actors)

    if activate:
        # Show completion message
        mes = show_message()
        if mes.value == 5:
            is_dirty = in_wrapper.pdg_dirty_network('HE_topnet_road_gen')
            if is_dirty:
                print('Topnet {} is dirty'.format('HE_topnet_road_gen'))
        #     #Delete the hda after the bake
            in_wrapper.delete_instantiated_asset()
            global _g_wrapper
            _g_wrapper = None

def run():
    global _g_wrapper

    bp_actors: list[Any] = getRoadSplineBP()
    renameRoadSplineBP(bp_actors)
    renamed_bp_actors: list[Any] = getRoadSplineBP()
    getRoadSplineData(renamed_bp_actors)
    hda_asset = get_roadGen_hda()

    # get the API singleton
    api = get_api()
    # Check if there is an existing valid session
    if not api.is_session_valid():
        # Create a new session
        api.create_session()

    if not hda_asset:
        unreal.log_error('Asset RoadGenerator located on %s isn`t found!' % (get_roadGen_hda_path()))
    else:
        # instantiate an asset with auto-cook enabled
        _g_wrapper = api.instantiate_asset(hda_asset, unreal.Transform(), enable_auto_cook=False)
        # Configure several parameters before first cook
        _g_wrapper.on_pre_instantiation_delegate.add_callable(on_pre_instantiation)
        # Configure inputs on_post_instantiation, after instantiation, but before first cook
        _g_wrapper.on_post_instantiation_delegate.add_callable(on_post_instantiation)
        # Cook the specified TOP node
        _g_wrapper.on_post_processing_delegate.add_callable(on_post_process)
        #
        _g_wrapper.on_post_pdgtop_network_cook_delegate.add_callable(on_post_cook)
        #
        _g_wrapper.on_post_pdg_bake_delegate.add_callable(on_post_pdg_bake)

if __name__ == '__main__':
    run()