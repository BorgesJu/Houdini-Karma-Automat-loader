import hou
import os

# Dictionnaire des types de textures et de leurs noms associés
texture_types = {
    "BASE_COLOR": ["diff", "dif", "basecolor", "base color", "base_color", "albedo", "alb", "diffuse", "color"],
    "SPECULAR_ROUGHNESS": ["roughness", "gloss", "glossiness", "rough"],
    "NORMAL": ["normal", "bump", "norm"],
    "DISPLACEMENT": ["displacement", "height", "disp", "dis"],
    "OPACITY": ["opacity", "alpha", "transparent", "transparency"],
    "METALNESS": ["metal", "metalness", "mtl", "metallic"]
}

# Fonction pour déterminer le type de texture en fonction du nom du fichier
def get_texture_type(file_name):
    for texture_type, keywords in texture_types.items():
        for keyword in keywords:
            if keyword in file_name.lower():
                return texture_type
    return None

# Fonction pour créer un nœud mtlximage à l'intérieur du nœud sélectionné
def create_mtlximage_in_selected_node(selected_node, image_path, texture_type):
    try:
        mtlximage_node = selected_node.createNode('mtlximage')
        if mtlximage_node is not None:
            mtlximage_node.setName(os.path.basename(image_path), unique_name=True)
            filename_parm = mtlximage_node.parm('file')
            if filename_parm is not None:
                filename_parm.set(image_path)
                return mtlximage_node
            else:
                return None
        else:
            return None
    except Exception as e:
        hou.ui.displayMessage(f"Error creating mtlximage node: {e}")
        return None

# Obtenir le premier nœud sélectionné
selected_nodes = hou.selectedNodes()
if not selected_nodes:
    hou.ui.displayMessage("Please select a node.")
else:
    selected_node = selected_nodes[0]  # Prend le premier nœud sélectionné
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
            # Variable pour compter le nombre d'images créées
            image_count = 0

            # Créer un nœud mtlximage pour chaque fichier image
            for image_file in image_files:
                image_path = os.path.join(folder_path, image_file)
                texture_type = get_texture_type(image_file)
                if texture_type is not None:
                    image_node = create_mtlximage_in_selected_node(selected_node, image_path, texture_type)
                    if image_node:
                        image_node.setComment(texture_type)  # Définir le type de texture dans le commentaire du nœud
                        image_count += 1

                        # Connecter les nœuds d'image au nœud mtlxstandard_surface
                        if texture_type == "BASE_COLOR":
                            selected_node.node('mtlxstandard_surface').setInput(1, image_node)  # Index pour 'base_color'
                        elif texture_type == "SPECULAR_ROUGHNESS":
                            selected_node.node('mtlxstandard_surface').setInput(6, image_node)  # Index pour 'specular_roughness'
                            image_node.parm("signature").set("default")
                            image_node.parm("filecolorspace").set("Raw")
                        elif texture_type == "NORMAL":
                            normal_map_node = selected_node.createNode("mtlxnormalmap")
                            normal_map_node.setInput(0, image_node)
                            selected_node.node('mtlxstandard_surface').setInput(40, normal_map_node)
                            image_node.parm("signature").set("vector2")
                        elif texture_type == "DISPLACEMENT":
                            mtlxdisplacement_node = selected_node.node('mtlxdisplacement')
                            if not mtlxdisplacement_node:
                                mtlxdisplacement_node = selected_node.createNode("mtlxdisplacement")
                            mtlxdisplacement_node.setInput(0, image_node)
                            image_node.parm("signature").set("default")
                            image_node.parm("filecolorspace").set("Raw")
                        elif texture_type == "OPACITY":
                            selected_node.node('mtlxstandard_surface').setInput(368, image_node)
                        elif texture_type == "METALNESS":
                            selected_node.node('mtlxstandard_surface').setInput(36, image_node)  # Index pour 'metalness'
                            image_node.parm("signature").set("default")
                            image_node.parm("filecolorspace").set("Raw")

            # Layout automatique des nœuds enfants du subnet
            selected_node.layoutChildren()

            if image_count > 0:
                hou.ui.displayMessage(f"{image_count} mtlximage nodes created and connected.")
            else:
                hou.ui.displayMessage("No mtlximage nodes created.")
