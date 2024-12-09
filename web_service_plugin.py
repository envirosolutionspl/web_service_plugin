# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WebServicePlugin
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QToolBar
from qgis.core import QgsSettings, Qgis

from qgis.PyQt.QtWidgets import QDialog

from .qgis_feed import QgisFeedDialog
from .api.region_fetch import RegionFetch
from .api.add_service import AddOGCService
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .web_service_plugin_dialog import WebServicePluginDialog
import os.path

"""Wersja wtyczki"""
plugin_version = '0.1.0'
plugin_name = 'Web Service Plugin'

class WebServicePlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        self.settings = QgsSettings()

        if Qgis.QGIS_VERSION_INT >= 31000:
            from .qgis_feed import QgisFeed
            self.selected_industry = self.settings.value("selected_industry", None)
            show_dialog = self.settings.value("showDialog", True, type=bool)
            if self.selected_industry is None and show_dialog:
                self.showBranchSelectionDialog()
            select_indust_session = self.settings.value('selected_industry')
            self.feed = QgisFeed(selected_industry=select_indust_session, plugin_name=plugin_name)
            self.feed.initFeed()

        # initialize locale
        locale = self.settings.value('locale/userLocale')[:2]
        locale_path = os.path.join(
            self.plugin_dir, 'i18n', f'WebServicePlugin_{locale}.qm'
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&EnviroSolutions')

        # toolbar
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, 'EnviroSolutions')
        if not self.toolbar:
            self.toolbar = self.iface.addToolBar(u'EnviroSolutions')
            self.toolbar.setObjectName(u'EnviroSolutions')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.regionFetch = RegionFetch(teryt='')


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('WebServicePlugin', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            # self.iface.addToolBarIcon(action)
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.dlg = WebServicePluginDialog(self.regionFetch)
        self.setup_dialog()

        icon_path = ':/plugins/web_service_plugin/images/icon.svg'
        self.add_action(
            icon_path,
            text=self.tr(plugin_name),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&EnviroSolutions'),
                action)
            # self.iface.removeToolBarIcon(action)
            self.toolbar.removeAction(action)

    def showBranchSelectionDialog(self):
        self.qgisfeed_dialog = QgisFeedDialog()

        if self.qgisfeed_dialog.exec_() == QDialog.Accepted:
            self.selected_branch = self.qgisfeed_dialog.comboBox.currentText()

            # Zapis w QGIS3.ini
            self.settings.setValue("selected_industry", self.selected_branch)
            self.settings.setValue("showDialog", False)

    def add_service(self) -> None:
        successfully_add = {}
        selected_urls = self.dlg.get_selected_services_urls()
        for name, url in selected_urls.items():
            services = ['WFS', 'WCS'] if self.dlg.wfs_rdbtn.isChecked() else ['WMTS', 'WMS']
            service_type = AddOGCService.detect_service_type(url, services)
            if service_type:
                add_layer = AddOGCService.add_service(url, service_type)
                successfully_add[name] = add_layer
            else:
                successfully_add[name] = False
        msgbox = QMessageBox(
            QMessageBox.Information,
            'Informacja',
            '\n'.join(
                f'Dodano usługę {key}' if value else f'Nie dodano usługi {key}'
                for key, value in successfully_add.items()
            )
        )
        msgbox.exec_()

    def setup_dialog(self) -> None:
        self.dlg.add_btn.clicked.connect(self.add_service)

    def run(self):
        if self.first_start == True:
            self.first_start = False

             # informacje o wersji
            self.dlg.setWindowTitle('%s %s' % (plugin_name, plugin_version))
            self.dlg.lbl_pluginVersion.setText('%s %s' % (plugin_name, plugin_version))

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
