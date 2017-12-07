'''
Created on Oct 29, 2015

@author: qurban.ali
'''
try:
    parentWin = None
    from uiContainer import uic
    import qtify_maya_window as qtfy
    parentWin = qtfy.getMayaWindow()
except:
    from PyQt4 import uic

from PyQt4.QtGui import QMessageBox, QFileDialog
import os.path as osp
import iutil
import utilities as utils
import cui
import appUsageApp
import re
import os

reload(utils)
rootPath = iutil.dirname(__file__, 2)
uiPath = osp.join(rootPath, 'ui')

USERS = ['qurban.ali', 'sarmad.mushtaq', 'mohammad.bilal', 'talha.ahmed',
         'taimour.khalid', 'assad.siddiqui', 'salman.rauf']


Form, Base = uic.loadUiType(osp.join(uiPath, 'main.ui'))


class UI(Form, Base):
    def __init__(self, parent=parentWin):
        super(UI, self).__init__(parent)
        self.setupUi(self)

        self.lastPath = ''
        self.title = 'Episode Planner'

        self.setWindowTitle(self.title)
        utils.setServer()
        self.populateProjectBox()

        self.browseButton.clicked.connect(self.setEpPath)
        self.populateButton.clicked.connect(self.populate)
        self.projectBox.currentIndexChanged[str].connect(self.setProject)

        appUsageApp.updateDatabase('epPlanner')

    def showMessage(self, **kwargs):
        return cui.showMessage(self, title=self.title, **kwargs)

    def setEpPath(self):
        filename = QFileDialog.getExistingDirectory(
            self, self.title, self.lastPath, QFileDialog.DontUseNativeDialog)
        if filename:
            self.epPathBox.setText(filename)
            self.lastPath = filename

    def epPath(self):
        path = self.epPathBox.text()
        if not osp.exists(path):
            self.showMessage(
                    msg='The system could not find the path specified',
                    icon=QMessageBox.Information)
            path = ''
        return path

    def setProject(self, project):
        self.epBox.clear()
        self.epBox.addItem('--Select Episode--')
        if project != '--Select Project--':
            errors = utils.setProject(project)
            self.populateEpisodes()
            if errors:
                self.showMessage(
                        msg='Error \'don\'t while configuring the TACTIC',
                        details=iutil.dictionaryToDetails(errors),
                        icon=QMessageBox.Critical)

    def populateProjectBox(self):
        self.projectBox.clear()
        self.projectBox.addItem('--Select Project--')
        projects, errors = utils.getProjects()
        if projects:
            self.projectBox.addItems(projects)
        if errors:
            self.showMessage(
                    msg=('Error occurred while fetching the list of Projects '
                         ' from TACTIC'),
                    details=iutil.dictionaryToDetails(errors),
                    icon=QMessageBox.Critical)

    def populateEpisodes(self):
        eps, errors = utils.getEpisodes()
        if eps:
            self.epBox.addItems(eps)
        if errors:
            self.showMessage(
                    msg=('Error occurred while fetching the list of Episodes '
                         ' from TACTIC'),
                    details=iutil.dictionaryToDetails(errors),
                    icon=QMessageBox.Critical)

    def getEpisode(self):
        ep = self.epBox.currentText()
        if ep == '--Select Episode--':
            self.showMessage(msg='Select an Episode and then try to populate',
                             icon=QMessageBox.Warning)
            ep = ''
        return ep

    def frameRange(self, shotPath):
        rnge = (0, 0)
        animaticPath = osp.join(shotPath, 'animatic')
        if osp.exists(animaticPath):
            files = os.listdir(animaticPath)
            fr = []
            if files:
                for ph in files:
                    try:
                        fr.append(int(ph.split('.')[1]))
                    except:
                        pass
                rnge = (min(fr), max(fr))
        return rnge

    def populate(self):
        if not os.environ['USERNAME'] in USERS:
            self.showMessage(
                msg="You don\'t have permissions to perform this action",
                icon=QMessageBox.Information)
            return
        path = self.epPath()
        if not path:
            return
        ep = self.getEpisode()
        if not ep:
            return
        seqsDir = osp.join(path, 'SEQUENCES')
        if not osp.exists(seqsDir):
            self.showMessage(
                    msg='The system could not find the SEQUENCES directory',
                    icon=QMessageBox.Critical)
            return
        seqs = [seq for seq in os.listdir(
            seqsDir) if re.match('^SQ\d{3}$', seq)]
        if not seqs:
            self.showMessage(
                    msg='The system could not find the Sequences directory',
                    icon=QMessageBox.Critical)
            return
        errors = utils.addSequences(ep, seqs)
        shots = {}
        for seq in seqs:
            shotsDir = osp.join(seqsDir, seq, 'SHOTS')
            if not osp.exists(shotsDir):
                errors['SHOTS directory not found in %s' % seq] = ''
                continue
            for shot in os.listdir(shotsDir):
                if re.match('^SQ\d{3}_SH\d{3}$', shot):
                    shots[shot] = self.frameRange(osp.join(shotsDir, shot))
        if shots:
            errors.update(utils.addShots(ep, shots))
        if errors:
            self.showMessage(
                    msg='Errors occurred while populating Sequences and shots',
                    icon=QMessageBox.Critical,
                    details=iutil.dictionaryToDetails(errors))
        else:
            self.showMessage(msg='Episode populated successfully',
                             icon=QMessageBox.Information)
