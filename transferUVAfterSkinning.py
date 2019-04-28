# =============================================================================
# !/usr/bin/env python
# title           :transfer_uvsAfterSkinning.py
# description     :Script is used to transfer the UVs of a mesh to a
#                   skinned version of the mesh that has identical topology
#                   and prevents the generation of the undeletable
#                   'transferAttributes' node.
# author          :Doug Halley
# date            :2018-01-07
# version         :5.0
# usage           :Function to execute transferUVAfterSkinning.Transfer_UV()
# notes           :Based on steps to transfer UVs found at
#           http://www.brookewagstaff.com/modeling-texturing/transferring-uvs/
# python_version  :2.7.14
# =============================================================================

# QtWidgets creates all widgets
from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui


class Transfer_UV(QtWidgets.QMainWindow):
    """
    Tool meant to transfer a UV-ed mesh to a skinned mesh without leaving additional nodes in
    construction history of the skinned mesh.
    """

    def __init__(self, parent=None):
        """
        Initilizes the PyQt Interface.

        Keyword Arguments:
            parent {None} -- By having no parent, ui can be standalone
                                (default: {None})
        """

        super(Transfer_UV, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        """
        Logic to create QtWidget's UI.
        """

        # frame settings
        self.setWindowTitle('Transfer UVs after Skinning')
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # self.setModal(False)
        self.setFixedHeight(150)
        self.setMinimumWidth(300)

        # defaults for margins and layouts are 10 but smaller values make the
        # layout look more professional
        # sets margins outside the layout: left, up, right, bottom
        self.layout().setContentsMargins(5, 5, 5, 5)

        # sets spacing between each element in the layout
        self.layout().setSpacing(5)

        # =====================================================================
        # PYQT Widget Defintions
        # =====================================================================

        # skinned_mesh_layout, child of central_widget ------------------------
        skinned_mesh_layout = QtWidgets.QHBoxLayout()

        skinned_mesh_lbl = QtWidgets.QLabel('Name of Skinned Mesh:')
        skinned_mesh_lbl.setAlignment(QtCore.Qt.AlignCenter)

        self.skinned_mesh_le = QtWidgets.QLineEdit(None)
        self.skinned_mesh_le.setReadOnly(True)

        skinned_mesh_btn = QtWidgets.QPushButton('<<')

        # uv_mesh_layout, child of central_widget -----------------------------
        uv_mesh_layout = QtWidgets.QHBoxLayout()

        uv_mesh_lbl = QtWidgets.QLabel('Name of UVed Mesh:')
        uv_mesh_lbl.setAlignment(QtCore.Qt.AlignCenter)

        self.uv_mesh_le = QtWidgets.QLineEdit(None)
        # self.uv_mesh_le.setPlaceholderText(None)
        self.uv_mesh_le.setReadOnly(True)

        load_uv_mesh_btn = QtWidgets.QPushButton('<<')

        self.transfer_btn = QtWidgets.QPushButton('Transfer UVs')
        self.transfer_btn.setEnabled(False)

        # =====================================================================
        # PYQT Widget/Layout Assignments
        # =====================================================================

        skinned_mesh_layout.addWidget(skinned_mesh_lbl)
        skinned_mesh_layout.addWidget(self.skinned_mesh_le)
        skinned_mesh_layout.addWidget(skinned_mesh_btn)

        uv_mesh_layout.addWidget(uv_mesh_lbl)
        uv_mesh_layout.addWidget(self.uv_mesh_le)
        uv_mesh_layout.addWidget(load_uv_mesh_btn)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QVBoxLayout())
        central_widget.layout().addLayout(skinned_mesh_layout)
        central_widget.layout().addLayout(uv_mesh_layout)

        central_widget.layout().addWidget(self.transfer_btn)
        self.setCentralWidget(central_widget)

        # =====================================================================
        # PyQt Execution Connections
        # =====================================================================

        skinned_mesh_btn.clicked.connect(lambda: self.select_skinned_mesh())
        load_uv_mesh_btn.clicked.connect(lambda: self.select_uv_mesh())
        self.transfer_btn.clicked.connect(lambda: self.transfer_uvs(
            str(self.skinned_mesh_le.text()), str(self.uv_mesh_le.text())))

    def enable_transfer_uv(self):
        """
        Checks if both self.uv_mesh_le and self.skinned_mesh_le have an input before enabling self.transfer_btn
        """

        if self.uv_mesh_le.text() and self.skinned_mesh_le.text():
            self.transfer_btn.setEnabled(True)

    def select_skinned_mesh(self):
        """
        Checks if selected object is a skinned mesh before storing and
            using the object
        """

        import maya.cmds as cmds # pylint: disable=import-error

        selection = cmds.ls(selection=True)

        if self._verify_selection(selection):
            found_skin_cluster = False

            for history_node in cmds.listHistory(selection[0]):
                if 'skinCluster' in history_node:
                    self.skinned_mesh_le.setText(str(selection[0]))
                    found_skin_cluster = True
                    self.enable_transfer_uv()
                    break

            if not found_skin_cluster:
                self.popup_message('Selected Object is not a Skinned Mesh')

    def select_uv_mesh(self):
        """
        Checks if selected object is a mesh and that only one object was selected
        """

        import maya.cmds as cmds # pylint: disable=import-error

        selection = cmds.ls(selection=True)

        if self._verify_selection(selection):
            self.uv_mesh_le.setText(str(selection[0]))
            self.enable_transfer_uv()

    def _verify_selection(self, selection):
        if not selection:
            self.popup_message('An object was not selected')
            return False
        elif len(selection) != 1:
            self.popup_message('Select only one object')
            return False
        elif len(selection) == 1:
            return True

    def popup_message(self, message):
        """
        Generic popup window with an OK button and displays message
        Generates QMessageBox with OK button. Used as a simple notification.

        Arguments:
            message {string} -- string to be generated in popup
        """

        popup_window = QtWidgets.QMessageBox()

        popup_window.setInformativeText(message)
        popup_window.setStandardButtons(QtWidgets.QMessageBox.Ok)

        popup_window.exec_()

    def transfer_uvs(self, skin_mesh, uv_mesh):
        """
        UVs are transferred from the uv_mesh to

        Arguments:
            skin_mesh {string} -- String used to identify object in Maya scene
                                    for the skinned mesh
            uv_mesh {string} -- String used to identify object in Maya scene
                                    for the mesh object
        """

        import maya.cmds as cmds # pylint: disable=import-error

        orig_mesh = ''
        intermediate_obj_attr = ''

        if skin_mesh == '' or skin_mesh is None:
            self.popup_message('A valid string name was not entered for ' +
                               'the rigged mesh.\nPlease re-run script.')
            return

        elif uv_mesh == '' or uv_mesh is None:
            self.popup_message('A valid string name was not entered for ' +
                               'the UVed mesh.\nPlease re-run script.')
            return

        else:
            # search through relatives of the skin_mesh to look for the 'ShapeOrig' object
            for x in cmds.listRelatives(skin_mesh):
                if 'ShapeOrig' in x:
                    orig_mesh = x

            # get list of orig_mesh's attributes
            for i in cmds.listAttr(orig_mesh):
                if 'intermediate' in i.lower():
                    intermediate_obj_attr = str(i) # saves attribute name

            # unchecks orig_mesh's intermediate_obj_attr to off
            cmds.setAttr('{0}.{1}'.format(orig_mesh, intermediate_obj_attr), 0)

            # select object with correct UVs followed by orig_mesh
            # to transfer attributes and UVs
            cmds.transferAttributes(
                uv_mesh, orig_mesh, transferPositions=0, transferNormals=0, transferUVs=2,
                transferColors=2, sampleSpace=5, sourceUvSpace='map1', searchMethod=3,
                flipUVs=0, colorBorders=1)

            # deletes construction history of oskin_mesh
            cmds.delete(orig_mesh, ch=True)

            # checks oskin_mesh's intermediate_obj_attr to on
            cmds.setAttr('{0}.{1}'.format(orig_mesh, intermediate_obj_attr), 1)

            self.popup_message('Successfully transfered UVs')


MAIN_WINDOW = [o for o in QtWidgets.qApp.topLevelWidgets() if o.objectName() == 'MayaWindow'][0]

UI = Transfer_UV(MAIN_WINDOW)
UI.show()
