# -*- coding: utf-8 -*-
"""
# Ibiraté - APP Analises | https://www.ibirate.com.br/
(C) 2026 by Poliana Cursino Betella | Pedro Cursino Betella Gomes
betella.poliana@gmail.com | pedro.cursino.gomes@gmail.com
"""

from qgis.PyQt import QtWidgets, QtCore, QtGui
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel, QgsWkbTypes, QgsMapLayer, Qgis
from .processor import ForestRules, SpatialEngine 

class AppComplianceDock(QtWidgets.QDockWidget):
    def __init__(self, iface):
        super(AppComplianceDock, self).__init__("Ibiraté - APP Analises")
        self.iface = iface
        self.main_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.main_widget)
        self._build_ui()
        self.setWidget(self.main_widget)

    def _build_ui(self):
        # --- ENTRADAS ---
        group_in = QtWidgets.QGroupBox("1. Entradas Base")
        lay_in = QtWidgets.QVBoxLayout(group_in)
        self.combo_nascente = QgsMapLayerComboBox()
        self.combo_nascente.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.combo_rio = QgsMapLayerComboBox()
        self.combo_rio.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.combo_imovel = QgsMapLayerComboBox()
        self.combo_imovel.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        lay_in.addWidget(QtWidgets.QLabel("Nascentes (Ponto):"))
        lay_in.addWidget(self.combo_nascente)
        lay_in.addWidget(QtWidgets.QLabel("Cursos d'Água (Linha):"))
        lay_in.addWidget(self.combo_rio)
        lay_in.addWidget(QtWidgets.QLabel("Limite do Imóvel (Polígono):"))
        lay_in.addWidget(self.combo_imovel)
        
        btn_auto = QtWidgets.QPushButton("Preencher com Selecionadas")
        btn_auto.clicked.connect(self._auto_fill_selected)
        lay_in.addWidget(btn_auto)
        self.layout.addWidget(group_in)

        # --- PARÂMETROS ---
        group_rules = QtWidgets.QGroupBox("2. Parâmetros Legais")
        lay_rules = QtWidgets.QVBoxLayout(group_rules)
        self.combo_largura = QtWidgets.QComboBox()
        self.combo_largura.addItems(["< 10m", "10-50m", "50-200m", "200-600m", "> 600m"])
        lay_rules.addWidget(QtWidgets.QLabel("Largura do Rio (Art. 4):"))
        lay_rules.addWidget(self.combo_largura)

        self.check_consolidado = QtWidgets.QCheckBox("Analisar Uso Consolidado")
        lay_rules.addWidget(self.check_consolidado)

        self.container_cons = QtWidgets.QWidget()
        lay_cons = QtWidgets.QVBoxLayout(self.container_cons)
        self.combo_mf = QtWidgets.QComboBox()
        self.combo_mf.addItems(["Até 1 MF", "1 a 2 MF", "2 a 4 MF", "4 a 10 MF", "> 10 MF"])
        lay_cons.addWidget(QtWidgets.QLabel("Tamanho do imóvel em Módulos Fiscais (MF):"))
        lay_cons.addWidget(self.combo_mf)

        # Largura exata: so e necessaria acima de 4 MF quando a regra e
        # "metade da largura, min. 30 m e max. 100 m" (Decreto 7.830/2012, art. 19, par. 4, II)
        self.container_largura = QtWidgets.QWidget()
        lay_larg = QtWidgets.QVBoxLayout(self.container_largura)
        lay_larg.setContentsMargins(0, 0, 0, 0)
        self.label_largura_exata = QtWidgets.QLabel("Largura do curso d'água (m) — recomposição = metade da largura (mín. 30 m, máx. 100 m):")
        self.label_largura_exata.setWordWrap(True)
        self.spin_largura = QtWidgets.QDoubleSpinBox()
        self.spin_largura.setRange(0, 100000)
        self.spin_largura.setDecimals(1)
        self.spin_largura.setSuffix(" m")
        lay_larg.addWidget(self.label_largura_exata)
        lay_larg.addWidget(self.spin_largura)
        lay_cons.addWidget(self.container_largura)
        self.label_faixa_cons = QtWidgets.QLabel("")
        self.label_faixa_cons.setStyleSheet("color: #2e7d32; font-weight: bold;")
        lay_cons.addWidget(self.label_faixa_cons)

        self.combo_mf.currentIndexChanged.connect(self._update_cons_preview)
        self.combo_largura.currentIndexChanged.connect(self._on_width_category_changed)
        self.spin_largura.valueChanged.connect(self._update_cons_preview)

        # Calculadora auxiliar
        calc_box = QtWidgets.QGroupBox("Auxílio: Calculadora de MF")
        lay_calc = QtWidgets.QGridLayout(calc_box)
        self.spin_mf_val = QtWidgets.QDoubleSpinBox(); self.spin_mf_val.setRange(0, 500); self.spin_mf_val.setSuffix(" ha")
        self.spin_area_imovel = QtWidgets.QDoubleSpinBox(); self.spin_area_imovel.setRange(0, 1000000); self.spin_area_imovel.setSuffix(" ha")
        self.label_res_mf = QtWidgets.QLabel("Resultado: - MF")
        btn_calc = QtWidgets.QPushButton("Calcular")
        btn_calc.clicked.connect(self._calculate_mf_math)
        lay_calc.addWidget(QtWidgets.QLabel("Valor MF:"), 0, 0); lay_calc.addWidget(self.spin_mf_val, 0, 1)
        lay_calc.addWidget(QtWidgets.QLabel("Área Imóvel:"), 1, 0); lay_calc.addWidget(self.spin_area_imovel, 1, 1)
        lay_calc.addWidget(btn_calc, 2, 0); lay_calc.addWidget(self.label_res_mf, 2, 1)
        lay_cons.addWidget(calc_box)

        btn_embrapa = QtWidgets.QPushButton("Consultar tamanho do MF (Embrapa)")
        btn_embrapa.setStyleSheet("font-size: 11px; color: blue; text-decoration: underline; border: none; background: none;")
        btn_embrapa.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://www.embrapa.br/codigo-florestal/area-de-reserva-legal-arl/modulo-fiscal")))
        lay_cons.addWidget(btn_embrapa)

        self.container_cons.setVisible(False)
        self.check_consolidado.toggled.connect(self.container_cons.setVisible)
        lay_rules.addWidget(self.container_cons)
        self.layout.addWidget(group_rules)

        self.btn_run = QtWidgets.QPushButton("GERAR ANÁLISES")
        self.btn_run.setStyleSheet("font-weight: bold; background-color: #2e7d32; color: white; min-height: 40px;")
        self.btn_run.clicked.connect(self._execute)
        self.layout.addWidget(self.btn_run)
        self.layout.addStretch()
        self._on_width_category_changed()

    def _needs_exact_width(self):
        mf = self.combo_mf.currentIndex()
        w = self.combo_largura.currentIndex()
        return mf in (3, 4) and w != 0

    def _on_width_category_changed(self, *args):
        lo, hi = ForestRules.width_range(self.combo_largura.currentIndex())
        if not (lo <= self.spin_largura.value() <= hi):
            self.spin_largura.setValue(lo)
        self._update_cons_preview()

    def _cons_river_distance(self):
        return ForestRules.get_consolidado_dist_river(
            self.combo_mf.currentIndex(),
            self.combo_largura.currentIndex(),
            self.spin_largura.value(),
        )

    def _update_cons_preview(self, *args):
        self.container_largura.setVisible(self._needs_exact_width())
        self.label_faixa_cons.setText(
            f"Faixa de recomposição no curso d'água: {self._cons_river_distance():.1f} m | nascente: 15 m"
        )

    def _auto_fill_selected(self):
        selected = self.iface.layerTreeView().selectedLayers()
        for layer in selected:
            if layer.type() == QgsMapLayer.VectorLayer:
                geom = layer.geometryType()
                if geom == QgsWkbTypes.LineGeometry: self.combo_rio.setLayer(layer)
                elif geom == QgsWkbTypes.PointGeometry: self.combo_nascente.setLayer(layer)
                elif geom == QgsWkbTypes.PolygonGeometry: self.combo_imovel.setLayer(layer)

    def _calculate_mf_math(self):
        mf, area = self.spin_mf_val.value(), self.spin_area_imovel.value()
        if mf > 0: self.label_res_mf.setText(f"Resultado: {(area/mf):.2f} MF")

    def _execute(self):
        bar = self.iface.messageBar()
        rio, nascente, imovel = self.combo_rio.currentLayer(), self.combo_nascente.currentLayer(), self.combo_imovel.currentLayer()
        if not imovel:
            bar.pushMessage("Ibiraté", "Selecione a camada de Limite do Imóvel.", level=Qgis.Warning, duration=6)
            return
        if not rio and not nascente:
            bar.pushMessage("Ibiraté", "Selecione ao menos uma camada de Cursos d'Água ou de Nascentes.", level=Qgis.Warning, duration=6)
            return

        dist_app = ForestRules.get_app_dist(self.combo_largura.currentIndex())
        use_cons = self.check_consolidado.isChecked()
        dist_cons = None
        if use_cons:
            if self._needs_exact_width():
                lo, hi = ForestRules.width_range(self.combo_largura.currentIndex())
                if not (lo <= self.spin_largura.value() <= hi):
                    bar.pushMessage("Ibiraté", f"A largura informada ({self.spin_largura.value():.1f} m) não corresponde à faixa selecionada ({self.combo_largura.currentText()}).", level=Qgis.Warning, duration=8)
                    return
            dist_cons = self._cons_river_distance()

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            layers, calc_crs = SpatialEngine.run_analysis(rio, nascente, imovel, dist_app, use_cons, dist_cons)
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            bar.pushMessage("Ibiraté - erro na análise", str(e), level=Qgis.Critical, duration=0)
            return
        QtWidgets.QApplication.restoreOverrideCursor()

        resumo = f"APP: {dist_app:.0f} m (rio) / 50 m (nascente)"
        if use_cons:
            resumo += f" | Uso consolidado: {dist_cons:.1f} m (rio) / 15 m (nascente)"
        bar.pushMessage(
            "Ibiraté",
            f"{len(layers)} camadas geradas. {resumo}. Cálculo em {calc_crs.authid()} ({calc_crs.description()}).",
            level=Qgis.Success, duration=10,
        )
