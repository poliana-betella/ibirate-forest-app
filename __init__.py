# -*- coding: utf-8 -*-
"""
Ibiraté - APP Analises | https://www.ibirate.com.br/
(C) 2026 by Poliana Cursino Betella | Pedro Cursino Betella Gomes
betella.poliana@gmail.com | pedro.cursino.gomes@gmail.com
"""

def classFactory(iface):
    from .app_compliance import AppCompliance
    return AppCompliance(iface)