"""Catálogo de exámenes: fichero de enunciado, fichero de criterios y metadatos.

tipo: Titular | Suplente | Reserva | Modelo  (Modelo = el zip no indica en qué
convocatoria se usó ese examen).
conv: convocatoria tal y como la indica el nombre del fichero/carpeta original.
"""

E = []


def add(year, tipo, conv, label, exam, crit, exam_pages=None, crit_pages=None, crit_file=None):
    E.append(dict(year=year, tipo=tipo, conv=conv, label=label, exam=exam,
                  crit=crit if crit_file is None else crit_file,
                  exam_pages=exam_pages, crit_pages=crit_pages))


# 2008: seis modelos sin convocatoria indicada
for n in range(1, 7):
    add(2008, "Modelo", "", f"Modelo {n}", f"2008/Biologia_{n}_-_Examen.pdf",
        [f for f in ["2008/Biologia_%d_-_Criterios_de_correccion.pdf" % n,
                     "2008/Biologia_%d_-_Criterios_de_Correccion.pdf" % n]])

# 2009: PDF escaneados, enunciado (págs. 1-2) + criterios (págs. 3-4)
for n in range(1, 7):
    add(2009, "Modelo", "", f"Modelo {n}", f"2009/biologia0{n}.pdf", f"2009/biologia0{n}.pdf",
        exam_pages=[0, 1], crit_pages=[2, 3])

_b10 = "2010/biologia/"
for conv, sub, tipo, lab, n in [
    ("Junio", "biologia_junio/biologia_junio", "Titular", "Titular", 1),
    ("Junio", "biologia_junio/biologia_junio_ra", "Reserva", "Reserva A", 2),
    ("Junio", "biologia_junio/biologia_junio_rb", "Reserva", "Reserva B", 5),
    ("Septiembre", "biologia_sept/biologia_sept", "Titular", "Titular", 3),
    ("Septiembre", "biologia_sept/biologia_sept_ra", "Reserva", "Reserva A", 6),
    ("Septiembre", "biologia_sept/biologia_sept_rb", "Reserva", "Reserva B", 4),
]:
    add(2010, tipo, conv, lab, f"{_b10}{sub}/_BIOLOGIA_-_EXAMEN_{n}_-_2010.pdf",
        f"{_b10}{sub}/BIOLOGIA_-_CRITERIOS_EXAMEN_{n}_-_2010.pdf")

for code, n in [("133B", 1), ("132A", 2), ("233A", 3), ("232A", 4), ("131A", 5), ("231B", 6)]:
    add(2011, "Modelo", "", f"Modelo {n}", f"2011/sel_2011_biologia/{code}-BIOLOGIA_-_EXAMEN_{n}-2011.pdf",
        f"2011/sel_2011_biologia/{code}-BIOLOGIA_-_CRITERIOS_EXAMEN_{n}-2011.pdf")

_b12 = "2012/sel_2012_biologia/"
for d, n, cfile in [("1_BIOLOGIA", 1, "CRITERIOS_1/BIOLOGIA-CRITERIOS_EXAMEN_1-2012.pdf"),
                    ("3_BIOLOGIA", 2, "CRITERIOS_3/BIOLOGIA-_CRITERIOS_EXAMEN_2-2012.pdf"),
                    ("2_BIOLOGIA", 3, "CRITERIOS_2/BIOLOGIA-CRITERIOS_EXAMEN_3-2012.pdf"),
                    ("6_BIOLOGIA", 4, "CRITERIOS_6/BIOLOGIA-CRITERIOS_EXAMEN_4-2012.pdf"),
                    ("4_BIOLOGIA", 5, "CRITERIOS_4/BIOLOGIA-CRITERIOS_EXAMEN_5-2012.pdf")]:
    add(2012, "Modelo", "", f"Modelo {n}", f"{_b12}{d}/BIOLOGIA-EXAMEN_{n}-2012.pdf", f"{_b12}{d}/{cfile}")
add(2012, "Titular", "Septiembre", "Titular", f"{_b12}BIOLOGIA-EXAMEN_6-2012_oficial_septiembre.pdf",
    f"{_b12}BIOLOGIA-CRITERIOS_EXAMEN_6-2012.pdf")

_b13 = "2013/sel_2013_biologia/"
for conv, sub, tipo, lab, n, cprefix in [
    ("Junio", "junio/titular", "Titular", "Titular", 6, "BIOLOGIA"),
    ("Junio", "junio/reserva_a", "Reserva", "Reserva A", 4, "BIOLOGIA"),
    ("Junio", "junio/reserva_b", "Reserva", "Reserva B", 3, "BIOLOGIA"),
    ("Septiembre", "septiembre/titular", "Titular", "Titular", 2, "BIOLOGIA"),
    ("Septiembre", "septiembre/reserva_a", "Reserva", "Reserva A", 1, "BIOLOGIA"),
    ("Septiembre", "septiembre/reserva_b", "Reserva", "Reserva B", 5, "BIOLOGIA"),
]:
    add(2013, tipo, conv, lab, f"{_b13}{sub}/BIOLOGIA-_EXAMEN_{n}-2012-13.pdf",
        f"{_b13}{sub}/{cprefix}-CRITERIOS_EXAMEN_{n}-2012-13.pdf")

