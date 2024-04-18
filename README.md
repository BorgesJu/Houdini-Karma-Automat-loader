# Karma Auto(matic)

![Karma Material Importer](https://github.com/BorgesJu/Houdini-Karma-Automat-loader/assets/39913185/73f5fee5-40fe-4794-844a-d68f048623f9)

Mat(erial) Importer

## Overview
Karma Automatic Material Importer is a script designed for SideFX Houdini that automates the process of importing and setting up materials using the Karma renderer and MaterialX standards. This tool is ideal for streamlining the texturing workflow, particularly when working with multiple texture files.

## Features
- **Automatic Texture Detection:** Automatically detects textures in a specified folder and categorizes them based on naming conventions.
- **Material Node Creation:** Dynamically creates `mtlximage` nodes for each detected texture.
- **Automatic Node Connections:** Connects textures to the appropriate slots in the `mtlxstandard_surface` shader based on the texture type.
- **Node Renaming:** Renames the main material node based on the folder name from which textures are imported.

## Installation
To use the Karma Automatic Material Importer, copy the Python script into your Houdini Python script directory.

## Usage
1. **Add to Houdini Toolshelf:**
   Create a new tool in Houdini's toolshelf and insert the script. This allows for easy access and execution within the Houdini environment.

2. **Select the Karma Material Builder Node:**
   Ensure that the `karmamaterialbuilder` node is selected in your Houdini scene before running the script from the toolshelf.

3. **Run the Script:**
   Execute the script from the toolshelf. You will be prompted to select a folder containing your texture files. Supported file formats include `.png`, `.jpg`, `.jpeg`, `.exr`, `.tif`, and `.tiff`.

4. **Automatic Processing:**
   Once a folder is selected, the script automatically scans for texture files, creates material nodes, and sets up connections based on detected texture types.

## Supported Texture Types
The script supports the following texture types and connects them to the corresponding MaterialX inputs:
- **Base Color**: Maps to `base_color`
- **Specular Roughness**: Maps to `specular_roughness`
- **Normal**: Maps to a `mtlxnormalmap` node, then to `normal`
- **Displacement**: Connects to `mtlxdisplacement`
- **Opacity**: Maps to `opacity`
- **Metalness**: Maps to `metalness`

## Customization
You can customize the script by modifying the `texture_types` dictionary to include additional texture types or to change the mapping of existing types based on your specific workflow needs.

## License
This project is open source and available under the MIT License. Feel free to fork, modify, and use it in your projects.

## Contribution
Contributions are welcome! If you have improvements or bug fixes, please feel free to fork the repository and submit a pull request.

[Aletheia Design](https://aletheiadesign.fr)  
[Aletheiadesign|Instagram](https://www.instagram.com/al3ph.d.sign/)
