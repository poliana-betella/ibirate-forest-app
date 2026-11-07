# -*- coding: utf-8 -*-
"""
# Ibiraté - APP Analises | https://www.ibirate.com.br/
(C) 2026 by Poliana Cursino Betella | Pedro Cursino Betella Gomes
betella.poliana@gmail.com | pedro.cursino.gomes@gmail.com
"""

import processing
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform

class ForestRules:
    # Lei 12.651/2012, art. 4, I (APP de cursos d'agua), por faixa de largura:
    # 0: < 10 m | 1: 10-50 m | 2: 50-200 m | 3: 200-600 m | 4: > 600 m
    @staticmethod
    def get_app_dist(index):
        return {0: 30.0, 1: 50.0, 2: 100.0, 3: 200.0, 4: 500.0}.get(index, 30.0)

    @staticmethod
    def get_consolidado_dist_river(mf_index, width_index=0, width_m=None):
        """Faixa minima de recomposicao em curso d'agua (area consolidada).

        Lei 12.651/2012, art. 61-A, par. 1 a 4, e Decreto 7.830/2012, art. 19, par. 4:
        - ate 1 MF: 5 m | 1 a 2 MF: 8 m | 2 a 4 MF: 15 m (qualquer largura)
        - 4 a 10 MF e rio com ate 10 m de largura: 20 m
        - demais casos (> 10 MF, ou rio com mais de 10 m): metade da largura
          do rio, com minimo de 30 m e maximo de 100 m.
        """
        if mf_index in (0, 1, 2):
            return {0: 5.0, 1: 8.0, 2: 15.0}[mf_index]
        if mf_index == 3 and width_index == 0:
            return 20.0
        half = (width_m or 0.0) / 2.0
        return max(30.0, min(100.0, half))

    @staticmethod
    def width_range(width_index):
        return {0: (0.0, 10.0), 1: (10.0, 50.0), 2: (50.0, 200.0),
                3: (200.0, 600.0), 4: (600.0, 100000.0)}.get(width_index, (0.0, 10.0))

class SpatialEngine:
    @staticmethod
    def run_analysis(rio, nascente, imovel, dist_app, use_cons, dist_cons_rio=None):
        """Executa a analise. Retorna (lista de camadas criadas, CRS de calculo).
        Erros sao propagados para a interface mostrar ao usuario."""
        created = []
        calc_crs = SpatialEngine._get_calculation_crs(imovel)

        app_rio = SpatialEngine._buffer_metric(rio, dist_app, calc_crs)
        app_nascente = SpatialEngine._buffer_metric(nascente, 50.0, calc_crs)
        app_total = SpatialEngine._combine_and_clip([app_rio, app_nascente], imovel, "1_APP")
        created.append(app_total)
        created.append(SpatialEngine._difference(imovel, app_total, "2_Area_Remanescente_Fora_APP"))

        if use_cons:
            cons_rio = SpatialEngine._buffer_metric(rio, dist_cons_rio, calc_crs)
            cons_nascente = SpatialEngine._buffer_metric(nascente, 15.0, calc_crs)
            cons_total = SpatialEngine._combine_and_clip([cons_rio, cons_nascente], imovel, "3_Uso_Consolidado_Recomposicao")
            created.append(cons_total)
            created.append(SpatialEngine._difference(imovel, cons_total, "4_Area_Remanescente_Fora_UsoConsolidado"))
            created.append(SpatialEngine._difference(app_total, cons_total, "5_Faixa_APP_Passivel_de_Uso"))

        return [l for l in created if l is not None], calc_crs

    @staticmethod
    def utm_epsg_for(lon, lat):
        """EPSG do fuso UTM para um ponto em graus (WGS84/SIRGAS 2000).
        No Brasil usa SIRGAS 2000 / UTM (18N-22N: 31972-31976; 18S-25S: 31978-31985);
        fora dessas faixas usa WGS 84 / UTM (326xx norte, 327xx sul)."""
        zone = int((lon + 180.0) // 6.0) + 1
        zone = max(1, min(60, zone))
        if lat < 0 and 18 <= zone <= 25:
            return 31960 + zone
        if lat >= 0 and 18 <= zone <= 22:
            return 31954 + zone
        return (32700 if lat < 0 else 32600) + zone

    @staticmethod
    def _get_calculation_crs(layer):
        """CRS UTM do fuso onde esta o imovel (centro da extensao da camada).
        Os buffers sao calculados em metros nesse fuso, sem distorcao de escala,
        independentemente do CRS do projeto."""
        center = layer.extent().center()
        wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
        if layer.crs() != wgs84:
            tr = QgsCoordinateTransform(layer.crs(), wgs84, QgsProject.instance())
            center = tr.transform(center)
        epsg = SpatialEngine.utm_epsg_for(center.x(), center.y())
        return QgsCoordinateReferenceSystem(f"EPSG:{epsg}")

    @staticmethod
    def _buffer_metric(layer, dist, calc_crs):
        if not layer: return None
        
        # Reprojeção temporária para o cálculo
        temp = processing.run("native:reprojectlayer", {
            'INPUT': layer, 'TARGET_CRS': calc_crs, 'OUTPUT': 'TEMPORARY_OUTPUT'
        })['OUTPUT']
        
        # Buffer perfeitamente redondo (100 segmentos)
        buf = processing.run("native:buffer", {
            'INPUT': temp, 
            'DISTANCE': dist, 
            'SEGMENTS': 100, 
            'END_CAP_STYLE': 0, 
            'JOIN_STYLE': 0, 
            'DISSOLVE': True, 
            'OUTPUT': 'TEMPORARY_OUTPUT'
        })['OUTPUT']
        
        return processing.run("native:reprojectlayer", {
            'INPUT': buf, 'TARGET_CRS': QgsProject.instance().crs(), 'OUTPUT': 'TEMPORARY_OUTPUT'
        })['OUTPUT']

    @staticmethod
    def _combine_and_clip(layers, mask, name):
        valid = [l for l in layers if l is not None]
        if not valid: return None
        combined = valid[0]
        if len(valid) > 1:
            combined = processing.run("native:mergevectorlayers", {'LAYERS': valid, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
            combined = processing.run("native:dissolve", {'INPUT': combined, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        
        final = processing.run("native:clip", {'INPUT': combined, 'OVERLAY': mask, 'OUTPUT': 'memory:'})['OUTPUT']
        final.setName(name)
        QgsProject.instance().addMapLayer(final)
        return final

    @staticmethod
    def _difference(input_layer, overlay_layer, name):
        if not input_layer or not overlay_layer: return
        res = processing.run("native:difference", {'INPUT': input_layer, 'OVERLAY': overlay_layer, 'OUTPUT': 'memory:'})['OUTPUT']
        res.setName(name)
        QgsProject.instance().addMapLayer(res)
        return res