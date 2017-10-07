# TransferUV

This Maya tool is used to transfer the UVs of a mesh to a skinned version of the mesh that has identical topology and prevents the generation of the undeletable "transferAttributes" node.

This tool is based on the steps shown here:
http://www.brookewagstaff.com/modeling-texturing/transferring-uvs/

<a href="http://www.youtube.com/watch?feature=player_embedded&v=gLuMgsd7YaI
" target="_blank"><img src="http://img.youtube.com/vi/gLuMgsd7YaI/0.jpg" 
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>

The demo above shows how it works. The function to call is transferUVAfterSkinning.transUI()

It uses the Qt.py framework so it can work with PySide and PySide2:
https://github.com/mottosso/Qt.py