_b14 = "2014/sel_2014_biologia/"
add(2014, "Titular", "Junio", "Titular", _b14 + "Biologia_JUN.pdf", _b14 + "BIOLOGIA_CRITERIOS_JUN.pdf")
add(2014, "Titular", "Septiembre", "Titular", _b14 + "Bilogia_SEPT.pdf", _b14 + "BIOLOGIA_CRITERIOS_SEPT.pdf")
for n, ex in [(2, "BIOLOGIA_EXAMEN_MODELO 2_13_14"), (3, "BIOLOGIA_EXAMEN_MODELO 3_13_14"),
              (5, "BIOLOGIA_EXAMEN_MODELO_5_13_14"), (6, "BIOLOGIA_EXAMEN_MODELO_6_13_14")]:
    add(2014, "Modelo", "", f"Modelo {n}", _b14 + ex.replace(" ", "_") + ".pdf",
        _b14 + f"BIOLOGIA_CRITERIOS_EXAMEN_MODELO_{n}_13_14.pdf")

_b15 = "2015/biologia/"
add(2015, "Modelo", "", "Modelo 1", _b15 + "MODELO_1_ANDALUCIA.pdf", _b15 + "CRITERIOS_MODELO_1_ANDALUCIA_BIOLOGIA.pdf")
add(2015, "Modelo", "", "Modelo 5", _b15 + "MODELO_5_ANDALUCIA.pdf", _b15 + "CRITERIOS_MODELO_5_ANDALUCIA_BIOLOGIA.pdf")
for n in (2, 3, 4, 6):
    add(2015, "Modelo", "", f"Modelo {n}", _b15 + f"Ua{n}BIOLOGIAexamen.pdf", _b15 + f"Ua{n}BIOLOGIAcriterios.pdf")

_b16 = "2016/biologia/"
add(2016, "Titular", "Junio", "Titular", _b16 + "titular_junio_6_EXAMEN_-BIOLOGIA.pdf",
    _b16 + "titular_junio_6_Criterios_BIOLOGIA.pdf")
add(2016, "Titular", "Septiembre", "Titular", _b16 + "titular_septiembre_Modelo_3_Andalucia_15-16-BIOLOGIA.pdf",
    _b16 + "titular_septiembre_Criterios_Modelo_3_Andalucia_15-16-BIOLOGIA.pdf")
add(2016, "Suplente", "Septiembre", "Suplente", _b16 + "suplemente_septiembre_Modelo_1_Andalucia_15-16-BIOLOGIA.pdf",
    _b16 + "suplemente_septiembre_Criterios_Modelo_1_Andalucia_15-16-BIOLOGIA.pdf")
add(2016, "Reserva", "", "Reserva A", _b16 + "reserva_a_Modelo_4_Andalucia_15-16-BIOLOGIA.docx.pdf",
    _b16 + "reserva_a_Criterios_Modelo_4_Andalucia_15-16-BIOLOGIA.pdf")
add(2016, "Reserva", "", "Reserva B", _b16 + "reserva_b_Modelo_6_Andalucia_15-16.pdf",
    _b16 + "reserva_b_Criterios_Modelo_6_Andalucia_15-16.pdf")

_b17 = "2017/biologia/"
for pre, tipo, conv, lab, n in [
    ("titular_junio", "Titular", "Junio", "Titular", 6),
    ("suplemente_junio", "Suplente", "Junio", "Suplente", 5),
    ("titular_septiembre", "Titular", "Septiembre", "Titular", 2),
    ("suplemente_septiembre", "Suplente", "Septiembre", "Suplente", 3),
    ("reserva_a", "Reserva", "", "Reserva A", 1),
    ("reserva_b", "Reserva", "", "Reserva B", 4),
]:
    add(2017, tipo, conv, lab, _b17 + f"{pre}_Modelo_{n}_Andalucia_16-17-BIOLOGIA.pdf",
        _b17 + f"{pre}_Criterios_Modelo_{n}_Andalucia_16-17-BIOLOGIA.pdf")

_b18 = "2018/biologia/"
for d, tipo, conv, lab in [
    ("titular_junio", "Titular", "Junio", "Titular"),
    ("suplente_junio", "Suplente", "Junio", "Suplente"),
    ("titular_septiembre", "Titular", "Septiembre", "Titular"),
    ("suplente_septiembre", "Suplente", "Septiembre", "Suplente"),
    ("Reserva_A", "Reserva", "", "Reserva A"),
    ("reserva_b", "Reserva", "", "Reserva B"),
]:
    add(2018, tipo, conv, lab, _b18 + d + "/EXAMEN-Biologia-17-18.pdf", _b18 + d + "/CRITERIOS-Biologia_17-18.pdf")

