# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WebServicePluginDialog
                                 A QGIS plugin
 Wtyczka umożliwia prezentację danych z serwisów WMS, WMTS, WFS i WCS w postaci warstw w QGIS. Wtyczka wykorzystuje dane z Ewidencji Zbiorów i Usług oraz strony geoportal.gov.pl
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-08-28
        git sha              : $Format:%H$
        copyright            : (C) 2024 by EnviroSolutions Sp. z o.o.
        email                : office@envirosolutions.pl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import re
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from devision_api import get_gminy, get_powiaty, get_wojewodztwa

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'web_service_plugin_dialog_base.ui'))



class WebServicePluginDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(WebServicePluginDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
 
        self.comboBox_gminy = self.comboBox_gminy
        self.comboBox_powiaty = self.comboBox_powiaty
        self.comboBox_wojewodztwa = self.comboBox_wojewodztwa



        self.load_wojewodztwa()
        self.comboBox_gminy.currentIndexChanged.connect(self.on_combobox_gminy_changed)
        self.comboBox_powiaty.currentIndexChanged.connect(self.on_combobox_powiaty_changed)
        self.comboBox_wojewodztwa.currentIndexChanged.connect(self.on_combobox_wojewodztwa_changed)


    def load_wojewodztwa(self): 
        self.devision_dict = get_wojewodztwa()
        self.comboBox_wojewodztwa.addItems(['województwo'] + sorted(self.devision_dict.keys()))
        self.comboBox_powiaty.addItems(['powiat'])
        self.comboBox_gminy.addItems(['gmina'])
        self.comboBox_wojewodztwa.setCurrentIndex(0)
        self.comboBox_powiaty.setCurrentIndex(0)
        self.comboBox_gminy.setCurrentIndex(0)

    def on_combobox_gminy_changed(self):
        selected_option = self.comboBox_gminy.currentText()
        #todo

    def on_combobox_powiaty_changed(self):
        selected_option = self.comboBox_powiaty.currentText()
        
        if selected_option == 'powiat' or not selected_option:
            self.comboBox_gminy.clear()
            self.comboBox_gminy.addItems(['gmina'])
        else:
            wojewodztwo = self.comboBox_wojewodztwa.currentText()
            if isinstance(self.devision_dict[wojewodztwo][selected_option], str):
                powiat_id = self.devision_dict[wojewodztwo][selected_option]
                self.devision_dict[wojewodztwo][selected_option] = get_gminy(powiat_id)
                print(get_gminy(powiat_id))
            gminy = self.devision_dict[wojewodztwo][selected_option]
            self.comboBox_gminy.clear()
            self.comboBox_gminy.addItems(['gmina'] + gminy)


    def on_combobox_wojewodztwa_changed(self):
        selected_option = self.comboBox_wojewodztwa.currentText()
        if selected_option == 'województwo':
            self.comboBox_powiaty.clear()
            self.comboBox_powiaty.addItems(['powiat'])
        else:
            if isinstance(self.devision_dict[selected_option], str):
                wojewodztwo_id = self.devision_dict[selected_option]
                self.devision_dict[selected_option] = get_powiaty(wojewodztwo_id)
            powiaty = sorted(self.devision_dict[selected_option].keys())
            self.comboBox_powiaty.clear()
            self.comboBox_powiaty.addItems(['powiat'] + powiaty)
        self.on_combobox_powiaty_changed()


