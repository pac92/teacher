"""Clasifica cada pregunta en temas (y de ahí en bloques de contenido).

Puntúa palabras clave del enunciado (peso 1) y de los criterios de corrección
(peso 0,4). Las correcciones manuales en overrides.json tienen prioridad.

Bloques LOMCE (RD 1105/2014, PEvAU Andalucía 2017-2024; mismos 5 bloques que
la LOE para 2008-2016):
  1 Base molecular y fisicoquímica de la vida
  2 Morfología, estructura y funciones celulares
  3 Herencia. Genética molecular (y evolución)
  4 Microorganismos y sus aplicaciones. Biotecnología
  5 Autodefensa de los organismos. Inmunología
Bloques LOMLOE (RD 243/2022, PAU desde 2025):
  A Biomoléculas · B Genética molecular · C Biología celular ·
  D Metabolismo · E Biotecnología (e ingeniería genética) · F Inmunología
  X = genética mendeliana, que la LOMLOE saca de Biología de 2º (pasa a 1º)
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "out")
OVR = os.path.join(ROOT, "tools", "overrides.json")

# id: (etiqueta, bloque LOMCE, bloque LOMLOE)
TOPICS = {
    "agua": ("Agua, sales minerales y disoluciones", 1, "A"),
    "glucidos": ("Glúcidos", 1, "A"),
    "lipidos": ("Lípidos", 1, "A"),
    "proteinas": ("Proteínas", 1, "A"),
    "enzimas": ("Enzimas y vitaminas", 1, "D"),
    "nucleicos": ("Nucleótidos y ácidos nucleicos", 1, "A"),
    "celula": ("Organización celular y orgánulos", 2, "C"),
    "membrana": ("Membrana y transporte", 2, "C"),
    "division": ("Ciclo celular, mitosis y meiosis", 2, "C"),
    "catabolismo": ("Catabolismo: respiración y fermentación", 2, "D"),
    "anabolismo": ("Anabolismo: fotosíntesis y quimiosíntesis", 2, "D"),
    "mendel": ("Genética mendeliana", 3, "X"),
    "molecular": ("Replicación, expresión génica y código", 3, "B"),
    "mutacion": ("Mutaciones y evolución", 3, "B"),
    "microbio": ("Microorganismos", 4, "E"),
    "biotec": ("Biotecnología e ingeniería genética", 4, "E"),
    "inmuno": ("Inmunología", 5, "F"),
}

KW = {
    "agua": [r"\bagua\b", r"sales minerales", r"\bosmo", r"hipert[oó]nic", r"hipot[oó]nic", r"isot[oó]nic",
             r"plasm[oó]lisis", r"turgen", r"hem[oó]lisis", r"tamp[oó]n", r"\bph\b", r"calor espec[ií]fico",
             r"disolvente", r"dipolo", r"capilaridad", r"densidad", r"precipitad", r"disoluci[oó]n", r"salin"],
    "glucidos": [r"gl[uú]cid", r"monosac[aá]rid", r"disac[aá]rid", r"polisac[aá]rid", r"almid[oó]n", r"celulosa",
                 r"gluc[oó]geno", r"sacarosa", r"lactosa", r"maltosa", r"\bribosa", r"fructosa", r"aldosa", r"cetosa",
                 r"glucos[ií]dic", r"quitina", r"hexosa", r"pentosa", r"galactosa", r"an[oó]mer", r"haworth",
                 r"fischer", r"triosa", r"az[uú]car", r"oligosac"],
    "lipidos": [r"l[ií]pid", r"[aá]cido[s]? graso", r"triacilglic", r"triglic[eé]r", r"fosfol[ií]pid", r"esteroid",
                r"colesterol", r"saponifica", r"jab[oó]n", r"esfingol", r"terpeno", r"carotenoide", r"\bceras?\b",
                r"\bgrasas?\b", r"anfip[aá]tic", r"insaturad", r"esterificaci", r"\bhormonas? esteroid"],
    "proteinas": [r"prote[ií]na", r"amino[aá]cido", r"pept[ií]dic", r"estructura (primaria|secundaria|terciaria|cuaternaria)",
                  r"h[eé]lice", r"l[aá]mina plegada", r"desnaturaliz", r"polip[eé]ptid", r"holoprote", r"heteroprote",
                  r"anf[oó]ter", r"conformaci[oó]n", r"puentes? disulfuro"],
    "enzimas": [r"enzim", r"cataliz", r"energ[ií]a de activaci", r"centro activo", r"inhibi", r"coenzima", r"cofactor",
                r"vitamina", r"michaelis", r"alost[eé]ric", r"apoenzima", r"holoenzima", r"sustrato", r"velocidad de (la )?reacci"],
    "nucleicos": [r"nucle[oó]tid", r"nucle[oó]sid", r"[aá]cidos? nucleic", r"doble h[eé]lice", r"watson", r"chargaff",
                  r"bases? nitrogenad", r"\badn\b", r"\barn\b", r"arnt|arnm|arnr|arn transferente|arn mensajero|arn ribos",
                  r"desoxirribo", r"\batp\b", r"\bpuric|\bpirimid", r"adenina|timina|guanina|citosina|uracilo"],
    "celula": [r"procariot", r"eucariot", r"org[aá]nul", r"mitocondri", r"cloroplast", r"ribosom", r"ret[ií]culo",
               r"golgi", r"lisosom", r"peroxisom", r"vacuola", r"citoesqueleto", r"microt[uú]bul", r"centriolo",
               r"centrosoma", r"\bcilio", r"flagelo", r"n[uú]cleo\b", r"nucl[eé]olo", r"envoltura nuclear", r"poro nuclear",
               r"cromatina", r"pared celular", r"teor[ií]a celular", r"endosimbi", r"microscop", r"c[eé]lula (animal|vegetal)",
               r"citosol", r"dictiosoma", r"hialoplasma", r"inclusiones", r"estructuras? (celulares|numeradas)"],
    "membrana": [r"membrana plasm", r"mosaico fluido", r"transporte (activo|pasivo)", r"difusi[oó]n", r"endocitosis",
                 r"exocitosis", r"pinocitosis", r"bomba de sodio", r"permeab", r"glucoc[aá]lix", r"transportador",
                 r"canal(es)? i[oó]nic", r"uniones (celulares|estrechas|adherentes)", r"desmosoma", r"\bmembranas?\b"],
    "division": [r"mitosis", r"meiosis", r"ciclo celular", r"interfase", r"profase", r"metafase", r"anafase", r"telofase",
                 r"citocinesis", r"sobrecruzamiento", r"quiasma", r"\bhuso\b", r"crom[aá]tida", r"bivalente",
                 r"haploide", r"diploide", r"cromosomas? hom[oó]log", r"divisi[oó]n celular", r"\bg1\b|\bg2\b|fase s\b",
                 r"gametos?", r"recombinaci[oó]n"],
    "catabolismo": [r"catab[oó]l", r"gluc[oó]lisis", r"krebs", r"(beta|β|b)[- ]?oxidaci", r"cadena (respiratoria|de transporte)",
                    r"fosforilaci[oó]n oxidativa", r"respiraci[oó]n (celular|aer)", r"fermentaci", r"acetil", r"piruv",
                    r"atp ?sintasa", r"\bnadh", r"tricarbox", r"rendimiento energ", r"aerobi", r"anaerobi", r"metabolismo",
                    r"\blactato\b|l[aá]ctic", r"etanol|alcoh[oó]lica", r"respiraci[oó]n"],
    "anabolismo": [r"fotos[ií]ntesis", r"fase luminosa", r"fase oscura", r"calvin", r"fotosistema", r"fotofosforilaci",
                   r"quimios[ií]ntesis", r"rubisco", r"clorofila", r"fotorrespiraci", r"anab[oó]l", r"gluconeog",
                   r"aut[oó]trof", r"fot[oó]lisis", r"estroma", r"tilacoide", r"\bnadph", r"fijaci[oó]n del co2|co2"],
    "mendel": [r"mendel", r"genotipo", r"fenotipo", r"homocig", r"heterocig", r"\balel", r"dominante", r"recesiv",
               r"cruzamiento", r"ligad[ao] al sexo", r"codominan", r"herencia intermedia", r"retrocruzamiento",
               r"hemofilia", r"daltonismo", r"grupos? sangu[ií]neo", r"\bf1\b|\bf2\b", r"ligamiento", r"autos[oó]mic",
               r"descendencia", r"progenitor", r"[aá]rbol geneal|genealog[ií]a|pedigr", r"cromosomas? sexual",
               r"herencia", r"h[ií]brido", r"leyes de mendel", r"ratones|guisantes|moscas|plantas? de flores"],
    "molecular": [r"replicaci[oó]n", r"transcripci[oó]n", r"traducci[oó]n", r"c[oó]digo gen[eé]tico", r"cod[oó]n",
                  r"anticod[oó]n", r"arn polimerasa", r"adn polimerasa", r"okazaki", r"cebador", r"horquilla",
                  r"semiconservativ", r"promotor", r"intr[oó]n", r"ex[oó]n", r"splicing|maduraci[oó]n del arn",
                  r"oper[oó]n", r"expresi[oó]n (g[eé]nica|del gen)", r"s[ií]ntesis de prote[ií]nas", r"\bgen(es)?\b",
                  r"dogma", r"secuencia de (bases|nucle[oó]tidos|amino)", r"hebra|cadena molde|cadena codificante",
                  r"ligasa|helicasa|topoisomerasa|primasa", r"5['’´]|3['’´]"],
    "mutacion": [r"mutaci", r"mutag", r"evoluci", r"darwin", r"lamarck", r"selecci[oó]n natural", r"neodarwin",
                 r"especiaci", r"variabilidad gen[eé]tica", r"c[aá]ncer", r"radiaci[oó]n", r"poliploid|aneuploid",
                 r"s[ií]ndrome de down|trisom[ií]a", r"adaptaci[oó]n", r"pruebas de la evoluci"],
    "microbio": [r"microorganism", r"bacteri", r"\bvirus", r"bacteri[oó]fago", r"\bfagos?\b", r"ciclo l[ií]tico",
                 r"lisog[eé]n", r"\bhongos?\b", r"levadura", r"protozoo", r"\balgas?\b", r"pri[oó]n", r"viroide",
                 r"\bgram\b", r"c[aá]pside", r"retrovirus", r"ciclos? biogeoqu", r"nitrifica|desnitrifica|fijaci[oó]n del nitr[oó]geno",
                 r"descomponedor", r"pat[oó]gen", r"antibi[oó]tic", r"microbio", r"acelular", r"conjugaci[oó]n|transducci[oó]n|transformaci[oó]n bacteriana",
                 r"esporas?", r"infecci", r"moh[oa]s?\b", r"microsc[oó]pic"],
    "biotec": [r"biotecnolog", r"ingenier[ií]a gen[eé]tica", r"adn recombinante", r"clonaci|\bclon", r"\bpcr\b",
               r"transg[eé]nic", r"enzimas? de restricci", r"\bvector", r"pl[aá]smido", r"c[eé]lulas madre",
               r"terapia g[eé]nica", r"crispr", r"biorremedia", r"industria (alimentaria|farmac[eé]utica)",
               r"yogur|\bpan\b|\bvino|cerveza|queso|vinagre", r"insulina", r"\bomg\b|organismos? modificad",
               r"depuraci[oó]n de aguas", r"biocombustible|biog[aá]s", r"proyecto genoma", r"secuenciaci"],
    "inmuno": [r"inmun", r"anticuerpo", r"ant[ií]geno", r"linfocito", r"macr[oó]fago", r"fagocit", r"vacun",
               r"suero(terapia)?", r"inflamaci", r"alergi|al[eé]rgic", r"autoinmun", r"\bsida\b|\bvih\b",
               r"trasplante|rechazo", r"complemento", r"interfer[oó]n", r"histamina", r"memoria inmun",
               r"respuesta (primaria|secundaria|humoral|celular)", r"barreras", r"inmunoglobulin", r"\btimo\b",
               r"c[eé]lulas plasm[aá]ticas", r"hipersensibilidad", r"\bmhc\b|\bhla\b", r"interleuc", r"lisozima",
               r"defensa", r"neutr[oó]filo|mastocito|bas[oó]filo|eosin[oó]filo", r"linfa|ganglios? linf",
               r"pat[oó]geno", r"infecci", r"seroterapia|sueroterapia"],
}
KWC = {k: [re.compile(p, re.I) for p in v] for k, v in KW.items()}


def fold(s):
    return unicodedata.normalize("NFC", s)


def scores(text, weight):
    t = fold(text)
    out = {}
    for k, pats in KWC.items():
        sc = 0.0
        for p in pats:
            n = len(p.findall(t))
            if n:
                sc += weight * min(n, 3) ** 0.7
        if sc:
            out[k] = sc
    return out


def classify(q):
    s = scores(q["text"], 1.0)
    for k, v in scores(q.get("crit_text", ""), 0.4).items():
        s[k] = s.get(k, 0) + v
    if not s:
        return ["celula"], {}
    ranked = sorted(s.items(), key=lambda kv: -kv[1])
    top = ranked[0][1]
    topics = [k for k, v in ranked if v >= 0.7 * top][:2]
    return topics, s


def main():
    db = json.load(open(os.path.join(OUT, "questions.json")))
    ovr = json.load(open(OVR)) if os.path.exists(OVR) else {}
    for q in db:
        topics, _ = classify(q)
        if q["id"] in ovr:
            topics = ovr[q["id"]]
        q["topics"] = topics
        q["lomce"] = sorted({TOPICS[t][1] for t in topics})
        q["lomloe"] = sorted({TOPICS[t][2] for t in topics})
    json.dump(db, open(os.path.join(OUT, "questions.json"), "w"), ensure_ascii=False, indent=0)
    if "-v" in sys.argv:
        for q in db:
            print(f"{q['id']:34s} {','.join(q['topics']):22s} {q['text'][:150]}")


if __name__ == "__main__":
    main()
