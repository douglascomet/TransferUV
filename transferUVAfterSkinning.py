#!/usr/bin/env python
#title           :transferUVAfterSkinning.py
#description     :Script is used to transfer the UVs of a mesh to a 
#					skinned version of the mesh that has identical topology
#					and prevents the generation of the undeletable "transferAttributes" node.
#author          :Doug Halley
#date            :20170606
#version         :3.0
#usage           :Function to execute transferUVAfterSkinning.transUI()
#notes           :
#python_version  :2.7.6  
#==============================================================================

"""
Based on steps to transfer UVs found at
http://www.brookewagstaff.com/modeling-texturing/transferring-uvs/
"""

import sys
import Qt
#QtWidgets creates all widgets
from Qt import QtWidgets as qw
from Qt import QtCore as qc

#QtGui customizes Gui
from Qt import QtGui as qg

import maya.cmds as cmds

class transUI(Qt.QtWidgets.QDialog):
	def __init__(self, *args):
		qw.QDialog.__init__(self)

		#frame settings
		self.setWindowTitle("Transfer UVs after Skinning")
		#self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
		self.setModal(False)
		self.setFixedHeight(150)
		self.setMinimumWidth(300)

		#parent layout
		self.setLayout(qw.QHBoxLayout())

		#defaults for margins and layouts are 10 but smaller values make the layout look more professional
		#sets margins outside the layout: left, up, right, bottom
		self.layout().setContentsMargins(5,5,5,5)

		#sets spacing between each element in the layout
		self.layout().setSpacing(5)

		ui_layout = qw.QVBoxLayout()
		
		self.layout().addLayout(ui_layout)
		
		skinnedMesh_layout = qw.QHBoxLayout()

		#lbl = label
		skinnedMesh_lbl = qw.QLabel("Name of Skinned Mesh:")
		skinnedMesh_lbl.setAlignment(qc.Qt.AlignCenter)

		#le = line edit
		self.skinnedMesh_le = qw.QLineEdit(None)
		self.skinnedMesh_le.setReadOnly(True)
		
		self.loadSkinnedMesh_btn = qw.QPushButton("<<")

		skinnedMesh_layout.addWidget(skinnedMesh_lbl)
		skinnedMesh_layout.addWidget(self.skinnedMesh_le)
		skinnedMesh_layout.addWidget(self.loadSkinnedMesh_btn)

		uvMesh_layout = qw.QHBoxLayout()

		#lbl = label
		uvMesh_lbl = qw.QLabel("Name of UVed Mesh:")
		uvMesh_lbl.setAlignment(qc.Qt.AlignCenter)

		#le = line edit
		self.uvMesh_le = qw.QLineEdit(None)
		#self.uvMesh_le.setPlaceholderText(None)
		self.uvMesh_le.setReadOnly(True)

		self.loadUVMesh_btn = qw.QPushButton("<<")

		self.loadUVMesh_btn = qw.QPushButton("<<")
		uvMesh_layout.addWidget(uvMesh_lbl)
		uvMesh_layout.addWidget(self.uvMesh_le)
		uvMesh_layout.addWidget(self.loadUVMesh_btn)

		#add labels and input fields
		ui_layout.addLayout(skinnedMesh_layout)
		ui_layout.addLayout(uvMesh_layout)
		
		self.transfer_bttn = qw.QPushButton("Transfer UVs")
		self.transfer_bttn.setEnabled(False)
		
		ui_layout.addWidget(self.transfer_bttn)
		self.layout().addLayout(ui_layout)
		
		self.loadSkinnedMesh_btn.clicked.connect(lambda: self.selectSkinnedMesh())
		self.loadUVMesh_btn.clicked.connect(lambda: self.selectUVMesh())
		self.transfer_bttn.clicked.connect(lambda: self.transferUV(str(self.skinnedMesh_le.text()), str(self.uvMesh_le.text())))	 	

	def setText_Rig(self):
		self.skinnedMesh_le.setText(str(self.skinnedMesh_le.text()))

	def setText_UV(self):
		self.uvMesh_le.setText(str(self.uvMesh_le.text()))

	def enableTransferUV(self):
		if self.uvMesh_le.text() and self.skinnedMesh_le.text():
			self.transfer_bttn.setEnabled(True)

	def selectSkinnedMesh(self):
		
		tempSelection = cmds.ls(selection = True)

		foundSkinCluster = False

		if not len(tempSelection):
			self.skinnedMesh_le.setText(None)
			self.popupMessage("An object was not selected")
		elif len(tempSelection) != 1:
			self.popupMessage("Please select only one object")
		elif len(tempSelection) == 1:
			
			for historyNode in cmds.listHistory(tempSelection[0]):
				if "skinCluster" in historyNode:
					self.skinnedMesh_le.setText(str(tempSelection[0]))
					foundSkinCluster = True
					self.enableTransferUV()
					break

			if not foundSkinCluster:
				self.popupMessage("Selected Object is not a Skinned Mesh")

	def selectUVMesh(self):
		
		tempSelection = cmds.ls(selection = True)

		if not len(tempSelection):
			self.uvMesh_le.setText(None)
			self.popupMessage("An object was not selected")

		elif len(tempSelection) != 1:
			self.popupMessage("Please select only one object")

		elif len(tempSelection) == 1:
			self.uvMesh_le.setText(str(tempSelection[0]))
			self.enableTransferUV()

	def popupMessage(self, message):

		popupWindow = qw.QMessageBox()

		popupWindow.setInformativeText(message)
		popupWindow.setStandardButtons(qw.QMessageBox.Ok)

		popupWindow.exec_()

	def transferUV(self, skinMesh, uvMesh):
		origMesh = ""
		restOfName = ""
		interAttr = ""
		interObjAttr = ""
		
		if skinMesh == "" or skinMesh == None:
			self.popupMessage( 'A valid string name was not entered for the rigged mesh.\nPlease re-run script.')
			return

		elif uvMesh == "" or uvMesh == None:
			self.popupMessage('A valid string name was not entered for the UVed mesh.\nPlease re-run script.')
			return

		else:
			skinMeshChildren = cmds.listRelatives(skinMesh)

			for x in skinMeshChildren:
				if "ShapeOrig" in x:
					origMesh = x

			#origMesh = skinMesh + "ShapeOrig"

			#get list of origMesh's attributes
			origMeshAttr = cmds.listAttr(origMesh)

			#traverse attributes 
			for i in origMeshAttr:
				if "intermediate" in i.lower():

					#saves attribute name
					interObjAttr = str(i)
		
			#unchecks origMesh's interObjAttr to off
			cmds.setAttr(("%s.%s" % (origMesh,interObjAttr)), 0)

			#select object with correct UVs followed by origMesh to transfer attributes and UVs
			cmds.transferAttributes(uvMesh, origMesh, transferPositions  = 0,  transferNormals = 0, transferUVs = 2, transferColors = 2, sampleSpace = 5, sourceUvSpace = "map1", searchMethod = 3, flipUVs = 0, colorBorders = 1)

			#deletes construction history of oskinMesh
			cmds.delete(origMesh, ch = True)

			#checks oskinMesh's interObjAttr to on
			cmds.setAttr(("%s.%s" % (origMesh,interObjAttr)), 1)

			self.popupMessage("Successfully transfered UVs")

#ex = transUI()
#ex.show()
