// Ciclos biogeoquímicos — datos completos con hotspots incluidos
// Cargado como <script> regular; expone window.BGQ_CYCLES

const CYCLES = {

  // ── CARBONO ───────────────────────────────────────────────────────────────
  carbon: {
    id: 'carbon', title: 'Ciclo del Carbono', symbol: 'C',
    image: './Carbono.png', imgW: 1688, imgH: 1125,
    accent: '#a78bfa',
    typeColors: {
      atmospheric: '#a78bfa', terrestrial: '#34d399', marine: '#38bdf8',
      geological: '#fbbf24', anthropogenic: '#f87171', volcanic: '#fb923c',
    },
    typeLabels: {
      atmospheric: 'Reservorio atmosférico', terrestrial: 'Biosfera terrestre',
      marine: 'Océano / marino', geological: 'Geología',
      anthropogenic: 'Antropogénico', volcanic: 'Volcánico',
    },
    elements: [
      // ── RESERVORIOS ────────────────────────────────────────────────────────
      {
        id: 'co2_atm', label: 'CO₂ atmosférico', type: 'atmospheric', kind: 'reservoir', x: 43, y: 5.5,
        content: {
          tag: 'Reservorio atmosférico', stock: '~870 GtC · 421 ppm (2023)',
          simple: [
            { p: 'El dióxido de carbono (CO₂) es el principal gas de efecto invernadero de la atmósfera terrestre. Las plantas y otros organismos fotosintéticos lo absorben del aire para fabricar materia orgánica.' },
            { p: 'Su concentración ha aumentado considerablemente desde la revolución industrial debido a la quema de combustibles fósiles y la deforestación, pasando de 280 ppm preindustriales a más de 421 ppm en 2023.' },
          ],
          sections: [
            { p: 'El dióxido de carbono atmosférico constituye el nexo central del ciclo del carbono. Aunque representa solo el 0,042 % del volumen atmosférico (~421 ppm en 2023), su papel como gas de efecto invernadero lo convierte en regulador clave del clima terrestre.' },
            { p: 'En épocas preindustriales la concentración era de ~280 ppm. Desde 1750, la quema de combustibles fósiles y la deforestación han elevado ese valor en más de un 50 %, a una tasa de ~2,5 ppm/año.' },
            { h: 'Balance de masas' },
            { eq: '\\frac{d[\\text{CO}_2]}{dt} = F_{\\text{fósil}} + F_{\\text{deforest.}} - F_{\\text{océano}} - F_{\\text{tierra}}', display: true },
            { p: 'Actualmente la tasa de acumulación neta es de ~5 GtC/año. El tiempo de residencia de una molécula frente al intercambio biológico es de ~4 años, pero la re-equilibración completa con el océano profundo tarda cientos a miles de años.' },
            { h: 'Efecto invernadero' },
            { p: 'El CO₂ absorbe radiación infrarroja mediante transiciones vibro-rotacionales. El forzamiento radiativo se aproxima como:' },
            { eq: '\\Delta F \\approx 5{,}35 \\cdot \\ln\\!\\left(\\frac{C}{C_0}\\right) \\; [\\text{W m}^{-2}]', display: true },
          ]
        }
      },
      {
        id: 'seres_terres', label: 'Seres vivos terrestres', type: 'terrestrial', kind: 'reservoir', x: 35.5, y: 36,
        content: {
          tag: 'Reservorio biótico terrestre', stock: '~550 GtC',
          simple: [
            { p: 'Las plantas, animales, hongos y bacterias que viven en tierra forman la biosfera terrestre. Las plantas son los principales almacenes de carbono: lo capturan del aire mediante la fotosíntesis y lo incorporan a su biomasa.' },
            { p: 'Cuando mueren o son descompuestas, ese carbono vuelve al suelo y a la atmósfera. Los bosques tropicales son especialmente importantes porque almacenan enormes cantidades de carbono en su madera y en el suelo.' },
          ],
          sections: [
            { p: 'La biosfera terrestre almacena ~550 GtC: plantas vasculares (~450 GtC), suelo y microbiota (~70 GtC), animales y hongos (~2 GtC). La biomasa vegetal supera con creces a la animal, siendo los bosques tropicales el mayor sumidero terrestre.' },
            { h: 'Productividad' },
            { p: 'La Productividad Primaria Bruta (GPP) global es ~120 GtC/año. Tras la respiración autótrofa (~60 GtC/año) queda una Productividad Primaria Neta (NPP) de ~60 GtC/año, que alimenta a los heterótrofos y al suelo.' },
            { eq: '\\text{NPP} = \\text{GPP} - R_a', display: true },
            { p: 'El tiempo de residencia varía: hojas (~1 año), madera (~50 años), madera de bosques primarios (> 200 años). Las perturbaciones (incendios, tala) liberan este carbono almacenado.' },
          ]
        }
      },
      {
        id: 'co2_dis', label: 'CO₂ disuelto', type: 'marine', kind: 'reservoir', x: 76, y: 35,
        content: {
          tag: 'Reservorio oceánico (DIC)', stock: '~38 000 GtC',
          simple: [
            { p: 'El CO₂ de la atmósfera se disuelve fácilmente en el agua del océano, donde forma ácido carbónico, bicarbonato y carbonato. El océano es el mayor reservorio activo de carbono del planeta, almacenando unas 50 veces más carbono que la atmósfera.' },
            { p: 'La absorción de tanto CO₂ está haciendo que el agua del mar se vuelva más ácida —un fenómeno llamado acidificación oceánica— lo que afecta gravemente a corales, moluscos y otros organismos con conchas de carbonato.' },
          ],
          sections: [
            { p: 'El Carbono Inorgánico Disuelto (DIC) oceánico es el mayor reservorio activo del ciclo, ~45 veces el CO₂ atmosférico. Se distribuye entre tres especies en equilibrio:' },
            { eq: '\\text{CO}_2(aq) + \\text{H}_2\\text{O} \\rightleftharpoons \\text{H}_2\\text{CO}_3 \\rightleftharpoons \\text{HCO}_3^- + \\text{H}^+ \\rightleftharpoons \\text{CO}_3^{2-} + 2\\,\\text{H}^+', display: true },
            { p: 'A pH 8,1 (actual), el $\\text{HCO}_3^-$ representa ~91 % del DIC. La disolución obedece la ley de Henry:' },
            { eq: '[\\text{CO}_2]_{aq} = K_H \\cdot p\\text{CO}_2, \\quad K_H \\approx 3{,}4 \\times 10^{-2}\\;\\text{mol L}^{-1}\\text{atm}^{-1}', display: true },
            { h: 'Acidificación oceánica' },
            { p: 'El exceso de CO₂ antropogénico absorbido desplaza el equilibrio hacia la derecha, reduciendo el pH (ya bajó 0,1 unidades desde 1800, equivalente a un 26 % de aumento de acidez) y disminuyendo la saturación de $\\text{CaCO}_3$, amenazando corales y moluscos.' },
          ]
        }
      },
      {
        id: 'seres_mar', label: 'Seres vivos marinos', type: 'marine', kind: 'reservoir', x: 75, y: 50,
        content: {
          tag: 'Reservorio biótico marino', stock: '~3 GtC',
          simple: [
            { p: 'El fitoplancton —algas microscópicas que flotan en la superficie del mar— realiza casi la mitad de toda la fotosíntesis del planeta. A pesar de su pequeño tamaño, fija grandes cantidades de carbono y produce aproximadamente la mitad del oxígeno atmosférico.' },
            { p: 'El zooplancton, los peces y otros organismos marinos se alimentan del fitoplancton, formando las redes tróficas marinas. Al igual que en tierra, los seres vivos marinos incorporan carbono mediante la fotosíntesis y lo liberan por la respiración.' },
          ],
          sections: [
            { p: 'Aunque el stock de biomasa marina es diminuto (~3 GtC) comparado con la terrestre, su tasa metabólica es altísima. El fitoplancton fija ~50 GtC/año — casi la mitad de la fotosíntesis global — y se regenera en días.' },
            { h: 'Bomba biológica' },
            { p: 'El fitoplancton muerto y las heces del zooplancton forman partículas orgánicas que se hunden (nieve marina), exportando carbono al océano profundo. Solo ~0,1 GtC/año llega al lecho marino y se preserva.' },
            { eq: '\\text{C}_{\\text{export}} \\approx \\text{NPP}_{\\text{marino}} \\times e\\text{-ratio} \\approx 50 \\times 0{,}1 = 5\\;\\text{GtC/año}', display: true },
          ]
        }
      },
      {
        id: 'comb_fos', label: 'Combustibles fósiles', type: 'geological', kind: 'reservoir', x: 26.3, y: 57,
        content: {
          tag: 'Reservorio fósil', stock: '~3 700 GtC',
          simple: [
            { p: 'El carbón, el petróleo y el gas natural son restos de organismos que vivieron hace millones de años y quedaron enterrados bajo la tierra. A lo largo del tiempo, la presión y el calor transformaron esa materia orgánica en combustibles ricos en carbono.' },
            { p: 'Al quemarlos, liberamos a la atmósfera el carbono que esos organismos habían almacenado durante millones de años. Este proceso ocurre a un ritmo mucho más rápido del que los sistemas naturales pueden absorber.' },
          ],
          sections: [
            { p: 'Los combustibles fósiles son carbono orgánico antiguo preservado en sedimentos anóxicos durante millones de años: carbón (~2 900 GtC), petróleo (~250 GtC) y gas natural (~140 GtC).' },
            { h: 'Combustión' },
            { eq: '\\text{C}_n\\text{H}_{2n+2} + \\frac{3n+1}{2}\\,\\text{O}_2 \\rightarrow n\\,\\text{CO}_2 + (n+1)\\,\\text{H}_2\\text{O} + \\Delta H', display: true },
            { p: 'La humanidad extrae y quema ~10,2 GtC/año (2022). Las reservas probadas restantes (~800 GtC quemables) superarían los 1,5 °C de calentamiento si se consumen en su totalidad.' },
          ]
        }
      },
      {
        id: 'rocas_carb', label: 'Rocas carbonatadas', type: 'geological', kind: 'reservoir', x: 43.8, y: 73.8,
        content: {
          tag: 'Reservorio litológico', stock: '~60 000 000 GtC',
          simple: [
            { p: 'Las calizas y otras rocas carbonatadas almacenan la mayor cantidad de carbono del planeta. Se formaron a partir de las conchas y esqueletos de organismos marinos acumulados en el fondo del océano durante millones de años.' },
            { p: 'Son tan abundantes que su reserva de carbono es miles de veces mayor que la de la atmósfera. El CO₂ que contienen solo vuelve a la atmósfera muy lentamente, a través del metamorfismo y el volcanismo.' },
          ],
          sections: [
            { p: 'Las rocas carbonatadas (caliza CaCO₃; dolomita CaMg(CO₃)₂) almacenan en la litosfera un stock ~70 000 veces mayor que la atmósfera. Son el reservorio más grande del ciclo del carbono.' },
            { h: 'Ciclo de Urey' },
            { eq: '\\text{CaSiO}_3 + \\text{CO}_2 \\rightarrow \\text{CaCO}_3 + \\text{SiO}_2', display: true },
            { h: 'Meteorización carbonatada' },
            { eq: '\\text{CaCO}_3 + \\text{CO}_2 + \\text{H}_2\\text{O} \\rightleftharpoons \\text{Ca}^{2+} + 2\\,\\text{HCO}_3^-', display: true },
          ]
        }
      },
      {
        id: 'sedimentos', label: 'Sedimentos', type: 'geological', kind: 'reservoir', x: 81, y: 73.8,
        content: {
          tag: 'Reservorio sedimentario', stock: '~3 000 GtC orgánicos',
          simple: [
            { p: 'Cuando los organismos marinos mueren, sus restos se hunden y se acumulan en el fondo del océano. Con el tiempo, estos sedimentos se compactan y pueden transformarse en rocas carbonatadas o en roca madre del petróleo.' },
            { p: 'Es un proceso muy lento que retira carbono del ciclo activo durante millones de años. Los sedimentos son una etapa clave en el almacenamiento geológico del carbono.' },
          ],
          sections: [
            { p: 'Los sedimentos marinos acumulan carbono procedente de la lluvia de partículas orgánicas (nieve marina) y de las conchas de CaCO₃. El stock orgánico asciende a ~3 000 GtC.' },
            { h: 'Diagénesis' },
            { eq: '2\\,\\text{CH}_2\\text{O} + \\text{SO}_4^{2-} \\rightarrow \\text{H}_2\\text{S} + 2\\,\\text{HCO}_3^-', display: true },
            { p: 'La línea de compensación de calcita (CCD, ~4 500 m) disuelve los carbonatos que caen por debajo de ella, limitando su preservación en grandes profundidades.' },
          ]
        }
      },
      {
        id: 'litosfera', label: 'Litosfera', type: 'geological', kind: 'reservoir', x: 6.2, y: 73.5,
        content: {
          tag: 'Reservorio mantélico y cortical', stock: '~100 000 000 GtC',
          simple: [
            { p: 'La litosfera —corteza y manto terrestre— es el reservorio de carbono más profundo del planeta. El carbono que llega al manto a través de la subducción puede permanecer allí durante decenas de millones de años.' },
            { p: 'Parte de ese carbono vuelve a la superficie a través de volcanes y fumarolas, cerrando el ciclo geológico. Sin este flujo volcánico, el CO₂ atmosférico se habría agotado hace miles de millones de años.' },
          ],
          sections: [
            { p: 'La litosfera profunda y el manto contienen el mayor stock de carbono del planeta, principalmente en forma de carbonatos minerales, grafito, diamante y CO₂ en fluidos. Regula el CO₂ atmosférico en escalas de millones de años.' },
            { h: 'Desgasificación mantélica' },
            { p: 'El manto pierde CO₂ por volcanismo en dorsales oceánicas (~0,05 GtC/año), arcos volcánicos (~0,03 GtC/año) y puntos calientes.' },
            { h: 'Ciclo carbono-silicato a largo plazo' },
            { p: 'El ciclo completo Litosfera → Atmósfera → Océano → Sedimentos → Subducción → Litosfera actúa como termostato planetario en escalas de $10^7$–$10^9$ años.' },
          ]
        }
      },
      // ── FLUJOS ─────────────────────────────────────────────────────────────
      {
        id: 'fotosintesis_t', label: 'Fotosíntesis terrestre', type: 'terrestrial', kind: 'flow', x: 38, y: 19,
        content: {
          tag: 'Flujo biótico terrestre', stock: '~120 GtC/año (GPP)',
          simple: [
            { p: 'La fotosíntesis es el proceso por el que las plantas capturan el CO₂ del aire y, usando la energía de la luz solar, lo transforman en materia orgánica. Es el principal mecanismo por el que el carbono entra en los seres vivos.' },
            { p: 'Las plantas con metabolismo C4, como el maíz o la caña de azúcar, son más eficientes en climas cálidos y secos.' },
          ],
          sections: [
            { p: 'La fotosíntesis oxigénica convierte CO₂ atmosférico y agua en glucosa usando energía solar. Es el flujo de entrada más grande del ciclo biológico rápido.' },
            { h: 'Reacción global' },
            { eq: '6\\,\\text{CO}_2 + 6\\,\\text{H}_2\\text{O} \\xrightarrow{h\\nu} \\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\,\\text{O}_2', display: true },
            { h: 'Ciclo de Calvin' },
            { eq: '3\\,\\text{CO}_2 + 9\\,\\text{ATP} + 6\\,\\text{NADPH} \\rightarrow \\text{G3P} + 9\\,\\text{ADP} + 8\\,\\text{P}_i + 6\\,\\text{NADP}^+', display: true },
          ]
        }
      },
      {
        id: 'resp_t', label: 'Respiración celular terrestre', type: 'terrestrial', kind: 'flow', x: 50, y: 19,
        content: {
          tag: 'Flujo biótico terrestre', stock: '~120 GtC/año',
          simple: [
            { p: 'Todos los seres vivos terrestres obtienen energía descomponiendo la materia orgánica. En este proceso consumen oxígeno y liberan CO₂ a la atmósfera.' },
            { p: 'La respiración del suelo, realizada por bacterias y hongos que descomponen la materia muerta, devuelve grandes cantidades de carbono a la atmósfera cada año. Con el aumento de la temperatura, este proceso se acelera.' },
          ],
          sections: [
            { p: 'La respiración aerobia se divide en respiración autótrofa ($R_a$ ~60 GtC/año) y heterótrofa ($R_h$ ~60 GtC/año, animales, hongos, bacterias del suelo).' },
            { h: 'Reacción global' },
            { eq: '\\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\,\\text{O}_2 \\rightarrow 6\\,\\text{CO}_2 + 6\\,\\text{H}_2\\text{O} + 36\\,\\text{ATP}', display: true },
            { h: 'Respiración del suelo' },
            { eq: 'R_s = R_{10} \\cdot Q_{10}^{(T-10)/10}, \\quad Q_{10} \\approx 2{,}4', display: true },
          ]
        }
      },
      {
        id: 'erupcion', label: 'Erupción volcánica', type: 'volcanic', kind: 'flow', x: 9, y: 19,
        content: {
          tag: 'Flujo geológico', stock: '~0,3 GtC/año',
          simple: [
            { p: 'Los volcanes liberan CO₂ procedente del interior de la Tierra. Este carbono, atrapado en el manto durante millones de años, escapa a la atmósfera durante las erupciones y por fumarolas.' },
            { p: 'Aunque el flujo volcánico es pequeño comparado con las emisiones humanas, ha sido fundamental a lo largo de la historia geológica de la Tierra para mantener el CO₂ en la atmósfera.' },
          ],
          sections: [
            { p: 'Los volcanes descargan CO₂ procedente del manto y de la descarbonatación de rocas calcáreas subducidas. Aunque el flujo es pequeño (~3 % del fósil), es la fuente última de carbono para el ciclo rápido.' },
            { h: 'Composición del gas volcánico' },
            { p: 'Los gases volcánicos son ~80 % H₂O, ~10 % CO₂, ~7 % SO₂ y trazas de H₂S, HCl, HF. Las grandes erupciones (traps) pueden inyectar varios GtC en décadas, como ocurrió en la extinción del Pérmico-Triásico.' },
          ]
        }
      },
      {
        id: 'extraccion', label: 'Extracción y combustión', type: 'anthropogenic', kind: 'flow', x: 22, y: 19,
        content: {
          tag: 'Flujo antropogénico', stock: '~10,2 GtC/año (2022)',
          simple: [
            { p: 'La quema de carbón, petróleo y gas natural es el principal motor del cambio climático actual. Al quemar estos combustibles, liberamos a la atmósfera el carbono almacenado durante millones de años.' },
            { p: 'Este proceso ocurre a un ritmo ~100 veces mayor que el flujo volcánico natural, mucho más rápido de lo que los sistemas naturales pueden absorber.' },
          ],
          sections: [
            { p: 'La quema de combustibles fósiles emite ~10,2 GtC/año en 2022: carbón ~40 %, petróleo ~34 %, gas ~20 %, cemento ~4 %, antorchas ~1 %.' },
            { h: 'Combustión del metano' },
            { eq: '\\text{CH}_4 + 2\\,\\text{O}_2 \\rightarrow \\text{CO}_2 + 2\\,\\text{H}_2\\text{O}', display: true },
            { h: 'Producción de cemento' },
            { eq: '\\text{CaCO}_3 \\xrightarrow{900°\\text{C}} \\text{CaO} + \\text{CO}_2', display: true },
          ]
        }
      },
      {
        id: 'disolucion', label: 'Disolución', type: 'marine', kind: 'flow', x: 82, y: 17,
        content: {
          tag: 'Flujo océano–atmósfera', stock: '~2,5 GtC/año (absorción neta)',
          simple: [
            { p: 'El CO₂ de la atmósfera se disuelve en la superficie del océano, especialmente en aguas frías. El océano absorbe alrededor de una cuarta parte del CO₂ emitido por los humanos.' },
            { p: 'Sin embargo, esta absorción está causando la acidificación del mar, afectando a corales y organismos con conchas de carbonato.' },
          ],
          sections: [
            { p: 'El flujo neto actual es de absorción (~2,5 GtC/año), ya que la pCO₂ atmosférica supera a la oceánica.' },
            { h: 'Ley de Henry y bomba de solubilidad' },
            { eq: 'F_{\\text{gas-mar}} = k_w \\cdot (p\\text{CO}_{2,atm} - p\\text{CO}_{2,mar})', display: true },
            { h: 'Factor de Revelle' },
            { eq: 'R = \\frac{\\Delta p\\text{CO}_2 / p\\text{CO}_2}{\\Delta \\text{DIC} / \\text{DIC}} \\approx 10{-}15', display: true },
          ]
        }
      },
      {
        id: 'fotosintesis_m', label: 'Fotosíntesis marina', type: 'marine', kind: 'flow', x: 64, y: 52,
        content: {
          tag: 'Flujo biótico marino', stock: '~50 GtC/año',
          simple: [
            { p: 'El fitoplancton marino capta el CO₂ disuelto en el agua y lo transforma en materia orgánica usando la luz solar. Produce aproximadamente la mitad del oxígeno de la atmósfera.' },
            { p: 'Su actividad depende de la disponibilidad de luz y nutrientes como el nitrógeno, el fósforo y el hierro.' },
          ],
          sections: [
            { p: 'El fitoplancton marino realiza casi la mitad de la fotosíntesis global a pesar de representar < 1 % de la biomasa fotosintética terrestre.' },
            { h: 'Ratio de Redfield' },
            { eq: '(\\text{CH}_2\\text{O})_{106}(\\text{NH}_3)_{16}(\\text{H}_3\\text{PO}_4) \\quad \\text{[C:N:P = 106:16:1]}', display: true },
          ]
        }
      },
      {
        id: 'resp_m', label: 'Respiración celular marina', type: 'marine', kind: 'flow', x: 88, y: 52,
        content: {
          tag: 'Flujo biótico marino', stock: '~49,5 GtC/año',
          simple: [
            { p: 'Los seres vivos marinos respiran al igual que los terrestres: consumen oxígeno y liberan CO₂ al agua. Las bacterias marinas son especialmente importantes, pues descomponen la materia orgánica muerta.' },
            { p: 'Casi toda la materia orgánica producida por el fitoplancton es consumida y respirada antes de llegar al fondo del mar.' },
          ],
          sections: [
            { p: 'Casi toda la producción primaria marina (~98 %) es remineralizada en la zona superficial y mesopelágica (200–1 000 m). Esta respiración devuelve CO₂ al agua.' },
            { h: 'Bucle microbiano' },
            { eq: '\\text{CH}_2\\text{O} + \\text{O}_2 \\rightarrow \\text{CO}_2 + \\text{H}_2\\text{O}', display: true },
          ]
        }
      },
      {
        id: 'acumul', label: 'Acumulación de restos', type: 'marine', kind: 'flow', x: 82, y: 62,
        content: {
          tag: 'Flujo sedimentario marino', stock: '~0,1 GtC/año preservado',
          simple: [
            { p: 'Cuando los organismos marinos mueren, sus restos se hunden hacia las profundidades. La mayor parte es descompuesta antes de llegar al fondo, pero una pequeña fracción se acumula en los sedimentos.' },
            { p: 'Este carbono queda retirado del ciclo activo durante millones de años y es el punto de partida para la formación del petróleo y el gas natural.' },
          ],
          sections: [
            { p: 'De los ~50 GtC/año fijados, solo ~5 GtC/año se exportan por debajo de 100 m, y apenas ~0,1 GtC/año se preservan en el sedimento de forma permanente.' },
            { eq: '\\text{C}_{\\text{org}} \\rightarrow \\text{CO}_2 + \\text{H}_2\\text{O} \\quad \\text{(> 99\\,\\% remineralizado antes del fondo)}', display: true },
          ]
        }
      },
      {
        id: 'metamorf', label: 'Metamorfismo', type: 'geological', kind: 'flow', x: 44, y: 52,
        content: {
          tag: 'Flujo geológico', stock: '~0,3 GtC/año',
          simple: [
            { p: 'Cuando las rocas carbonatadas son enterradas profundamente y sometidas a altas temperaturas y presiones, se transforman y liberan CO₂.' },
            { p: 'Este gas asciende a través de la corteza y puede escapar a la atmósfera por volcanes y fumarolas. El metamorfismo opera en escalas de millones de años.' },
          ],
          sections: [
            { p: 'Las reacciones de descarbonatación liberan CO₂ que escapa por fumarolas y volcanes.' },
            { h: 'Reacción de descarbonatación principal' },
            { eq: '\\text{CaCO}_3 + \\text{SiO}_2 \\xrightarrow{T,P} \\text{CaSiO}_3 + \\text{CO}_2\\uparrow', display: true },
          ]
        }
      },
      {
        id: 'litogenesis', label: 'Litogénesis', type: 'geological', kind: 'flow', x: 65, y: 73,
        content: {
          tag: 'Flujo sedimentario', stock: '~0,2 GtC/año',
          simple: [
            { p: 'La litogénesis es el proceso por el que los sedimentos del fondo marino se compactan y consolidan formando rocas a lo largo de millones de años.' },
            { p: 'Si contienen conchas y esqueletos, forman rocas calizas; si contienen materia orgánica, pueden dar lugar a roca madre del petróleo.' },
          ],
          sections: [
            { h: 'Precipitación biogénica de CaCO₃' },
            { eq: '\\text{Ca}^{2+} + 2\\,\\text{HCO}_3^- \\rightarrow \\text{CaCO}_3 \\downarrow + \\text{CO}_2 + \\text{H}_2\\text{O}', display: true },
          ]
        }
      },
      {
        id: 'subduccion', label: 'Subducción', type: 'geological', kind: 'flow', x: 28, y: 73,
        content: {
          tag: 'Flujo geotectónico', stock: '~0,05 GtC/año al manto',
          simple: [
            { p: 'La subducción ocurre cuando una placa tectónica oceánica se hunde bajo otra placa, arrastrando consigo los sedimentos y el carbono almacenado en ellos.' },
            { p: 'Una parte del carbono subducido vuelve a la superficie a través de volcanes, cerrando el ciclo geológico del carbono.' },
          ],
          sections: [
            { p: 'De cada 100 unidades de carbono que entran en una zona de subducción, ~30 se desgasifican en el arco volcánico y ~70 penetran al manto.' },
            { eq: '\\text{MgCO}_3 + \\text{SiO}_2 \\xrightarrow{\\text{manto}} \\text{MgSiO}_3 + \\text{CO}_2', display: true },
          ]
        }
      },
    ],
  },

  // ── NITRÓGENO ─────────────────────────────────────────────────────────────
  nitrogen: {
    id: 'nitrogen', title: 'Ciclo del Nitrógeno', symbol: 'N',
    image: './Nitrogeno.png', imgW: 1688, imgH: 1125,
    accent: '#34d399',
    typeColors: {
      atmospheric: '#a78bfa', biotic: '#34d399', microbial: '#fbbf24',
      edaphic: '#38bdf8', anthropogenic: '#f87171',
    },
    typeLabels: {
      atmospheric: 'Reservorio atmosférico', biotic: 'Biosfera',
      microbial: 'Microorganismos del suelo', edaphic: 'Compuestos edáficos',
      anthropogenic: 'Antropogénico',
    },
    elements: [
      // ── RESERVORIOS ────────────────────────────────────────────────────────
      {
        id: 'n2_atm', label: 'N₂ atmosférico', type: 'atmospheric', kind: 'reservoir', x: 70, y: 8,
        content: {
          tag: 'Reservorio atmosférico', stock: '~3 900 000 GtN · 78 % del volumen',
          simple: [
            { p: 'El nitrógeno molecular (N₂) es el gas más abundante de la atmósfera terrestre, constituyendo el 78 % del volumen del aire. Sin embargo, su triple enlace lo hace prácticamente inerte: la gran mayoría de los seres vivos no puede utilizarlo directamente.' },
            { p: 'Solo ciertos microorganismos —las bacterias fijadoras de nitrógeno— pueden romper ese enlace y transformar el N₂ en formas aprovechables como el amonio. Este proceso es indispensable para que el nitrógeno entre en la biosfera.' },
          ],
          sections: [
            { p: 'El N₂ atmosférico representa el mayor reservorio de nitrógeno del planeta. Su triple enlace (N≡N) tiene una energía de disociación de 945 kJ/mol, lo que explica su extrema estabilidad química y la necesidad de catálisis biológica o condiciones extremas para fijarlo.' },
            { h: 'Fijación biológica' },
            { eq: '\\text{N}_2 + 8\\,\\text{H}^+ + 8\\,e^- + 16\\,\\text{ATP} \\rightarrow 2\\,\\text{NH}_3 + \\text{H}_2 + 16\\,\\text{ADP}', display: true },
            { p: 'La fijación biológica (BNF) aporta ~120 TgN/año al ciclo terrestre, frente a los ~5 TgN/año de la fijación abiótica por rayos. La enzima nitrogenasa requiere condiciones anóxicas y gran aporte energético.' },
            { h: 'Desnitrificación como retorno' },
            { p: 'El N₂ regresa a la atmósfera principalmente a través de la desnitrificación bacteriana (~120 TgN/año), cerrando el ciclo y evitando la acumulación indefinida de nitratos en los suelos.' },
          ]
        }
      },
      {
        id: 'productores_n', label: 'Productores', type: 'biotic', kind: 'reservoir', x: 40, y: 44,
        content: {
          tag: 'Reservorio biótico vegetal', stock: '~500 TgN en biomasa vegetal',
          simple: [
            { p: 'Las plantas y otros organismos fotosintéticos absorben nitrógeno del suelo principalmente en forma de nitrato (NO₃⁻) y amonio (NH₄⁺). Con él fabrican proteínas, ácidos nucleicos y clorofila, incorporando el nitrógeno a la materia orgánica viva.' },
            { p: 'Sin nitrógeno asimilable, las plantas no pueden crecer: es el nutriente que más frecuentemente limita la productividad de los ecosistemas terrestres. Por eso los fertilizantes nitrogenados son tan utilizados en agricultura.' },
          ],
          sections: [
            { p: 'Las plantas vasculares asimilan predominantemente NO₃⁻ en suelos bien aireados y NH₄⁺ en suelos ácidos o encharcados. La reducción asimilatoria del nitrato require dos enzimas secuenciales:' },
            { h: 'Reducción asimilatoria del nitrato' },
            { eq: '\\text{NO}_3^- \\xrightarrow{\\text{NR}} \\text{NO}_2^- \\xrightarrow{\\text{NiR}} \\text{NH}_4^+', display: true },
            { p: 'El amonio resultante se incorpora a aminoácidos via el ciclo GS-GOGAT (glutamina sintetasa / glutamato sintasa), consumiendo ATP y NADH. El nitrógeno incorporado se distribuye a proteínas, clorofilas, ADN y ARN.' },
            { h: 'Ratio C:N y calidad del tejido' },
            { p: 'El ratio C:N de los tejidos vegetales (~25:1 en hojas, ~100:1 en madera) determina su velocidad de descomposición. Los tejidos ricos en N se descomponen más rápido, devolviendo nitrógeno al suelo con mayor facilidad.' },
          ]
        }
      },
      {
        id: 'consumidores_n', label: 'Consumidores', type: 'biotic', kind: 'reservoir', x: 66, y: 38,
        content: {
          tag: 'Reservorio biótico animal', stock: '~1 TgN en biomasa animal',
          simple: [
            { p: 'Los animales obtienen el nitrógeno que necesitan comiendo plantas u otros animales. Una vez dentro del organismo, el nitrógeno pasa de las proteínas de los alimentos a las proteínas propias del animal, sus enzimas y su material genético.' },
            { p: 'El exceso de nitrógeno que no puede almacenarse se excreta como urea (en mamíferos), ácido úrico (en aves y reptiles) o amonio (en peces), liberándolo de vuelta al entorno.' },
          ],
          sections: [
            { p: 'Los animales obtienen nitrógeno orgánico mediante la digestión de proteínas alimentarias. El catabolismo de aminoácidos libera grupos amino que se eliminan como urea en el ciclo de la urea:' },
            { h: 'Ciclo de la urea (mamíferos)' },
            { eq: '\\text{NH}_3 + \\text{CO}_2 + 3\\,\\text{ATP} \\rightarrow \\text{(CH}_2\\text{N)}_2\\text{CO} + 2\\,\\text{ADP} + \\text{AMP}', display: true },
            { p: 'La eficiencia de conversión de N alimentario a N corporal es baja (~20–40 %), por lo que los consumidores devuelven grandes cantidades de N al ecosistema via excreción y muerte, siendo cruciales para la redistribución del nitrógeno en el paisaje.' },
          ]
        }
      },
      {
        id: 'descomponedores_n', label: 'Descomponedores', type: 'biotic', kind: 'reservoir', x: 50, y: 60,
        content: {
          tag: 'Reservorio biótico descomponedor', stock: '~150 TgN en microbiota edáfica',
          simple: [
            { p: 'Hongos y bacterias descomponen la materia orgánica muerta —hojas, cadáveres, excrementos— rompiendo las moléculas complejas y liberando el nitrógeno que contienen en forma de amonio (NH₄⁺). Este proceso se llama amonificación.' },
            { p: 'Sin los descomponedores, el nitrógeno quedaría atrapado indefinidamente en la materia muerta y los suelos se agotarían rápidamente. Son el eslabón que recicla el nitrógeno de regreso al reservorio edáfico.' },
          ],
          sections: [
            { p: 'Los descomponedores del suelo (bacterias y hongos saprofitos) mineralizan el nitrógeno orgánico de proteínas, aminoácidos y ácidos nucleicos mediante hidrólisis enzimática y desaminación oxidativa:' },
            { h: 'Amonificación' },
            { eq: '\\text{R-NH}_2 + \\text{H}_2\\text{O} \\rightarrow \\text{R-OH} + \\text{NH}_3 \\rightarrow \\text{NH}_4^+', display: true },
            { p: 'La tasa de mineralización depende del ratio C:N del substrato, la temperatura y la humedad del suelo. Los sustratos con C:N > 30 inmovilizan N neto (los microbios compiten con las plantas), mientras que los de C:N < 20 mineralizan N neto.' },
          ]
        }
      },
      {
        id: 'bact_simbioticas', label: 'Bacterias fijadoras simbióticas', type: 'microbial', kind: 'reservoir', x: 18, y: 50,
        content: {
          tag: 'Microorganismos fijadores simbióticos', stock: '~100 TgN/año fijados',
          simple: [
            { p: 'Algunas bacterias del género Rhizobium viven en simbiosis dentro de los nódulos de las raíces de leguminosas (guisantes, lentejas, soja, alfalfa). A cambio de azúcares que la planta les proporciona, estas bacterias convierten el N₂ del aire en amonio, que la planta puede usar directamente.' },
            { p: 'Esta asociación es tan eficiente que las leguminosas rara vez necesitan fertilizantes nitrogenados. Por eso se cultivan tradicionalmente en rotación con otros cultivos: enriquecen el suelo con nitrógeno de forma natural.' },
          ],
          sections: [
            { p: 'La simbiosis Rhizobium–leguminosa es la vía de fijación biológica más productiva del planeta (~70 TgN/año). La planta suministra fotosintatos a la bacteria, y esta fija N₂ con la enzima nitrogenasa en condiciones microanaeróbicas mantenidas por la leghemoglobina (proteína que regula el O₂).' },
            { h: 'Reacción de la nitrogenasa' },
            { eq: '\\text{N}_2 + 16\\,\\text{ATP} + 8\\,e^- + 8\\,\\text{H}^+ \\xrightarrow{\\text{nitrogenasa}} 2\\,\\text{NH}_3 + \\text{H}_2 + 16\\,\\text{ADP} + 16\\,\\text{P}_i', display: true },
            { p: 'Otras asociaciones simbióticas importantes: Frankia con alisos, cianobacterias con hepáticas y helechos acuáticos (Azolla), y cianobacterias endosimbiontes de esponjas marinas.' },
          ]
        }
      },
      {
        id: 'bact_suelo', label: 'Bacterias fijadoras del suelo', type: 'microbial', kind: 'reservoir', x: 18, y: 70,
        content: {
          tag: 'Microorganismos fijadores libres', stock: '~20 TgN/año fijados',
          simple: [
            { p: 'Algunas bacterias (Azotobacter, Clostridium, cianobacterias) viven libremente en el suelo y en los océanos y también son capaces de fijar el N₂ del aire, aunque de forma menos eficiente que las simbióticas.' },
            { p: 'Estas bacterias son especialmente importantes en ecosistemas sin leguminosas, como las turberas, los desiertos o los océanos, donde constituyen la única fuente de entrada de nitrógeno nuevo al sistema.' },
          ],
          sections: [
            { p: 'Los fijadores libres incluyen bacterias aerobias (Azotobacter, ~15–25 kgN/ha/año), bacterias anaerobias (Clostridium), y cianobacterias (Nostoc, Anabaena) en suelos y océanos.' },
            { p: 'La nitrogenasa libre es altamente sensible al O₂ y se inactiva irreversiblemente en presencia de oxígeno. Azotobacter protege la enzima mediante una respiración muy intensa que mantiene el O₂ intracelular bajo (protección conformacional).' },
            { h: 'Coste energético de la fijación libre' },
            { p: 'Fijar 1 kg de N₂ requiere ~15–20 kg de glucosa (materia orgánica del suelo). Por eso los fijadores libres aportan menos N que los simbióticos, pero son ecológicamente esenciales en ecosistemas sin plantas noduladas.' },
          ]
        }
      },
      {
        id: 'nh4', label: 'NH₄⁺', type: 'edaphic', kind: 'reservoir', x: 42, y: 78,
        content: {
          tag: 'Amonio edáfico', stock: '~50 TgN en suelos',
          simple: [
            { p: 'El amonio (NH₄⁺) es el primer compuesto nitrogenado que producen tanto la descomposición de la materia orgánica como la fijación del N₂. Las plantas pueden absorberlo directamente, y algunas lo prefieren al nitrato en suelos ácidos.' },
            { p: 'En el suelo, el amonio se adhiere a las partículas de arcilla cargadas negativamente, por lo que no se lava fácilmente con la lluvia. Es la forma de nitrógeno más estable a corto plazo en el suelo.' },
          ],
          sections: [
            { p: 'El NH₄⁺ es la forma reducida del nitrógeno inorgánico en el suelo. Su equilibrio con el NH₃ gaseoso depende del pH:' },
            { eq: '\\text{NH}_4^+ \\rightleftharpoons \\text{NH}_3(g) + \\text{H}^+, \\quad pK_a = 9{,}25', display: true },
            { p: 'A pH < 7 predomina el NH₄⁺ (retenido por las arcillas); a pH > 8 aumenta el NH₃ volátil, fuente de pérdidas de N. El NH₄⁺ es también el substrato de las bacterias nitrificantes (Nitrosomonas), que lo convierten en NO₂⁻.' },
          ]
        }
      },
      {
        id: 'no3', label: 'NO₃⁻', type: 'edaphic', kind: 'reservoir', x: 60, y: 78,
        content: {
          tag: 'Nitrato edáfico', stock: '~10 TgN en suelos',
          simple: [
            { p: 'El nitrato (NO₃⁻) es la forma de nitrógeno que absorben la mayoría de las plantas en suelos bien aireados. Se produce a partir del amonio por la acción de bacterias nitrificantes.' },
            { p: 'Al ser un anión, el nitrato no se adhiere a las arcillas del suelo y se lava fácilmente con el agua de lluvia hacia los acuíferos y ríos, donde puede causar eutrofización y contaminación del agua potable.' },
          ],
          sections: [
            { p: 'El NO₃⁻ es el producto final de la nitrificación y la forma dominante de N inorgánico en suelos agrícolas bien aireados y con pH neutro. Su alta solubilidad lo hace muy móvil y susceptible a lixiviación.' },
            { h: 'Asimilación de nitrato' },
            { eq: '\\text{NO}_3^- + 10\\,\\text{H}^+ + 8\\,e^- \\rightarrow \\text{NH}_4^+ + 3\\,\\text{H}_2\\text{O}', display: true },
            { p: 'La lixiviación de nitrato hacia aguas subterráneas es el principal problema ambiental asociado a la fertilización nitrogenada excesiva. En la UE, valores > 50 mg/L de NO₃⁻ en agua potable están prohibidos por la Directiva de Nitratos.' },
          ]
        }
      },
      {
        id: 'no2', label: 'NO₂⁻', type: 'edaphic', kind: 'reservoir', x: 78, y: 78,
        content: {
          tag: 'Nitrito edáfico', stock: 'Intermedio transitorio (< 1 TgN)',
          simple: [
            { p: 'El nitrito (NO₂⁻) es un compuesto intermedio en la nitrificación: se produce cuando las bacterias del género Nitrosomonas oxidan el amonio, y es inmediatamente oxidado a nitrato por las bacterias Nitrobacter.' },
            { p: 'El nitrito es tóxico para las plantas y los animales en concentraciones elevadas, por lo que normalmente no se acumula en el suelo. Es también intermediario en la desnitrificación, cuando las bacterias reducen el nitrato a N₂.' },
          ],
          sections: [
            { p: 'El NO₂⁻ actúa como intermediario en dos procesos opuestos: la nitrificación (NH₄⁺ → NO₂⁻ → NO₃⁻) y la desnitrificación (NO₃⁻ → NO₂⁻ → NO → N₂O → N₂). Su tiempo de residencia en el suelo es de horas a días.' },
            { h: 'Nitrificación por etapas' },
            { eq: '\\text{NH}_4^+ + \\frac{3}{2}\\,\\text{O}_2 \\xrightarrow{\\text{Nitrosomonas}} \\text{NO}_2^- + \\text{H}_2\\text{O} + 2\\,\\text{H}^+', display: true },
            { eq: '\\text{NO}_2^- + \\frac{1}{2}\\,\\text{O}_2 \\xrightarrow{\\text{Nitrobacter}} \\text{NO}_3^-', display: true },
            { p: 'En condiciones de hipoxia transitoria (suelos encharcados tras lluvias intensas), el NO₂⁻ puede acumularse y reducirse a N₂O (óxido nitroso), un gas de efecto invernadero ~265 veces más potente que el CO₂ a 100 años.' },
          ]
        }
      },
      // ── FLUJOS ─────────────────────────────────────────────────────────────
      {
        id: 'fijacion_atm', label: 'Fijación atmosférica', type: 'atmospheric', kind: 'flow', x: 8, y: 30,
        content: {
          tag: 'Flujo abiótico', stock: '~5 TgN/año',
          simple: [
            { p: 'Los rayos producen temperaturas de más de 30 000 °C que rompen el triple enlace del N₂ y lo combinan con el oxígeno para formar óxidos de nitrógeno (NOₓ). Estos reaccionan con el vapor de agua atmosférico y caen disueltos en la lluvia como ácido nítrico.' },
            { p: 'Aunque el aporte de la fijación por rayos es pequeño comparado con la fijación biológica, fue durante miles de millones de años la única fuente de nitrógeno reactivo en la Tierra primitiva antes de la evolución de las bacterias fijadoras.' },
          ],
          sections: [
            { p: 'La descarga eléctrica de un rayo aporta energía suficiente para superar la barrera cinética de disociación del N₂. En la atmósfera se producen ~40 millones de rayos/día.' },
            { h: 'Reacciones en la atmósfera' },
            { eq: '\\text{N}_2 + \\text{O}_2 \\xrightarrow{\\text{rayo}} 2\\,\\text{NO}', display: true },
            { eq: '2\\,\\text{NO} + \\text{O}_2 \\rightarrow 2\\,\\text{NO}_2 \\quad \\xrightarrow{\\text{H}_2\\text{O}} \\quad \\text{HNO}_3', display: true },
            { p: 'El ácido nítrico formado se deposita en la superficie con las precipitaciones (deposición húmeda) o como aerosoles de nitrato (deposición seca), aportando ~5 TgN/año a los ecosistemas terrestres y marinos.' },
          ]
        }
      },
      {
        id: 'absorcion_n', label: 'Absorción', type: 'biotic', kind: 'flow', x: 44, y: 28,
        content: {
          tag: 'Flujo de asimilación vegetal', stock: '~1 000 TgN/año (flujo bruto)',
          simple: [
            { p: 'Las raíces de las plantas absorben nitrógeno del suelo principalmente en forma de nitrato o amonio. Para ello utilizan proteínas transportadoras especializadas que requieren energía, siendo uno de los procesos que más ATP consume en la planta.' },
            { p: 'Las micorrizas —hongos que colonizan las raíces— amplifican enormemente la superficie de absorción y permiten a las plantas acceder a nutrientes en zonas del suelo que las raíces no alcanzarían.' },
          ],
          sections: [
            { p: 'La absorción de nitrato es activa y mediada por transportadores de alta afinidad (NRT2) en condiciones de escasez y de baja afinidad (NRT1) cuando el NO₃⁻ es abundante. La energía proviene del gradiente de protones generado por la ATPasa de membrana.' },
            { h: 'Síntesis de aminoácidos via GS-GOGAT' },
            { eq: '\\text{NH}_4^+ + \\text{Glu} + \\text{ATP} \\xrightarrow{\\text{GS}} \\text{Gln} + \\text{ADP}', display: true },
            { eq: '\\text{Gln} + \\alpha\\text{-CG} + \\text{NADH} \\xrightarrow{\\text{GOGAT}} 2\\,\\text{Glu}', display: true },
            { p: 'La glutamina es el aminoácido dador de N para la síntesis de todos los demás aminoácidos y nucleótidos. Las micorrizas arbusculares pueden aportar hasta el 80 % del N absorbido en plantas de praderas.' },
          ]
        }
      },
      {
        id: 'desnitrificacion', label: 'Desnitrificación', type: 'microbial', kind: 'flow', x: 84, y: 20,
        content: {
          tag: 'Flujo microbiano al N₂', stock: '~120 TgN/año',
          simple: [
            { p: 'La desnitrificación es el proceso por el que ciertas bacterias anaerobias transforman el nitrato del suelo en nitrógeno molecular (N₂), que escapa a la atmósfera. Cierra el ciclo devolviéndole al aire el nitrógeno que los seres vivos habían acumulado.' },
            { p: 'Ocurre en condiciones de bajo oxígeno: suelos encharcados, sedimentos anóxicos y zonas de mínimo de oxígeno en el océano. Es el principal mecanismo por el que el nitrógeno vuelve a la atmósfera.' },
          ],
          sections: [
            { p: 'Las bacterias desnitrificantes (Pseudomonas, Paracoccus, Thiobacillus) utilizan el NO₃⁻ como aceptor alternativo de electrones en la respiración anaerobia.' },
            { h: 'Cadena de reducción' },
            { eq: '\\text{NO}_3^- \\rightarrow \\text{NO}_2^- \\rightarrow \\text{NO} \\rightarrow \\text{N}_2\\text{O} \\rightarrow \\text{N}_2', display: true },
            { p: 'El N₂O es un subproducto parcial de la desnitrificación incompleta. A escala global, ~7 TgN/año se emiten como N₂O, contribuyendo al calentamiento climático y a la destrucción del ozono estratosférico.' },
            { h: 'Reacción global' },
            { eq: '5\\,\\text{CH}_2\\text{O} + 4\\,\\text{NO}_3^- \\rightarrow 2\\,\\text{N}_2 + 4\\,\\text{HCO}_3^- + \\text{CO}_2 + 3\\,\\text{H}_2\\text{O}', display: true },
          ]
        }
      },
      {
        id: 'amonificacion', label: 'Amonificación', type: 'microbial', kind: 'flow', x: 36, y: 68,
        content: {
          tag: 'Flujo de mineralización', stock: '~1 000 TgN/año',
          simple: [
            { p: 'La amonificación es el proceso por el que los microorganismos del suelo descomponen las proteínas y otros compuestos nitrogenados de la materia orgánica muerta, liberando el nitrógeno en forma de amonio (NH₄⁺).' },
            { p: 'Es el primer paso en la reciclaje del nitrógeno orgánico: sin amonificación, el nitrógeno quedaría bloqueado en la materia muerta y los suelos se empobrencerían rápidamente en este nutriente esencial.' },
          ],
          sections: [
            { p: 'La amonificación comprende la hidrólisis enzimática de proteínas (proteasas), ácidos nucleicos (nucleasas) y compuestos de quitina, seguida de la desaminación de los aminoácidos liberados.' },
            { h: 'Desaminación oxidativa de glutamato' },
            { eq: '\\text{Glu} + \\text{NAD}^+ + \\text{H}_2\\text{O} \\xrightarrow{\\text{GDH}} \\alpha\\text{-cetoglutarato} + \\text{NH}_4^+ + \\text{NADH}', display: true },
            { p: 'La velocidad de amonificación está controlada por la temperatura (Q₁₀ ≈ 2), la humedad y la calidad del sustrato (ratio C:N). En suelos tropicales cálidos y húmedos, la mineralización puede superar la absorción vegetal, causando pérdidas de N por lixiviación.' },
          ]
        }
      },
      {
        id: 'nitrificacion', label: 'Nitrificación', type: 'microbial', kind: 'flow', x: 62, y: 82,
        content: {
          tag: 'Flujo microbiano aerobio', stock: '~130 TgN/año',
          simple: [
            { p: 'La nitrificación es el proceso por el que bacterias especializadas oxidan el amonio (NH₄⁺) primero a nitrito (NO₂⁻) y luego a nitrato (NO₃⁻). Estas bacterias son quimiolitoautótrofas: obtienen su energía de la oxidación del nitrógeno y el CO₂ del aire como fuente de carbono.' },
            { p: 'El nitrato producido es la forma que mejor absorben la mayoría de las plantas, pero también la más fácil de perder por lavado con el agua de lluvia. La nitrificación conecta el amonio generado por los descomponedores con el nitrato que usan los productores.' },
          ],
          sections: [
            { p: 'La nitrificación es llevada a cabo por dos grupos funcionales distintos de bacterias quimioautótrofas:' },
            { h: 'Nitrosomonas: amonio → nitrito' },
            { eq: '\\text{NH}_4^+ + \\frac{3}{2}\\,\\text{O}_2 \\rightarrow \\text{NO}_2^- + \\text{H}_2\\text{O} + 2\\,\\text{H}^+ \\quad \\Delta G = -275\\,\\text{kJ/mol}', display: true },
            { h: 'Nitrobacter: nitrito → nitrato' },
            { eq: '\\text{NO}_2^- + \\frac{1}{2}\\,\\text{O}_2 \\rightarrow \\text{NO}_3^- \\quad \\Delta G = -76\\,\\text{kJ/mol}', display: true },
            { p: 'Recientemente se han descubierto bacterias que realizan la nitrificación completa (comammox, Nitrospira), pasando de NH₄⁺ a NO₃⁻ en un solo organismo. La nitrificación es estrictamente aerobia y se inhibe por pH bajo (< 5,5) y amonio en exceso.' },
          ]
        }
      },
    ],
  },

  // ── FÓSFORO ───────────────────────────────────────────────────────────────
  phosphorus: {
    id: 'phosphorus', title: 'Ciclo del Fósforo', symbol: 'P',
    image: './Fosforo.png', imgW: 1688, imgH: 1125,
    accent: '#fbbf24',
    typeColors: {
      biotic: '#34d399', hydrospheric: '#38bdf8',
      lithospheric: '#fbbf24', anthropogenic: '#f87171',
    },
    typeLabels: {
      biotic: 'Biosfera', hydrospheric: 'Hidrosfera',
      lithospheric: 'Litosfera / Geología', anthropogenic: 'Antropogénico',
    },
    elements: [
      // ── RESERVORIOS ────────────────────────────────────────────────────────
      {
        id: 'guano', label: 'Guano', type: 'biotic', kind: 'reservoir', x: 12, y: 28,
        content: {
          tag: 'Reservorio biótico secundario', stock: 'Históricamente: ~12 Mt P explotados',
          simple: [
            { p: 'El guano es la acumulación de excrementos de aves marinas y murciélagos, muy rico en fosfatos y nitratos. Durante el siglo XIX fue explotado masivamente como fertilizante natural, desencadenando la llamada "fiebre del guano" en países como Perú y Chile.' },
            { p: 'El guano se forma porque las aves marinas concentran el fósforo del pescado que comen y lo excretan en las costas. Es un ejemplo de cómo el ciclo del fósforo cruza la barrera entre el océano y la tierra a través de la vida.' },
          ],
          sections: [
            { p: 'El guano de aves ictiófagas (cormoranes, piqueros, pelícanos) puede contener hasta 12 % de P₂O₅ en peso seco, junto con abundante N orgánico. Fue el principal fertilizante mundial antes de la síntesis de Haber-Bosch y la explotación de roca fosfórica.' },
            { h: 'Composición típica del guano' },
            { p: 'Guano fresco: ~16 % N, ~9 % P₂O₅, ~3 % K₂O. Guano fosilizado (más rico en P): hasta 35 % P₂O₅. La diferencia radica en la volatilización del N amoniacal con el tiempo.' },
            { p: 'Las Islas Chincha (Perú) acumularon depósitos de hasta 50 m de espesor durante siglos de nidificación. La explotación entre 1840 y 1880 agotó la mayoría de las reservas accesibles, generando ingresos equivalentes al 80 % del presupuesto peruano de la época.' },
          ]
        }
      },
      {
        id: 'productores_p', label: 'Productores', type: 'biotic', kind: 'reservoir', x: 37, y: 30,
        content: {
          tag: 'Reservorio biótico vegetal', stock: '~500 TgP en biomasa vegetal',
          simple: [
            { p: 'Las plantas absorben fósforo del suelo en forma de fosfato (H₂PO₄⁻ o HPO₄²⁻). Lo utilizan para construir moléculas fundamentales: el ADN y el ARN que contienen la información genética, el ATP que transporta energía, y los fosfolípidos de las membranas celulares.' },
            { p: 'A diferencia del nitrógeno, el fósforo no tiene forma gaseosa en condiciones normales, por lo que el ciclo del fósforo es completamente sedimentario: el fósforo solo puede moverse disuelto en agua o incorporado a la materia viva.' },
          ],
          sections: [
            { p: 'El fósforo es esencial para la vida porque es el componente central del ATP (moneda energética universal), el esqueleto de los ácidos nucleicos, y los cabezales polares de fosfolípidos de membrana.' },
            { h: 'Absorción de fosfato y rol de las micorrizas' },
            { p: 'El fosfato es poco móvil en el suelo porque se adsorbe fuertemente a óxidos de Fe y Al (suelos ácidos) o precipita como Ca₃(PO₄)₂ (suelos alcalinos). Las hifas de hongos micorrizicos arbusculares (AMF) extienden la zona de absorción vegetal hasta 8 cm más allá de la raíz, captando el P difusivo.' },
            { h: 'Ciclo biológico rápido' },
            { p: 'El tiempo de residencia del P en la biomasa vegetal es corto (~1–10 años). La descomposición libera fosfato inorgánico al suelo, donde puede ser reabsorbido por las plantas (inmobilización-mineralización) con tiempos de reciclaje de días a semanas.' },
          ]
        }
      },
      {
        id: 'cadena_trofica', label: 'Resto de la cadena trófica', type: 'biotic', kind: 'reservoir', x: 65, y: 25,
        content: {
          tag: 'Reservorio biótico animal', stock: '~2 TgP en biomasa animal',
          simple: [
            { p: 'Los animales obtienen el fósforo que necesitan al consumir plantas u otros animales. Gran parte del fósforo corporal se concentra en los huesos y los dientes, donde forma el mineral hidroxiapatita, que da dureza y resistencia al esqueleto.' },
            { p: 'El fósforo sobrante se excreta en la orina como fosfato inorgánico y en las heces como fósforo orgánico. Esta excreción redistribuye el fósforo por el ecosistema, fertilizando suelos y cuerpos de agua.' },
          ],
          sections: [
            { p: 'En los huesos y dientes el P se encuentra como hidroxiapatita: Ca₁₀(PO₄)₆(OH)₂. Un vertebrado típico almacena el 85–90 % de su P corporal en el esqueleto.' },
            { h: 'Composición del hueso' },
            { eq: '\\text{Ca}_{10}(\\text{PO}_4)_6(\\text{OH})_2 \\quad \\text{(hidroxiapatita)}', display: true },
            { p: 'Los grandes herbívoros son importantes vectores de P del ecosistema: al pastar en zonas ricas y defecar en otras, redistribuyen el fósforo paisajisticamente. Los hipopótamos transfieren unas 1 000 TgP/año del pasto terrestre al agua dulce en los ríos africanos donde nadan.' },
          ]
        }
      },
      {
        id: 'hidrosfera_p', label: 'Hidrosfera', type: 'hydrospheric', kind: 'reservoir', x: 36, y: 57,
        content: {
          tag: 'Reservorio acuático', stock: '~90 000 TgP disuelto y particulado',
          simple: [
            { p: 'El fosfato disuelto en ríos, lagos y océanos es el principal nutriente que limita la productividad primaria en la mayoría de los ecosistemas acuáticos. Una pequeña cantidad de fosfato puede desencadenar floraciones masivas de algas.' },
            { p: 'Cuando el fósforo llega en exceso a los cuerpos de agua —por ejemplo, desde campos agrícolas o aguas residuales— provoca eutrofización: las algas se multiplican explosivamente, consumen el oxígeno disuelto y matan a los peces y otros organismos.' },
          ],
          sections: [
            { p: 'En la hidrosfera el P existe como fosfato inorgánico disuelto (PO₄³⁻, HPO₄²⁻, H₂PO₄²⁻ según el pH), fósforo orgánico disuelto (DON-P) y P particulado. El P total en el océano es ~88 000 TgP.' },
            { h: 'Especiación del fosfato con el pH' },
            { eq: '\\text{H}_3\\text{PO}_4 \\rightleftharpoons \\text{H}_2\\text{PO}_4^- \\rightleftharpoons \\text{HPO}_4^{2-} \\rightleftharpoons \\text{PO}_4^{3-}', display: true },
            { p: 'A pH 7–8 (oceánico) predomina HPO₄²⁻. La concentración en océano abierto es < 1 μmol/L en la superficie (zona fótica) y aumenta con la profundidad por remineralización. La relación de Redfield (C:N:P = 106:16:1) define la composición del fitoplancton marino.' },
          ]
        }
      },
      {
        id: 'litosfera_p', label: 'Litosfera', type: 'lithospheric', kind: 'reservoir', x: 40, y: 80,
        content: {
          tag: 'Reservorio litológico', stock: '~10⁹ TgP en rocas',
          simple: [
            { p: 'Las rocas fosfáticas —principalmente la apatita— son el mayor reservorio de fósforo del planeta. A diferencia del carbono o el nitrógeno, el fósforo no tiene una fase gaseosa estable, por lo que su ciclo es completamente dependiente de la geología: sin meteorización de rocas, no hay fósforo nuevo para la biosfera.' },
            { p: 'Las reservas conocidas de roca fosfórica explotable son finitas y se estima que podrían agotarse en 50–100 años al ritmo actual de extracción. Esto hace que el "pico del fósforo" sea un problema de sostenibilidad global tan serio como el del petróleo.' },
          ],
          sections: [
            { p: 'La apatita (Ca₅(PO₄)₃X, donde X = F, Cl, OH) es el mineral fosfatado más común, presente en rocas ígneas, metamórficas y sedimentarias. Las reservas mundiales de roca fosfórica se concentran en Marruecos (~70 %), China y Oriente Medio.' },
            { h: 'Fórmula de la fluorapatita' },
            { eq: '\\text{Ca}_5(\\text{PO}_4)_3\\text{F} \\quad \\text{(fluorapatita, mineral más común)}', display: true },
            { p: 'La meteorización química de la apatita por ácidos húmicos y ácido carbónico libera fosfato soluble. El proceso es lento (~1 TgP/año global), insuficiente para compensar las exportaciones agrícolas actuales (~50 MtP/año), lo que hace imprescindible el reciclaje del fósforo en los sistemas productivos.' },
          ]
        }
      },
      {
        id: 'sedimentos_p', label: 'Sedimentos', type: 'lithospheric', kind: 'reservoir', x: 80, y: 62,
        content: {
          tag: 'Reservorio sedimentario', stock: '~840 TgP en sedimentos oceánicos',
          simple: [
            { p: 'Los restos de organismos acuáticos se acumulan en el fondo del mar formando sedimentos ricos en fósforo. Con el tiempo y la presión, estos sedimentos pueden transformarse en nuevas rocas fosfáticas, cerrando el ciclo geológico del fósforo.' },
            { p: 'Los sedimentos también actúan como "trampa" de fósforo: en condiciones de bajo oxígeno, el P puede liberarse de nuevo al agua, fertilizando desde el fondo a los organismos de la superficie.' },
          ],
          sections: [
            { p: 'El fósforo sedimentario existe en tres formas: mineral (vivianita, apatita autigénica), orgánico y adsorbido a óxidos de hierro. En condiciones óxicas, los óxidos de Fe atrapan el P; en condiciones anóxicas, el Fe³⁺ se reduce a Fe²⁺ y el P se libera, fertilizando la columna de agua.' },
            { h: 'Trampa redox del P' },
            { eq: '\\text{Fe(OH)}_3 \\cdot \\text{PO}_4 + e^- \\rightarrow \\text{Fe}^{2+} + \\text{PO}_4^{3-} + 3\\,\\text{OH}^-', display: true },
            { p: 'Esta liberación redox de P desde sedimentos en lagos eutrofizados perpetúa el problema de forma autosustentada, incluso tras la eliminación de la fuente externa de P (carga interna). La formación de apatita autigénica en sedimentos es la principal vía de enterramiento geológico del P.' },
          ]
        }
      },
      {
        id: 'fertilizantes', label: 'Fertilizantes', type: 'anthropogenic', kind: 'reservoir', x: 88, y: 38,
        content: {
          tag: 'Reservorio antropogénico', stock: '~50 MtP/año extraídos globalmente',
          simple: [
            { p: 'Los fertilizantes fosfatados se obtienen tratando la roca fosfórica con ácido sulfúrico para producir superfosfato soluble. Son indispensables para mantener la productividad agrícola moderna: sin ellos, el mundo no podría alimentar a su población actual.' },
            { p: 'El problema es que gran parte del fósforo de los fertilizantes no llega a las plantas: entre el 70 y el 90 % se pierde hacia ríos, lagos y el océano, donde causa eutrofización, o se fija en el suelo en formas no disponibles para las plantas.' },
          ],
          sections: [
            { p: 'La industria de los fertilizantes fosfatados extrae ~50 MtP/año de roca fosfórica. El proceso industrial principal es la producción de superfosfato:' },
            { h: 'Producción de superfosfato' },
            { eq: '\\text{Ca}_3(\\text{PO}_4)_2 + 2\\,\\text{H}_2\\text{SO}_4 \\rightarrow \\text{Ca}(\\text{H}_2\\text{PO}_4)_2 + 2\\,\\text{CaSO}_4', display: true },
            { p: 'Las estimaciones de "peak phosphorus" varían entre 2030 y 2100 según las reservas consideradas. Marruecos controla ~70 % de las reservas mundiales conocidas. El reciclaje de P desde aguas residuales urbanas y estiércol ganadero es esencial para la sostenibilidad a largo plazo.' },
          ]
        }
      },
      // ── FLUJOS ─────────────────────────────────────────────────────────────
      {
        id: 'meteor_guano', label: 'Meteorización', type: 'lithospheric', kind: 'flow', x: 10, y: 52,
        content: {
          tag: 'Flujo geoquímico', stock: '~1 TgP/año',
          simple: [
            { p: 'La meteorización química de las rocas fosfáticas por el agua de lluvia y los ácidos húmicos del suelo libera lentamente el fósforo de los minerales y lo pone en solución, donde puede ser absorbido por plantas o transportado por los ríos.' },
            { p: 'En las costas donde las aves marinas nidifican masivamente, el guano acumulado se disuelve con la lluvia y libera fosfato que llega directamente al mar, fertilizando las aguas costeras y creando algunos de los caladeros de pesca más productivos del mundo.' },
          ],
          sections: [
            { p: 'La meteorización de la apatita es la fuente primaria de P para los ecosistemas terrestres y el océano. El mecanismo principal es la hidrólisis ácida:' },
            { eq: '\\text{Ca}_5(\\text{PO}_4)_3\\text{F} + 4\\,\\text{H}^+ \\rightarrow 5\\,\\text{Ca}^{2+} + 3\\,\\text{HPO}_4^{2-} + \\text{HF}', display: true },
            { p: 'La tasa global de meteorización de P (~1 TgP/año) es muy inferior a la extracción agrícola (~50 MtP/año), lo que confirma que el ciclo natural del fósforo opera en escalas de millones de años, incompatibles con las necesidades agrícolas actuales.' },
          ]
        }
      },
      {
        id: 'meteor_hidro', label: 'Meteorización', type: 'lithospheric', kind: 'flow', x: 28, y: 82,
        content: {
          tag: 'Flujo erosivo continental', stock: '~3 TgP/año al océano',
          simple: [
            { p: 'La erosión de los suelos y rocas por el agua de lluvia y los ríos arrastra partículas de fósforo desde los continentes hasta el océano. Es el principal mecanismo por el que el fósforo llega al mar y alimenta al fitoplancton oceánico.' },
            { p: 'La deforestación y la agricultura intensiva aumentan la erosión del suelo y el flujo de fósforo hacia los ríos y el mar, generando zonas costeras con exceso de nutrientes y proliferación de algas.' },
          ],
          sections: [
            { p: 'Los ríos transportan al océano ~3 TgP/año: ~0,6 TgP/año en forma disuelta y ~2,4 TgP/año como P particulado (mineral + orgánico). La fracción disuelta biodisponible es la que alimenta directamente al fitoplancton costero.' },
            { p: 'La actividad humana ha triplicado la carga de P fluvial al océano en los últimos siglos, por erosión agrícola, fertilizantes y aguas residuales. Esta entrada extra de P causa hipoxia costera (zonas muertas) en más de 400 puntos del mundo.' },
          ]
        }
      },
      {
        id: 'disolucion_p', label: 'Disolución', type: 'hydrospheric', kind: 'flow', x: 48, y: 48,
        content: {
          tag: 'Flujo hidrosfera–biosfera', stock: '~60 TgP/año',
          simple: [
            { p: 'Las plantas y el fitoplancton absorben el fosfato disuelto en el agua del suelo o del mar para usarlo en sus procesos vitales. Este intercambio es el puente entre el reservorio inorgánico del agua y la materia orgánica viva.' },
            { p: 'En los ecosistemas acuáticos, la disponibilidad de fosfato controla cuánto fitoplancton puede crecer. En muchos lagos y zonas costeras, añadir pequeñas cantidades de fosfato dispara floraciones de algas.' },
          ],
          sections: [
            { p: 'En suelos, el P se mueve hacia las raíces principalmente por difusión, a una velocidad muy lenta (~10⁻¹³ m²/s). La zona de agotamiento de P alrededor de una raíz se establece en 1–2 mm, lo que hace que la exploración radical y las micorrizas sean críticas.' },
            { p: 'En el océano, el ciclo del P es muy rápido en la zona fótica: el tiempo de residencia del P disuelto es solo ~weeks en superficie, donde el fitoplancton lo incorpora con la misma velocidad con la que la remineralización bacteriana lo libera.' },
          ]
        }
      },
      {
        id: 'excrecion_p', label: 'Excreción', type: 'biotic', kind: 'flow', x: 58, y: 18,
        content: {
          tag: 'Flujo biótico de retorno', stock: '~50 TgP/año',
          simple: [
            { p: 'Los animales excretan el fósforo sobrante de su dieta a través de la orina (como fosfato inorgánico) y las heces (como fósforo orgánico). Tanto en tierra como en el mar, esta excreción devuelve el fósforo al entorno y lo redistribuye espacialmente.' },
            { p: 'Las aves marinas que pescan en el océano y defecan en tierra son un ejemplo espectacular: transportan físicamente el fósforo marino hasta la costa, fertilizando ecosistemas terrestres con nutrientes oceánicos.' },
          ],
          sections: [
            { p: 'La excreción animal devuelve P en formas de alta disponibilidad. En mamíferos, el P urinario (principalmente H₂PO₄⁻ y HPO₄²⁻) es directamente asimilable por las plantas; el P fecal requiere mineralización microbiana previa.' },
            { p: 'En el océano, la excreción del zooplancton y los peces es uno de los principales mecanismos de regeneración del P en la zona fótica. Los krill antárticos excretan cantidades de P equivalentes al 5–15 % de la producción primaria local.' },
          ]
        }
      },
      {
        id: 'acumulacion_p', label: 'Acumulación', type: 'biotic', kind: 'flow', x: 82, y: 46,
        content: {
          tag: 'Flujo de enterramiento', stock: '~1 TgP/año preservado',
          simple: [
            { p: 'Cuando los organismos mueren, sus restos se acumulan en el fondo de los mares y lagos. La mayor parte del fósforo es reciclada rápidamente por las bacterias, pero una pequeña fracción queda enterrada en los sedimentos, retirándola del ciclo activo durante millones de años.' },
            { p: 'Este enterramiento gradual es la razón por la que el ciclo del fósforo tiene que ser continuamente "recargado" por la meteorización de rocas. Sin un retorno geológico desde el fondo del mar (subducción y volcanismo), la biosfera se quedaría sin fósforo.' },
          ],
          sections: [
            { p: 'La eficiencia de enterramiento del P marino es baja (~0,1–1 % del P sedimentado). La mayor parte se remineraliza en la interfaz agua-sedimento y se devuelve a la columna de agua. El P que se entierra permanentemente se asocia principalmente a la apatita autigénica y a los óxidos de hierro.' },
          ]
        }
      },
      {
        id: 'litogenesis_p', label: 'Litogénesis', type: 'lithospheric', kind: 'flow', x: 62, y: 80,
        content: {
          tag: 'Flujo sedimentario', stock: '~0,5 TgP/año',
          simple: [
            { p: 'La litogénesis es el proceso lento por el que los sedimentos del fondo marino se compactan y transforman en roca sólida, con el paso de millones de años. Los sedimentos ricos en fósforo dan lugar a rocas fosfáticas (fosfatitas) que pueden ser explotadas como fertilizante.' },
            { p: 'Este proceso cierra el ciclo geológico del fósforo: el P que fue absorbido por los organismos hace millones de años, que murió y se hundió en el fondo del mar, queda ahora inmovilizado en roca y solo volverá a ser disponible cuando esa roca sea meterorizada en la superficie.' },
          ],
          sections: [
            { p: 'La formación de apatita sedimentaria (francolita) es el principal mecanismo de enterramiento a largo plazo del P oceánico. Ocurre en sedimentos ricos en materia orgánica de zonas de surgencia costera (upwelling), donde el P se concentra por remineralización bacteriana intensa.' },
          ]
        }
      },
      {
        id: 'explotacion', label: 'Explotación', type: 'anthropogenic', kind: 'flow', x: 87, y: 55,
        content: {
          tag: 'Flujo antropogénico', stock: '~50 MtP/año extraídos (2023)',
          simple: [
            { p: 'La minería de roca fosfórica extrae cada año unas 50 millones de toneladas de fósforo de depósitos formados hace decenas de millones de años. Este fósforo se usa principalmente para fabricar fertilizantes que alimentan la agricultura global.' },
            { p: 'El problema es que las reservas son finitas y no renovables en escala humana: una vez extraído y dispersado en el ambiente, el fósforo es prácticamente irrecuperable. Sin estrategias de recuperación y reciclaje, la humanidad se enfrenta a una crisis de fósforo a largo plazo.' },
          ],
          sections: [
            { p: 'La extracción anual de roca fosfórica (~220 Mt de mineral) equivale a unos 50 MtP/año. La eficiencia global de uso del P es baja: ~20 % del P extraído llega al plato del consumidor; el resto se pierde en diversas etapas de la cadena alimentaria.' },
            { p: 'Las estimaciones de reservas explotables a precios actuales varían de 60 a 300 años. Sin embargo, el "peak phosphorus" (máximo de producción antes del declive) podría ocurrir antes de 2050 según modelos geopolíticos que consideran la concentración geográfica de las reservas.' },
          ]
        }
      },
    ],
  },

  // ── AZUFRE ────────────────────────────────────────────────────────────────
  sulfur: {
    id: 'sulfur', title: 'Ciclo del Azufre', symbol: 'S',
    image: './Azufre.png', imgW: 1688, imgH: 1125,
    accent: '#fb923c',
    typeColors: {
      atmospheric: '#a78bfa', biotic: '#34d399', edaphic: '#38bdf8',
      geological: '#fbbf24', anthropogenic: '#f87171',
    },
    typeLabels: {
      atmospheric: 'Reservorio atmosférico', biotic: 'Azufre orgánico',
      edaphic: 'Suelo / Hidrosfera', geological: 'Geología',
      anthropogenic: 'Antropogénico',
    },
    elements: [
      // ── RESERVORIOS ────────────────────────────────────────────────────────
      {
        id: 's_atm', label: 'Azufre atmosférico', type: 'atmospheric', kind: 'reservoir', x: 70, y: 10,
        content: {
          tag: 'Reservorio atmosférico', stock: '~5 TgS (H₂S, SO₂, H₂SO₄)',
          simple: [
            { p: 'El azufre atmosférico existe principalmente como dióxido de azufre (SO₂), sulfuro de hidrógeno (H₂S) y aerosoles de sulfato (H₂SO₄). Aunque su concentración es baja, tiene un gran impacto en el clima y la química de la atmósfera.' },
            { p: 'El SO₂ emitido por volcanes e industrias se oxida en la atmósfera formando ácido sulfúrico, que con la lluvia precipita como lluvia ácida, dañando bosques, lagos y edificios. Los aerosoles sulfatados también reflejan la luz solar, produciendo un efecto de enfriamiento climático.' },
          ],
          sections: [
            { p: 'El SO₂ atmosférico tiene un tiempo de residencia de solo 1–2 semanas, siendo eliminado por oxidación a H₂SO₄ y deposición húmeda o seca. Los aerosoles de sulfato resultantes tienen un forzamiento radiativo directo de –0,4 W/m² (enfriamiento).' },
            { h: 'Oxidación del SO₂ en la atmósfera' },
            { eq: '\\text{SO}_2 + \\text{OH} \\rightarrow \\text{HOSO}_2 \\xrightarrow{\\text{O}_2} \\text{SO}_3 \\xrightarrow{\\text{H}_2\\text{O}} \\text{H}_2\\text{SO}_4', display: true },
            { p: 'El DMS (dimetilsulfuro, (CH₃)₂S) emitido por el fitoplancton marino es la mayor fuente natural de S atmosférico en el hemisferio sur. Su oxidación a sulfato genera núcleos de condensación de nubes, influyendo en el albedo oceánico (hipótesis CLAW).' },
          ]
        }
      },
      {
        id: 's_organico', label: 'Azufre orgánico', type: 'biotic', kind: 'reservoir', x: 52, y: 44,
        content: {
          tag: 'Reservorio biótico', stock: '~10 GtS en biomasa total',
          simple: [
            { p: 'El azufre forma parte esencial de todas las células vivas. Se incorpora principalmente en dos aminoácidos: la cisteína y la metionina, que son imprescindibles para la estructura y función de las proteínas. Los puentes disulfuro entre cisteínas dan la forma tridimensional a muchas proteínas.' },
            { p: 'Las plantas absorben el azufre del suelo en forma de sulfato (SO₄²⁻). Algunas plantas como el ajo, la cebolla y la mostaza acumulan compuestos azufrados especiales que tienen propiedades medicinales y les protegen de los herbívoros.' },
          ],
          sections: [
            { p: 'El azufre orgánico se encuentra en aminoácidos (cisteína, metionina), cofactores (CoA, biotina, tiamina) y en el glutatión, antioxidante celular universal. La cisteína es esencial para los puentes disulfuro (S–S) que estabilizan la estructura de proteínas.' },
            { h: 'Puente disulfuro' },
            { eq: '2\\,\\text{R-SH} + \\frac{1}{2}\\,\\text{O}_2 \\rightarrow \\text{R-S-S-R} + \\text{H}_2\\text{O}', display: true },
            { p: 'El DMS (dimetilsulfuro), producido por el fitoplancton al degradar DMSP (dimetilsulfoniopropionato), es el compuesto azufrado biogénico más abundante del océano. Es el aroma característico del mar y la principal fuente natural de S atmosférico.' },
          ]
        }
      },
      {
        id: 'suelo_so4', label: 'Suelo (SO₄²⁻)', type: 'edaphic', kind: 'reservoir', x: 84, y: 44,
        content: {
          tag: 'Reservorio edáfico', stock: '~300 GtS en suelos y aguas continentales',
          simple: [
            { p: 'El sulfato (SO₄²⁻) es la forma de azufre más abundante en el suelo y la que utilizan las plantas para su nutrición. Llega al suelo por meteorización de minerales sulfurados, deposición de lluvia ácida y mineralización de materia orgánica.' },
            { p: 'En los suelos ácidos tropicales, el sulfato puede adsorberse a los óxidos de hierro y aluminio, quedando retenido en el suelo en lugar de lixiviarse. En suelos orgánicos como las turberas, grandes cantidades de azufre quedan almacenadas en la materia orgánica.' },
          ],
          sections: [
            { p: 'El sulfato edáfico procede de tres fuentes: meteorización de sulfuros (FeS₂) y sulfatos (yeso, CaSO₄), deposición atmosférica y mineralización del S orgánico. La concentración típica en suelos agrícolas es de 10–30 mg S/kg.' },
            { h: 'Reducción asimilatoria del sulfato' },
            { eq: '\\text{SO}_4^{2-} + \\text{ATP} \\rightarrow \\text{APS} \\rightarrow \\text{SO}_3^{2-} \\rightarrow \\text{S}^{2-} \\rightarrow \\text{Cys}', display: true },
            { p: 'La asimilación de sulfato por plantas requiere su reducción desde S⁶⁺ a S²⁻, consumiendo cuatro pares de electrones (ATP, NADPH, ferredoxina). Este proceso ocurre principalmente en los cloroplastos.' },
          ]
        }
      },
      {
        id: 'sedimentos_s', label: 'Sedimentos', type: 'geological', kind: 'reservoir', x: 86, y: 65,
        content: {
          tag: 'Reservorio sedimentario', stock: '~8 400 GtS en sedimentos',
          simple: [
            { p: 'En los sedimentos marinos sin oxígeno, las bacterias reducen el sulfato del agua de mar a sulfuro de hidrógeno (H₂S). Este H₂S reacciona con el hierro disuelto para formar pirita (FeS₂), un mineral negro que se acumula en los sedimentos y que es el origen de muchos yacimientos minerales.' },
            { p: 'La formación de pirita en los sedimentos es una de las formas más importantes de enterramiento del azufre y del carbono. El azufre "atrapado" en la pirita puede permanecer en la corteza terrestre durante cientos de millones de años.' },
          ],
          sections: [
            { p: 'Los sedimentos marinos son el mayor reservorio de azufre en la superficie terrestre, principalmente como sulfuros (pirita, FeS₂) y sulfatos (yeso, anhidrita). La reducción sulfatogénica bacteriana (SRB) es el proceso clave de enterramiento.' },
            { h: 'Sulfato-reducción bacteriana y formación de pirita' },
            { eq: '\\text{SO}_4^{2-} + 2\\,\\text{CH}_2\\text{O} \\xrightarrow{\\text{SRB}} \\text{H}_2\\text{S} + 2\\,\\text{HCO}_3^-', display: true },
            { eq: '\\text{H}_2\\text{S} + \\text{Fe}^{2+} \\rightarrow \\text{FeS}_2 + 2\\,\\text{H}^+', display: true },
            { p: 'La oxidación de pirita en minas expuestas al aire genera drenaje ácido de minas (AMD), un grave problema ambiental: el pH puede bajar a < 2, movilizando metales pesados tóxicos.' },
          ]
        }
      },
      {
        id: 'comb_fos_s', label: 'Combustibles fósiles', type: 'geological', kind: 'reservoir', x: 46, y: 76,
        content: {
          tag: 'Reservorio fósil azufrado', stock: '~8 000 GtS en carbón y petróleo',
          simple: [
            { p: 'Los combustibles fósiles contienen azufre que procede de los organismos y del agua de mar del pasado. El carbón puede tener entre el 0,5 y el 5 % de azufre; el petróleo, entre el 0,1 y el 5 %. Al quemarlos, ese azufre se emite a la atmósfera como SO₂.' },
            { p: 'El petróleo de alto contenido en azufre (petróleo "ácido") es más problemático ambientalmente y más costoso de refinar. Por eso las normativas obligan a desulfurar los carburantes antes de su uso.' },
          ],
          sections: [
            { p: 'El azufre en el carbón se presenta como: pirita (FeS₂), sulfatos minerales y azufre orgánico incorporado a la materia vegetal fosilizada. En el petróleo, predomina el azufre orgánico en tioles, sulfuros y tiofenos.' },
            { h: 'Combustión del azufre en el carbón' },
            { eq: '\\text{FeS}_2 + \\frac{15}{4}\\,\\text{O}_2 \\rightarrow \\frac{1}{2}\\,\\text{Fe}_2\\text{O}_3 + 2\\,\\text{SO}_2', display: true },
            { p: 'El proceso Claus recupera el S del gas natural ácido (H₂S) en refinerías: 2H₂S + SO₂ → 3S + 2H₂O. Produce azufre elemental sólido, que se usa para fabricar ácido sulfúrico.' },
          ]
        }
      },
      {
        id: 'rocas_sulfuradas', label: 'Rocas sulfuradas', type: 'geological', kind: 'reservoir', x: 16, y: 78,
        content: {
          tag: 'Reservorio litológico', stock: '~5 × 10⁹ GtS en la litosfera',
          simple: [
            { p: 'Las rocas sulfuradas incluyen minerales como la pirita (FeS₂), la galena (PbS), la calcopirita (CuFeS₂) y el yeso (CaSO₄·2H₂O). Son el mayor reservorio de azufre de la Tierra y la fuente principal de este elemento para el ciclo biogeoquímico.' },
            { p: 'La meteorización de las rocas sulfuradas libera lentamente el azufre al suelo y al agua, poniéndolo a disposición de los ecosistemas. También son fuente de metales como el cobre, el plomo y el zinc, que se extraen por minería.' },
          ],
          sections: [
            { p: 'Los principales minerales azufrados de la litosfera son sulfuros metálicos (pirita, calcopirita, galena, esfalerita) y sulfatos (yeso CaSO₄·2H₂O, anhidrita CaSO₄, barita BaSO₄). La pirita es el más abundante.' },
            { h: 'Oxidación de la pirita (meteorización)' },
            { eq: '4\\,\\text{FeS}_2 + 15\\,\\text{O}_2 + 8\\,\\text{H}_2\\text{O} \\rightarrow 4\\,\\text{Fe(OH)}_3 + 8\\,\\text{SO}_4^{2-} + 8\\,\\text{H}^+', display: true },
            { p: 'Esta reacción libera sulfato y acidifica el agua, siendo responsable del drenaje ácido de minas. A escala geológica, la oxidación de pirita expuesta al aire durante la orogénesis montañosa aporta SO₄²⁻ al océano y CO₂ a la atmósfera (por carbonatación).' },
          ]
        }
      },
      {
        id: 'actividad_humana', label: 'Actividad humana', type: 'anthropogenic', kind: 'reservoir', x: 18, y: 52,
        content: {
          tag: 'Fuente antropogénica', stock: '~80 TgS/año emitidos (2020)',
          simple: [
            { p: 'La industria humana es actualmente la mayor fuente de azufre para la atmósfera, superando a los volcanes. La quema de carbón y petróleo con azufre, la fundición de minerales sulfurados y la refinería de petróleo emiten grandes cantidades de SO₂.' },
            { p: 'Las emisiones de SO₂ se redujeron significativamente en Europa y Norteamérica desde los años 80 gracias a la instalación de desulfuradoras en las centrales térmicas y la reducción del azufre en los combustibles. Sin embargo, Asia sigue siendo un emisor importante.' },
          ],
          sections: [
            { p: 'Las emisiones antropogénicas de SO₂ alcanzaron su pico en ~150 TgS/año en la década de 1970. Gracias a controles ambientales (Protocolo de Helsinki, 1985; Directiva NEC europea), han caído a ~80 TgS/año en 2020, todavía el doble que las emisiones volcánicas.' },
            { h: 'Desulfuración de gases de combustión (FGD)' },
            { eq: '\\text{SO}_2 + \\text{CaCO}_3 + \\frac{1}{2}\\,\\text{H}_2\\text{O} \\rightarrow \\text{CaSO}_4 \\cdot \\frac{1}{2}\\text{H}_2\\text{O} + \\text{CO}_2', display: true },
            { p: 'El yeso producido en los lavadores húmedos de SO₂ de las centrales eléctricas se usa en la industria de la construcción. En Europa, ~30 % del yeso comercializado es de origen sintético.' },
          ]
        }
      },
      // ── FLUJOS ─────────────────────────────────────────────────────────────
      {
        id: 'erupcion_s', label: 'Erupción', type: 'geological', kind: 'flow', x: 12, y: 32,
        content: {
          tag: 'Flujo volcánico', stock: '~30 TgS/año',
          simple: [
            { p: 'Los volcanes emiten grandes cantidades de SO₂ y H₂S desde el interior de la Tierra. En la atmósfera, el SO₂ se oxida a ácido sulfúrico, formando aerosoles que pueden enfríar el clima temporalmente al reflejar la luz solar.' },
            { p: 'Las grandes erupciones, como el Pinatubo en 1991 o el Tambora en 1815, inyectaron tanto SO₂ en la estratosfera que causaron descensos de temperatura de 0,5–1 °C durante 1–2 años. Esto da idea del papel del azufre en la regulación climática natural.' },
          ],
          sections: [
            { p: 'El vulcanismo emite ~30 TgS/año, principalmente como SO₂ (~90 %) y H₂S (~10 %). Las erupciones explosivas que alcanzan la estratosfera (> 25 km) son especialmente efectivas para el enfriamiento climático porque los aerosoles de sulfato persisten 1–3 años.' },
            { h: 'Forzamiento climático de erupciones explosivas' },
            { p: 'El Pinatubo (1991) inyectó ~20 TgS en la estratosfera, causando un enfriamiento global de ~0,5 °C durante 18 meses. La erupción islandesa del Laki (1783) emitió ~120 TgS y causó hambrunas en Europa por fallo de cosechas.' },
          ]
        }
      },
      {
        id: 'emision_antrop', label: 'Emisión antropogénica', type: 'anthropogenic', kind: 'flow', x: 30, y: 18,
        content: {
          tag: 'Flujo antropogénico a la atmósfera', stock: '~80 TgS/año',
          simple: [
            { p: 'La quema de combustibles fósiles que contienen azufre —principalmente carbón y fuelóleo— emite dióxido de azufre (SO₂) a la atmósfera. Este gas es el principal responsable de la lluvia ácida que dañó gravemente los bosques europeos y norteamericanos en el siglo XX.' },
            { p: 'Gracias a las regulaciones ambientales, las emisiones de SO₂ de los países industrializados se han reducido drásticamente, pero el problema sigue vigente en países en desarrollo con alta dependencia del carbón.' },
          ],
          sections: [
            { p: 'Las fuentes antropogénicas de SO₂ son: quema de carbón (~50 % del total), refinería y combustión de petróleo (~25 %), fundición de minerales sulfurados (~15 %) y otras industrias (~10 %).' },
            { h: 'Combustión de carbón con pirita' },
            { eq: '4\\,\\text{FeS}_2 + 11\\,\\text{O}_2 \\rightarrow 2\\,\\text{Fe}_2\\text{O}_3 + 8\\,\\text{SO}_2', display: true },
            { p: 'El SO₂ tiene efectos directos sobre la salud: irrita las vías respiratorias y agrava el asma. La OMS fija un límite de 20 μg/m³ como media diaria. El SO₂ es también el precursor del smog ácido en megaciudades con alto uso de carbón.' },
          ]
        }
      },
      {
        id: 'lluvia_acida', label: 'Lluvia ácida', type: 'atmospheric', kind: 'flow', x: 86, y: 28,
        content: {
          tag: 'Flujo de deposición ácida', stock: 'pH 4–5 en zonas afectadas',
          simple: [
            { p: 'El SO₂ atmosférico reacciona con el vapor de agua y el oxígeno para formar ácido sulfúrico (H₂SO₄), que cae disuelto en la lluvia. La lluvia natural tiene un pH de ~5,6; la lluvia ácida puede tener un pH de 4 o menos, siendo tan ácida como el zumo de naranja.' },
            { p: 'La lluvia ácida acidifica los suelos y las aguas superficiales, matando a los peces y destruyendo la vegetación. También corroe los edificios y monumentos de piedra caliza. En los años 70–80, devastó bosques enteros en Alemania ("Waldsterben") y Escandinavia.' },
          ],
          sections: [
            { p: 'La formación del ácido sulfúrico atmosférico es un proceso en dos etapas: primero la oxidación en fase gaseosa (con el radical OH) y luego la disolución y oxidación en fase acuosa (dentro de las gotas de nube).' },
            { h: 'Formación de H₂SO₄ en fase acuosa' },
            { eq: '\\text{SO}_2(aq) + \\text{H}_2\\text{O} \\rightarrow \\text{H}_2\\text{SO}_3 \\xrightarrow{\\text{O}_3, \\text{H}_2\\text{O}_2} \\text{H}_2\\text{SO}_4', display: true },
            { p: 'El impacto en los suelos ocurre por: acidificación directa (desplazamiento de cationes base Ca²⁺, Mg²⁺ por H⁺), movilización de Al³⁺ tóxico para las raíces, y lixiviación de nutrientes. En lagos con poca capacidad tampón, el pH puede caer a 4, eliminando casi toda la vida acuática.' },
          ]
        }
      },
      {
        id: 'acumulacion_s', label: 'Acumulación', type: 'edaphic', kind: 'flow', x: 86, y: 58,
        content: {
          tag: 'Flujo de enterramiento', stock: '~1 TgS/año',
          simple: [
            { p: 'El sulfato del suelo y el agua puede acumularse en los sedimentos del fondo marino, principalmente en forma de sulfuros (pirita) y sulfatos (yeso). En condiciones de bajo oxígeno, las bacterias reducen el sulfato produciendo H₂S, que reacciona con metales del sedimento.' },
            { p: 'Este proceso de acumulación retira azufre del ciclo activo durante millones de años, conectando el ciclo biológico rápido del azufre con el ciclo geológico lento.' },
          ],
          sections: [
            { p: 'La acumulación de S en sedimentos anóxicos es controlada por las bacterias sulfato-reductoras (SRB). La tasa global de enterramiento de pirita es ~1 TgS/año, en equilibrio con la meteorización de sulfuros.' },
            { h: 'Equilibrio geológico del azufre' },
            { p: 'A escala de millones de años, el ciclo del azufre está acoplado al ciclo del oxígeno: enterrar pirita produce O₂ (porque el S actúa de reductor alternativo en lugar del carbono orgánico); oxidar pirita consume O₂. Las variaciones en el ratio pirita/sulfato en la historia geológica reflejan cambios en la oxigenación de los océanos.' },
          ]
        }
      },
      {
        id: 'procesos_geol', label: 'Procesos geológicos', type: 'geological', kind: 'flow', x: 68, y: 78,
        content: {
          tag: 'Flujo de diagénesis profunda', stock: '~1 TgS/año',
          simple: [
            { p: 'Los sedimentos ricos en materia orgánica y azufre, sometidos a presión y temperatura durante millones de años, se transforman en combustibles fósiles que también contienen azufre. El azufre queda así "encerrado" en el carbón y el petróleo hasta que son extraídos y quemados.' },
            { p: 'Estos procesos geológicos lentos conectan el ciclo rápido del azufre con el depósito fósil, actuando como un almacenamiento a largo plazo que, una vez alterado por la industria humana, libera azufre con consecuencias ambientales.' },
          ],
          sections: [
            { p: 'Durante la diagénesis y la catagenesis, el azufre orgánico de los tejidos vivos se redistribuye en el querogen (precursor de petróleo) y la pirita. El azufre inorgánico puede unirse al carbono orgánico termoquímicamente (TSR, Thermochemical Sulfate Reduction) a temperaturas > 120 °C.' },
          ]
        }
      },
      {
        id: 'metamorfismo_s', label: 'Metamorfismo', type: 'geological', kind: 'flow', x: 54, y: 78,
        content: {
          tag: 'Flujo geológico', stock: '~1 TgS/año',
          simple: [
            { p: 'A grandes profundidades y temperaturas, las rocas que contienen azufre se transforman y liberan compuestos azufrados (principalmente H₂S y SO₂) que ascienden hacia la superficie con los fluidos hidrotermales y los volcanes.' },
            { p: 'Este proceso es el equivalente del metamorfismo del carbono: el azufre atrapado en la roca hace millones de años vuelve lentamente al ciclo activo a través de las zonas volcánicas y las dorsales oceánicas.' },
          ],
          sections: [
            { p: 'En las dorsales oceánicas, los sistemas hidrotermales (fumarolas negras y blancas) liberan H₂S a temperaturas de 250–400 °C. Las comunidades quimiosintéticas que habitan estos ecosistemas (bacterias sulfooxidantes, tubeworms) usan el H₂S como fuente de energía:' },
            { eq: '\\text{H}_2\\text{S} + 2\\,\\text{O}_2 \\rightarrow \\text{SO}_4^{2-} + 2\\,\\text{H}^+ \\quad \\Delta G = -798\\,\\text{kJ/mol}', display: true },
            { p: 'Las fumarolas hidrotermales son también importantes fuentes de metales (Fe, Cu, Zn, Mn) al océano profundo, coprecipitando con los sulfuros para formar los "chimeneas" características.' },
          ]
        }
      },
      {
        id: 'mineria', label: 'Minería', type: 'anthropogenic', kind: 'flow', x: 16, y: 66,
        content: {
          tag: 'Flujo antropogénico', stock: '~250 MtS/año extraídos como minerales',
          simple: [
            { p: 'La minería extrae rocas sulfuradas para obtener metales (cobre, plomo, zinc) y azufre elemental. Al exponer estos minerales al aire y al agua, el azufre se oxida y puede liberar ácidos y metales pesados al entorno, contaminando ríos y aguas subterráneas.' },
            { p: 'El azufre elemental extraído se usa principalmente para fabricar ácido sulfúrico, el producto químico industrial más producido del mundo, esencial para los fertilizantes, los plásticos y muchos otros productos.' },
          ],
          sections: [
            { p: 'La minería de sulfuros metálicos genera ~4 billones de toneladas de residuos anualmente. El problema ambiental principal es el drenaje ácido de minas (AMD), causado por la oxidación bacteriana (Acidithiobacillus ferrooxidans) de la pirita en presencia de agua y O₂.' },
            { p: 'La producción de ácido sulfúrico a partir del azufre elemental es la mayor industria química del mundo: ~250 Mt H₂SO₄/año. El 60 % se usa para fabricar fertilizantes fosfatados (superfosfato), cerrando el vínculo entre los ciclos del azufre y el fósforo.' },
          ]
        }
      },
      {
        id: 'extraccion_s', label: 'Extracción y combustión', type: 'anthropogenic', kind: 'flow', x: 32, y: 78,
        content: {
          tag: 'Flujo antropogénico fósil', stock: '~80 TgS/año quemados',
          simple: [
            { p: 'Al extraer y quemar carbón y petróleo, el azufre que contienen estos combustibles se libera a la atmósfera como SO₂. Es el mayor flujo de azufre generado por la humanidad y el principal responsable de la lluvia ácida industrial.' },
            { p: 'Reducir el contenido de azufre en los combustibles y desulfurar los gases de combustión ha sido uno de los grandes éxitos ambientales de las últimas décadas, permitiendo la recuperación de los bosques y lagos acidificados en Europa y América del Norte.' },
          ],
          sections: [
            { p: 'La extracción de combustibles fósiles libera S de dos formas: como SO₂ durante la combustión (S integrado en la materia fósil), y como H₂S en el gas natural ácido (gas asociado a yacimientos con H₂S libre, hasta el 30 % del volumen en algunos campos).' },
            { h: 'Proceso Claus de recuperación de azufre' },
            { eq: '2\\,\\text{H}_2\\text{S} + \\text{SO}_2 \\rightarrow 3\\,\\text{S} + 2\\,\\text{H}_2\\text{O}', display: true },
            { p: 'El proceso Claus recupera azufre elemental de los gases ácidos de refinería con una eficiencia > 99 %. Este azufre recuperado (~70 Mt/año) se usa para fabricar ácido sulfúrico, convirtiendo un residuo contaminante en materia prima industrial.' },
          ]
        }
      },
    ],
  },

};

window.BGQ_CYCLES = CYCLES;
