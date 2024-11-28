import hou
import os

# Dictionnaire des types de textures et de leurs noms associés
texture_types = {
    "BASE_COLOR": ["diff", "dif", "basecolor", "base color", "base_color", "albedo", "alb", "diffuse", "color", "col"],
    "SPECULAR_ROUGHNESS": ["roughness", "gloss", "glossiness", "rough", "specular", "spec", "roughnessmap", "specmap"],
    "NORMAL": ["normal", "normalmap", "normals", "bump", "norm", "bumpmap"],
    "DISPLACEMENT": ["displacement", "height", "disp", "dis", "heightmap"],
    "OPACITY": ["opacity", "alpha", "transparent", "transparency", "mask"],
    "METALNESS": ["metal", "metalness", "mtl", "metallic", "metalnessmap"],
    "AMBIENT_OCCLUSION": ["ao", "ambientocclusion", "occlusion"],
    "EMISSIVE": ["emissive", "emit", "emission"]
}

# Fonction pour déterminer le type de texture en fonction du nom du fichier
def get_texture_type(file_name):
    for texture_type, keywords in texture_types.items():
        for keyword in keywords:
            if keyword in file_name.lower():
                return texture_type
    return None

# Fonction pour créer un nœud avec un paramètre 'file' à l'intérieur du nœud sélectionné
def create_node_with_file(selected_node, node_type, image_path, node_name=None):
    try:
        node = selected_node.createNode(node_type)
        if node is not None:
            if node_name:
                node.setName(node_name, unique_name=True)
            else:
                node.setName(os.path.basename(image_path), unique_name=True)
            filename_parm = node.parm('file')
            if filename_parm is not None:
                filename_parm.set(image_path)
                return node
            else:
                return None
        else:
            return None
    except Exception as e:
        hou.ui.displayMessage(f"Error creating {node_type} node: {e}")
        return None

# Fonction pour créer un nœud mtlximage à l'intérieur du nœud sélectionné
def create_mtlximage_in_selected_node(selected_node, image_path, texture_type):
    return create_node_with_file(selected_node, 'mtlximage', image_path)

# Obtenir le premier nœud sélectionné
selected_nodes = hou.selectedNodes()
if not selected_nodes:
    hou.ui.displayMessage("Please select a node.")
else:
    selected_node = selected_nodes[0]  # Prend le premier nœud sélectionné
    # Créer le nœud mtlxstandard_surface s'il n'existe pas
    mtlx_standard_surface_node = selected_node.node('mtlxstandard_surface')
    if not mtlx_standard_surface_node:
        mtlx_standard_surface_node = selected_node.createNode('mtlxstandard_surface')
        mtlx_standard_surface_node.setName('mtlxstandard_surface', unique_name=True)
    # Demander à l'utilisateur de choisir un dossier
    folder_path = hou.ui.selectFile(start_directory='/', file_type=hou.fileType.Directory, title='Select Folder')
    if folder_path:
        # Extraire le nom du dossier à partir du chemin du dossier sélectionné
        folder_name = os.path.basename(os.path.normpath(folder_path))

        # Renommer le noeud principal sélectionné avec le nom du dossier
        selected_node.setName(folder_name, unique_name=True)

        # Scanner tous les fichiers images dans le dossier
        image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.exr', '.tif', '.tiff'))]

        if not image_files:
            hou.ui.displayMessage("No image files found in the selected folder.")
        else:
            # Variable pour compter le nombre de textures créées
            texture_count = 0

            # Créer un nœud pour chaque fichier image
            for image_file in image_files:
                image_path = os.path.join(folder_path, image_file)
                texture_type = get_texture_type(image_file)
                if texture_type is not None:
                    if texture_type == "NORMAL":
                        # Créer mtlxgltf_normalmap
                        mtlxgltf_normalmap_node = create_node_with_file(selected_node, 'mtlxgltf_normalmap', image_path, node_name=image_file + '_gltf_normalmap')
                        if mtlxgltf_normalmap_node:
                            mtlxgltf_normalmap_node.setComment(texture_type)
                            mtlxgltf_normalmap_node.parm("filecolorspace").set("Raw")
                            # Créer mtlxnormalmap
                            normal_map_node = selected_node.createNode("mtlxnormalmap")
                            normal_map_node.setName(image_file + "_normalmap", unique_name=True)
                            normal_map_node.setInput(0, mtlxgltf_normalmap_node)
                            # Connecter au mtlxstandard_surface
                            mtlx_standard_surface_node.setInput(40, normal_map_node)
                            texture_count += 1
                        else:
                            hou.ui.displayMessage(f"Failed to create mtlxgltf_normalmap node for {image_file}")
                    else:
                        image_node = create_mtlximage_in_selected_node(selected_node, image_path, texture_type)
                        if image_node:
                            image_node.setComment(texture_type)  # Définir le type de texture dans le commentaire du nœud
                            texture_count += 1

                            # Connecter les nœuds d'image au nœud mtlxstandard_surface
                            if texture_type == "BASE_COLOR":
                                mtlx_standard_surface_node.setInput(1, image_node)  # Index pour 'base_color'
                            elif texture_type == "SPECULAR_ROUGHNESS":
                                mtlx_standard_surface_node.setInput(6, image_node)  # Index pour 'specular_roughness'
                                image_node.parm("signature").set("default")
                                image_node.parm("filecolorspace").set("Raw")
                            elif texture_type == "DISPLACEMENT":
                                mtlxdisplacement_node = selected_node.node('mtlxdisplacement')
                                if not mtlxdisplacement_node:
                                    mtlxdisplacement_node = selected_node.createNode("mtlxdisplacement")
                                    mtlxdisplacement_node.setName('mtlxdisplacement', unique_name=True)
                                mtlxdisplacement_node.setInput(0, image_node)
                                image_node.parm("signature").set("default")
                                image_node.parm("filecolorspace").set("Raw")
                            elif texture_type == "OPACITY":
                                mtlx_standard_surface_node.setInput(368, image_node)
                            elif texture_type == "METALNESS":
                                mtlx_standard_surface_node.setInput(36, image_node)  # Index pour 'metalness'
                                image_node.parm("signature").set("default")
                                image_node.parm("filecolorspace").set("Raw")
                            elif texture_type == "AMBIENT_OCCLUSION":
                                # Si vous souhaitez gérer l'AO, ajoutez le code ici
                                pass
                            elif texture_type == "EMISSIVE":
                                # Si vous souhaitez gérer l'émissif, ajoutez le code ici
                                pass
                        else:
                            hou.ui.displayMessage(f"Failed to create mtlximage node for {image_file}")
                else:
                    hou.ui.displayMessage(f"Texture type not recognized for {image_file}")

            # Layout automatique des nœuds enfants du subnet
            selected_node.layoutChildren()

            if texture_count > 0:
                hou.ui.displayMessage(f"{texture_count} texture nodes created and connected.")
            else:
                hou.ui.displayMessage("No texture nodes created.")
