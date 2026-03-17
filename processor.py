# -*- coding: utf-8 -*-
"""
# Ibiraté - APP Analises | https://www.ibirate.com.br/
(C) 2026 by Poliana Cursino Betella | Pedro Cursino Betella Gomes
betella.poliana@gmail.com | pedro.cursino.gomes@gmail.com
"""

import processing
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsUnitTypes

class ForestRules:
    @staticmethod
    def get_app_dist(index):
        return {0: 30.0, 1: 50.0, 2: 100.0, 3: 200.0, 4: 500.0}.get(index, 30.0)

    @staticmethod
    def get_consolidado_dist_river(mf_index):
        return {0: 5.0, 1: 8.0, 2: 15.0, 3: 20.0, 4: 30.0}.get(mf_index, 5.0)

class SpatialEngine:
    @staticmethod
    def run_analysis(rio, nascente, imovel, dist_app, use_cons, mf_idx):
        try:
            # Usa o CRS do projeto se for métrico, caso contrário, detecta UTM
            calc_crs = SpatialEngine._get_calculation_crs(imovel)
            
            app_rio = SpatialEngine._buffer_metric(rio, dist_app, calc_crs)
            app_nascente = SpatialEngine._buffer_metric(nascente, 50.0, calc_crs)
            app_total = SpatialEngine._combine_and_clip([app_rio, app_nascente], imovel, "1_APP")
            
            SpatialEngine._difference(imovel, app_total, "2_Area_Remanescente_Fora_APP")

            if use_cons:
                dist_cons_r = ForestRules.get_consolidado_dist_river(mf_idx)
                cons_rio = SpatialEngine._buffer_metric(rio, dist_cons_r, calc_crs)
                cons_nascente = SpatialEngine._buffer_metric(nascente, 15.0, calc_crs)
                cons_total = SpatialEngine._combine_and_clip([cons_rio, cons_nascente], imovel, "3_Uso_Consolidado_Recomposicao")
                
                SpatialEngine._difference(imovel, cons_total, "4_Area_Remanescente_Fora_UsoConsolidado")
                SpatialEngine._difference(app_total, cons_total, "5_Faixa_APP_Passivel_de_Uso")

        except Exception as e:
            print(f"Ibiraté Error: {e}")

    @staticmethod
    def _get_calculation_crs(layer):
        """Retorna um CRS métrico seguro para cálculo sem disparar erros de grade .gsb"""
        project_crs = QgsProject.instance().crs()
        if project_crs.mapUnits() == QgsUnitTypes.DistanceMeters:
            return project_crs
        
        # Fallback para SIRGAS 2000 UTM Zone 23S (comum em SP/MG/PR) se o projeto for geográfico
        return QgsCoordinateReferenceSystem("EPSG:31983")

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