_b19 = "2019/sel_2019_biologia/"
for d, tipo, conv, lab, ex, cr in [
    ("Titular_Junio", "Titular", "Junio", "Titular", "Examenes_Biologia_A_y_B.pdf", "Biologia_Criterios_de_Correccion_A_y_B.pdf"),
    ("Suplente_Junio", "Suplente", "Junio", "Suplente", "Examenes_Biologia_-_A_y_B.pdf", "Biologia_-_Criterios_de_correccion.pdf"),
    ("Titular_Septiembre", "Titular", "Septiembre", "Titular", "Examenes_Biologia_-_A_y_B.pdf", "Biologia_-_Criterios_de_correccion_A_y_B.pdf"),
    ("Suplente_Septiembre", "Suplente", "Septiembre", "Suplente", "Examenes_Biologia_-_A_y_B.pdf", "Criterios_de_Correccion_-Biologia.pdf"),
    ("Reserva_A", "Reserva", "", "Reserva A", "Examenes_Biologia_-_A_y_B.pdf", "Biologia_-_Criterios_de_correccion.pdf"),
    ("Reserva_B", "Reserva", "", "Reserva B", "Examenes_Biologia_-_A_y_B.pdf", "Biologia_-_Criterios_de_Correccion.pdf"),
]:
    add(2019, tipo, conv, lab, _b19 + d + "/" + ex, _b19 + d + "/" + cr)

for n in range(1, 7):
    add(2020, "Modelo", "", f"Modelo {n}", f"2020/biologia/biologia_P_{n}.pdf", f"2020/biologia/biologia_C_{n}.pdf")

_b21 = "2021/biologia/"
for tipo, conv, lab, ex, cr in [
    ("Titular", "Ordinaria", "Titular", "ORD_TITULAR_BIOLOGIA-JUNIO-IMPRESO.pdf", "ORD_TITULAR_Criterios_Biologia.pdf"),
    ("Suplente", "Ordinaria", "Suplente", "ORD_SUPLENTE_Examen_Biologia.pdf", "ORD_SUPLENTE_Criterios_Biologia.pdf"),
    ("Reserva", "Ordinaria", "Reserva", "ORD_RESER_Examen_Biologia.pdf", "ORD_RESER_Criterios_Biologia.pdf"),
    ("Titular", "Extraordinaria", "Titular", "EXTRA_TITULAR_BIOLOGIA-JULIO-IMPRESO.pdf", "EXTRA_TITULAR_Criterios_Biologia.pdf"),
    ("Suplente", "Extraordinaria", "Suplente", "EXTRA_SUPLENTE_Examen_Biologia.pdf", "EXTRA_SUPLENTE_Criterios_Biologia.pdf"),
    ("Reserva", "Extraordinaria", "Reserva B", "EXTRA_RESERVA_B_Examen_Biologia.pdf", "EXTRA_RESERVA_B_Criterios_Biologia.pdf"),
]:
    add(2021, tipo, conv, lab, _b21 + ex, _b21 + cr)

_b22 = "2022/biologia/"
for c, conv in [("ORD", "Ordinaria"), ("EXTRA", "Extraordinaria")]:
    add(2022, "Titular", conv, "Titular", _b22 + f"IMPRESO-BIOLOGIA-{c}-TITULAR-EXAMEN.pdf", _b22 + f"BIOLOGIA-{c}-TITULAR-CRITERIOS.pdf")
    add(2022, "Suplente", conv, "Suplente", _b22 + f"BIOLOGIA-{c}-SUPLENTE-EXAMEN.pdf", _b22 + f"BIOLOGIA-{c}-SUPLENTE-CRITERIOS.pdf")
    add(2022, "Reserva", conv, "Reserva", _b22 + f"BIOLOGIA-{c}-RESERVA-EXAMEN.pdf", _b22 + f"BIOLOGIA-{c}-RESERVA-CRITERIOS.pdf")

for t, tipo in [("TITULAR", "Titular"), ("SUPLENTE", "Suplente"), ("RESERVA", "Reserva")]:
    for ab in "AB":
        add(2023, tipo, ab, f"{tipo} {ab}", f"2023/biologia/EXAMEN_BIOLOGIA_{t}_{ab}.pdf",
            f"2023/biologia/CRITERIOS_BIOLOGIA_{t}_{ab}.pdf")

for tipo in ("Titular", "Suplente", "Reserva"):
    for ab in "AB":
        add(2024, tipo, ab, f"{tipo} {ab}", f"2024/BIOLOGIA/Examen_{tipo}-{ab}_BIOLOGIA.pdf",
            f"2024/BIOLOGIA/Criterios_{tipo}-{ab}_BIOLOGIA.pdf")

for name, tipo, ab, lab in [("Titular-A", "Titular", "A", "Titular A"), ("Titular2-A", "Titular", "A", "Titular 2 A"),
                            ("Suplente1-A", "Suplente", "A", "Suplente A"), ("Titular-B", "Titular", "B", "Titular B"),
                            ("Suplente1-B", "Suplente", "B", "Suplente 1 B"), ("Suplente2-B", "Suplente", "B", "Suplente 2 B")]:
    add(2025, tipo, ab, lab, f"2025/Biologia/Examen_{name}_Biologia.pdf", f"2025/Biologia/Criterios_{name}_Biologia.pdf")


def era(year):
    if year <= 2019:
        return 1
    if year <= 2024:
        return 2
    return 3
