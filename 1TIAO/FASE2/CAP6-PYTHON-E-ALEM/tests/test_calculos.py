"""
test_calculos.py
----------------
Testes unitarios para as funcoes agronomicas e financeiras do PerdaZero.
"""

import os
import sys
import unittest

# Adiciona pasta src ao path para os testes
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import calculos


class TestCalculosAgronomicos(unittest.TestCase):

    def test_calcular_kg_total(self):
        amostras = {
            "toco": 2.5,
            "tolete": 3.0,
            "cana_inteira": 1.0,
            "ponteiro": 0.5,
            "estilhaco": 0.5,
        }
        total = calculos.calcular_kg_total(amostras)
        self.assertEqual(total, 7.5)

    def test_calcular_perda_t_ha(self):
        # 10 m2 amostrados, 5 kg recolhidos
        # 5 / 10 * 10 = 5.0 t/ha
        perda = calculos.calcular_perda_t_ha(5.0, 10.0)
        self.assertEqual(perda, 5.0)

    def test_calcular_perda_t_ha_area_invalida(self):
        with self.assertRaises(ValueError):
            calculos.calcular_perda_t_ha(5.0, 0)

    def test_calcular_perda_pct(self):
        # perda 10 t/ha, produtividade 90 t/ha => producao total 100 t/ha => 10.0%
        pct = calculos.calcular_perda_pct(10.0, 90.0)
        self.assertEqual(pct, 10.0)

    def test_calcular_prejuizo(self):
        # 5 t/ha perda, 10 ha, 140 kg ATR/t, R$ 1.20 por kg ATR
        # 5 * 10 * 140 * 1.20 = 8400.00
        prejuizo = calculos.calcular_prejuizo(5.0, 10.0, 140.0, 1.20)
        self.assertEqual(prejuizo, 8400.00)

    def test_classificar_perda(self):
        faixas = (2.5, 5.0, 10.0)
        self.assertEqual(calculos.classificar_perda(2.0, faixas), "BAIXA")
        self.assertEqual(calculos.classificar_perda(3.5, faixas), "MODERADA")
        self.assertEqual(calculos.classificar_perda(7.5, faixas), "ALTA")
        self.assertEqual(calculos.classificar_perda(12.0, faixas), "CRITICA")

    def test_composicao_perdas(self):
        amostras = {
            "toco": 5.0,
            "tolete": 5.0,
            "cana_inteira": 0.0,
            "ponteiro": 0.0,
            "estilhaco": 0.0,
        }
        comp = calculos.composicao_perdas(amostras)
        self.assertEqual(comp["toco"], 50.0)
        self.assertEqual(comp["tolete"], 50.0)
        self.assertEqual(comp["estilhaco"], 0.0)


if __name__ == "__main__":
    unittest.main()
