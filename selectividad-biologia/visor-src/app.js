/* Visor de preguntas de Selectividad · Biología (PAU/PEvAU Andalucía) */
(function () {
  "use strict";

  const Q = window.DB.q;
  const M = window.DB.meta;
  const $ = (id) => document.getElementById(id);
  const el = (tag, attrs, ...kids) => {
    const n = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      if (k === "class") n.className = attrs[k];
      else if (k === "text") n.textContent = attrs[k];
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== undefined && attrs[k] !== null && attrs[k] !== false) n.setAttribute(k, attrs[k]);
    }
    for (const c of kids) if (c != null) n.append(c);
    return n;
  };
  const fold = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const store = {
    get(k, d) { try { const v = localStorage.getItem("selbio:" + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem("selbio:" + k, JSON.stringify(v)); } catch (e) { /* sin almacenamiento */ } },
  };

  const YEARS = [...new Set(Q.map((q) => q.y))].sort((a, b) => a - b);
  const Y0 = YEARS[0], Y1 = YEARS[YEARS.length - 1];
  const TIPOS = ["Titular", "Suplente", "Reserva", "Modelo"];
  const CONVS = [
    ["Junio", "Junio"], ["Septiembre", "Septiembre"], ["Ordinaria", "Ordinaria"], ["Extraordinaria", "Extraordinaria"],
    ["A", "Examen A"], ["B", "Examen B"], ["", "Sin indicar"],
  ];
  const TIPO_HELP = {
    Titular: "Examen titular de la convocatoria",
    Suplente: "Examen suplente (se usa si hay incidencias con el titular)",
    Reserva: "Examen de reserva",
    Modelo: "Uno de los 6 modelos del año; el zip original no indica en qué convocatoria se usó",
  };
  const SCHEMES = {
    lomloe: { key: "b2", names: M.lomloe, codes: Object.keys(M.lomloe), topicKey: "lomloe", prefix: "" },
    lomce: { key: "b1", names: M.lomce, codes: Object.keys(M.lomce), topicKey: "lomce", prefix: "Bloque " },
  };
  const STOP = new Set("a al ante bajo con contra de del desde durante e el en entre es esta este esto hacia hasta la las le lo los mas mediante o para por que se segun sin sobre su sus tras u un una uno unos unas y ya".split(" "));

  /* ---------------- índice de búsqueda ---------------- */
  const blockWords = (q) => {
    const w = [];
    for (const c of q.b2) w.push(M.lomloe[c]);
    for (const c of q.b1) w.push(M.lomce[c]);
    return w.join(" ");
  };
  const DOCS = Q.map((q, i) => {
    const meta = [q.y, q.t, q.c, q.l, q.s1, q.s2, blockWords(q), q.o ? "ocr" : "", q.f ? "figura imagen" : ""].join(" ");
    return {
      i,
      tx: fold(q.tx),
      ct: fold(q.ct || ""),
      meta: fold(meta),
    };
  });
  const tokenize = (s) => s.split(/[^a-z0-9ñ]+/).filter(Boolean);
  const VOC = new Map(); // palabra -> Set(doc) (enunciado + metadatos)
  const VOCT = new Map(); // palabra -> Set(doc) (solo enunciado, para exclusiones)
  const VOCC = new Map(); // palabra -> Set(doc) (criterios)
  const addWords = (map, text, i) => {
    for (const w of tokenize(text)) {
      let s = map.get(w);
      if (!s) map.set(w, (s = new Set()));
      s.add(i);
    }
  };
  for (const d of DOCS) {
    addWords(VOC, d.tx, d.i);
    addWords(VOCT, d.tx, d.i);
    addWords(VOC, d.meta, d.i);
    addWords(VOCC, d.ct, d.i);
  }
  const VOCW = [...VOC.keys()].sort();
  const VOCTW = [...VOCT.keys()].sort();
  const VOCCW = [...VOCC.keys()].sort();

  function prefixDocs(words, map, tok) {
    const out = new Set();
    if (tok.length < 3 || /^\d+$/.test(tok)) {
      const s = map.get(tok);
      if (s) s.forEach((x) => out.add(x));
      return out;
    }
    // búsqueda binaria del primer término con ese prefijo
    let lo = 0, hi = words.length;
    while (lo < hi) { const m = (lo + hi) >> 1; if (words[m] < tok) lo = m + 1; else hi = m; }
    for (let k = lo; k < words.length && words[k].startsWith(tok); k++) map.get(words[k]).forEach((x) => out.add(x));
    return out;
  }

  function parseQuery(raw) {
    const q = fold(raw.replace(/[«»“”]/g, '"'));
    const terms = [];
    const re = /(-?)"([^"]+)"|(-?)(\d{4})\s*-\s*(\d{4})|(-?)([^\s"]+)/g;
    let m;
    while ((m = re.exec(q))) {
      if (m[2]) terms.push({ neg: !!m[1], phrase: m[2].trim() });
      else if (m[4]) terms.push({ neg: !!m[3], range: [+m[4], +m[5]] });
      else {
        for (const w of tokenize(m[7])) if (!STOP.has(w)) terms.push({ neg: !!m[6], word: w });
      }
    }
    return terms;
  }

  function searchSet(raw, inCrit) {
    const terms = parseQuery(raw);
    if (!terms.length) return { set: null, words: [] };
    let cur = null;
    const excl = [];
    const hl = [];
    for (const t of terms) {
      let s;
      if (t.range) {
        s = new Set(Q.map((q, i) => (q.y >= t.range[0] && q.y <= t.range[1] ? i : -1)).filter((i) => i >= 0));
      } else if (t.phrase) {
        s = new Set();
        DOCS.forEach((d) => { if (d.tx.includes(t.phrase) || (!t.neg && d.meta.includes(t.phrase)) || (inCrit && d.ct.includes(t.phrase))) s.add(d.i); });
        if (!t.neg) hl.push(t.phrase);
      } else if (t.neg && !/^\d+$/.test(t.word)) {
        // las exclusiones solo miran el enunciado (y los criterios si se pide)
        s = prefixDocs(VOCTW, VOCT, t.word);
        if (inCrit) prefixDocs(VOCCW, VOCC, t.word).forEach((x) => s.add(x));
      } else {
        s = prefixDocs(VOCW, VOC, t.word);
        if (inCrit) prefixDocs(VOCCW, VOCC, t.word).forEach((x) => s.add(x));
        if (!t.neg) hl.push(t.word);
      }
      if (t.neg) excl.push(s);
      else cur = cur == null ? s : new Set([...cur].filter((x) => s.has(x)));
    }
    if (cur == null) cur = new Set(Q.map((_, i) => i));
    for (const s of excl) cur = new Set([...cur].filter((x) => !s.has(x)));
    return { set: cur, words: hl };
  }

  /* ---------------- estado ---------------- */
  const DEF = { scheme: "lomloe", blocks: [], topics: [], tipos: [], convs: [], y0: Y0, y1: Y1, fig: false, dup: false, q: "", crit: false, order: "chron" };
  const S = Object.assign({}, DEF, store.get("state", {}));
  S.y0 = Math.max(Y0, Math.min(Y1, S.y0)); S.y1 = Math.max(S.y0, Math.min(Y1, S.y1));
  if (!SCHEMES[S.scheme]) S.scheme = "lomloe";
  let LIST = [];
  let POS = 0;
  let HL = [];
  let listLimit = 150;
  let openCrit = store.get("openCrit", false);
  let openText = false;
  const expanded = new Set(store.get("expanded", []));

  const save = () => store.set("state", S);

  function passes(q, i, skip, sres) {
    const sc = SCHEMES[S.scheme];
    if (skip !== "blocks" && (S.blocks.length || S.topics.length)) {
      const okB = q[sc.key].some((b) => S.blocks.includes(String(b)));
      const okT = q.tp.some((t) => S.topics.includes(t));
      if (!okB && !okT) return false;
    }
    if (skip !== "tipos" && S.tipos.length && !S.tipos.includes(q.t)) return false;
    if (skip !== "convs" && S.convs.length && !S.convs.includes(q.c)) return false;
    if (skip !== "years" && (q.y < S.y0 || q.y > S.y1)) return false;
    if (S.fig && !q.f) return false;
    if (S.dup && !q.d.length) return false;
    if (sres && !sres.has(i)) return false;
    return true;
  }

  const CONV_ORDER = { Junio: 0, Ordinaria: 0, A: 0, Septiembre: 1, Extraordinaria: 1, B: 1, "": 2 };
  function sortList(list) {
    const sc = SCHEMES[S.scheme];
    const firstBlock = (q) => sc.codes.indexOf(String(q[sc.key][0]));
    if (S.order === "chronDesc") list.sort((a, b) => Q[b].y - Q[a].y || a - b);
    else if (S.order === "block") list.sort((a, b) => firstBlock(Q[a]) - firstBlock(Q[b]) || a - b);
    else list.sort((a, b) => a - b);
    return list;
  }

  function recompute(keepId) {
    const sr = searchSet(S.q, S.crit);
    HL = sr.words;
    const list = [];
    Q.forEach((q, i) => { if (passes(q, i, null, sr.set)) list.push(i); });
    LIST = sortList(list);
    const want = keepId != null ? keepId : (LIST.length ? Q[LIST[Math.min(POS, LIST.length - 1)]].id : null);
    const at = LIST.findIndex((i) => Q[i].id === want);
    POS = at >= 0 ? at : 0;
    listLimit = Math.max(150, POS + 50);
    renderFacets(sr.set);
    renderList();
    renderCard();
    save();
  }

  /* ---------------- filtros ---------------- */
  function countBy(skip, sset, fn) {
    const c = new Map();
    Q.forEach((q, i) => {
      if (!passes(q, i, skip, sset)) return;
      for (const k of fn(q)) c.set(k, (c.get(k) || 0) + 1);
    });
    return c;
  }

  function renderFacets(sset) {
    const sc = SCHEMES[S.scheme];
    document.querySelectorAll(".seg button").forEach((b) => b.setAttribute("aria-checked", b.dataset.scheme === S.scheme));
    // bloques y temas
    const cb = countBy("blocks", sset, (q) => q[sc.key].map(String));
    const ct = countBy("blocks", sset, (q) => q.tp);
    const wrap = $("fBlocks");
    wrap.textContent = "";
    for (const code of sc.codes) {
      const topics = Object.keys(M.topics).filter((t) => String(M.topics[t][sc.topicKey]) === code);
      const on = S.blocks.includes(code);
      const isOpen = expanded.has(S.scheme + code);
      const row = el("label", { class: "blk-row", title: sc.names[code] },
        el("input", { type: "checkbox", checked: on || null, onchange: (e) => { toggleArr(S.blocks, code, e.target.checked); recompute(curId()); } }),
        el("span", { class: "dot", style: `background:var(--b-${code})` }),
        el("span", { class: "blk-name" }, el("b", { text: (S.scheme === "lomloe" ? code : code + ".") }), sc.names[code]),
        el("span", { class: "cnt", text: cb.get(code) || 0 }),
        topics.length > 1 ? el("button", {
          class: "tog", title: "Temas", "aria-expanded": isOpen, text: isOpen ? "▾" : "▸",
          onclick: (e) => { e.preventDefault(); const k = S.scheme + code; expanded.has(k) ? expanded.delete(k) : expanded.add(k); store.set("expanded", [...expanded]); renderFacets(sset); },
        }) : null);
      const box = el("div", { class: "blk" }, row);
      if (topics.length > 1 && isOpen) {
        const tl = el("div", { class: "topics" });
        for (const t of topics) {
          tl.append(el("label", { class: "blk-row" },
            el("input", { type: "checkbox", checked: on || S.topics.includes(t) || null, disabled: on || null, onchange: (e) => { toggleArr(S.topics, t, e.target.checked); recompute(curId()); } }),
            el("span", { class: "blk-name", text: M.topics[t].label }),
            el("span", { class: "cnt", text: ct.get(t) || 0 })));
        }
        box.append(tl);
      }
      wrap.append(box);
    }
    // tipo
    const ctp = countBy("tipos", sset, (q) => [q.t]);
    chips($("fTipo"), TIPOS.map((t) => [t, t]), S.tipos, ctp, TIPO_HELP);
    // convocatoria
    const ccv = countBy("convs", sset, (q) => [q.c]);
    chips($("fConv"), CONVS.filter(([k]) => ccv.has(k) || S.convs.includes(k)), S.convs, ccv, {
      A: "2023-2025: examen A (probablemente convocatoria ordinaria)", B: "2023-2025: examen B (probablemente extraordinaria)",
      "": "El zip original no indica la convocatoria",
    });
    // años
    const cy = countBy("years", sset, (q) => [q.y]);
    $("yMin").min = $("yMax").min = Y0; $("yMin").max = $("yMax").max = Y1;
    $("yMin").value = S.y0; $("yMax").value = S.y1;
    $("yearLbl").textContent = S.y0 === S.y1 ? `(${S.y0})` : `(${S.y0}–${S.y1})`;
    const yg = $("fYears");
    yg.textContent = "";
    for (const y of YEARS) {
      yg.append(el("button", {
        class: y >= S.y0 && y <= S.y1 ? "on" : "", title: `${y}: ${cy.get(y) || 0} preguntas`, text: "'" + String(y).slice(2),
        disabled: cy.get(y) ? null : true,
        onclick: () => {
          if (S.y0 === y && S.y1 === y) { S.y0 = Y0; S.y1 = Y1; } else { S.y0 = S.y1 = y; }
          recompute(curId());
        },
      }));
    }
    $("fFig").checked = S.fig;
    $("fDup").checked = S.dup;
    $("q").value !== S.q && ($("q").value = S.q);
    $("inCrit").checked = S.crit;
    $("order").value = S.order;
  }

  function chips(box, items, arr, counts, help) {
    box.textContent = "";
    for (const [k, lab] of items) {
      const on = arr.includes(k);
      box.append(el("button", {
        class: "chip", "aria-pressed": on, title: help && help[k],
        onclick: () => { toggleArr(arr, k, !on); recompute(curId()); },
      }, lab, el("span", { class: "cnt", text: counts.get(k) || 0 })));
    }
  }

  function toggleArr(arr, v, on) {
    const i = arr.indexOf(v);
    if (on && i < 0) arr.push(v);
    if (!on && i >= 0) arr.splice(i, 1);
  }

  const curId = () => (LIST.length ? Q[LIST[POS]].id : null);

  /* ---------------- lista ---------------- */
  function snippet(q) {
    const t = q.tx.replace(/^\s*(Pregunta\s+)?[A-D]?\.?\s*\d+(\.\d)?\s*[.\-–]*\s*(\(\d puntos\))?\s*/i, "");
    if (!HL.length) return [t.slice(0, 180)];
    const ft = fold(t);
    let first = -1;
    for (const w of HL) { const k = ft.indexOf(w); if (k >= 0 && (first < 0 || k < first)) first = k; }
    let start = Math.max(0, first - 50);
    if (first < 0) start = 0;
    const s = t.slice(start, start + 200);
    return highlight(s, start > 0);
  }
  function highlight(s, lead) {
    const fs = fold(s);
    const marks = [];
    for (const w of HL) {
      let k = 0;
      while ((k = fs.indexOf(w, k)) >= 0) { marks.push([k, k + w.length]); k += w.length; }
    }
    marks.sort((a, b) => a[0] - b[0]);
    const out = [];
    if (lead) out.push("…");
    let p = 0;
    for (const [a, b] of marks) {
      if (a < p) continue;
      out.push(s.slice(p, a), el("mark", { text: s.slice(a, b) }));
      p = b;
    }
    out.push(s.slice(p));
    return out;
  }

  function renderList() {
    $("count").textContent = `${LIST.length} ${LIST.length === 1 ? "pregunta" : "preguntas"}`;
    const ol = $("results");
    ol.textContent = "";
    const sc = SCHEMES[S.scheme];
    const n = Math.min(LIST.length, listLimit);
    for (let k = 0; k < n; k++) {
      const q = Q[LIST[k]];
      const li = el("li", { class: k === POS ? "cur" : "", "data-k": k, onclick: () => go(k) },
        el("span", { class: "r-bar", style: `background:var(--b-${q[sc.key][0]})` }),
        el("div", { class: "r-body" },
          el("div", { class: "r-top" }, el("b", { text: q.y }), `${q.l}${q.c && !/^[AB]$/.test(q.c) ? " · " + q.c : ""} · ${q.s2}`),
          el("div", { class: "r-txt" }, ...snippet(q))));
      ol.append(li);
    }
    $("more").hidden = LIST.length <= listLimit;
    $("posTot").textContent = LIST.length;
  }

  function markList() {
    const ol = $("results");
    ol.querySelectorAll("li.cur").forEach((li) => li.classList.remove("cur"));
    if (POS >= listLimit) { listLimit = POS + 50; renderList(); }
    const li = ol.querySelector(`li[data-k="${POS}"]`);
    if (li) {
      li.classList.add("cur");
      const r = li.getBoundingClientRect(), R = ol.getBoundingClientRect();
      if (r.top < R.top || r.bottom > R.bottom) li.scrollIntoView({ block: "center" });
    }
  }

  /* ---------------- tarjeta ---------------- */
  const niceName = (q, extra) => `Biologia-${q.y}-${q.l.replace(/\s+/g, "")}${q.c ? "-" + q.c : ""}-${q.s2.replace(/[^\w.-]+/g, "")}${extra || ""}.webp`;

  function renderCard() {
    const has = LIST.length > 0;
    $("empty").hidden = has;
    $("card").hidden = !has;
    $("prev").disabled = $("next").disabled = !has;
    $("rand").disabled = LIST.length < 2;
    $("posIn").value = has ? POS + 1 : "";
    $("posIn").max = LIST.length;
    if (!has) return;
    const q = Q[LIST[POS]];
    const sc = SCHEMES[S.scheme];
    const cr = $("crumbs");
    cr.textContent = "";
    const lab = q.l.startsWith(q.t) ? q.l : q.t;
    cr.append(el("span", { class: "year", text: q.y }),
      el("span", { class: `pill tipo-${q.t}`, title: TIPO_HELP[q.t], text: lab }));
    if (lab !== q.l) cr.append(el("span", { class: "pill", text: q.l }));
    if (q.c) cr.append(el("span", { class: "pill", text: /^[AB]$/.test(q.c) ? "Examen " + q.c : q.c }));
    cr.append(el("span", { class: "pill", text: q.s1 }), el("span", { class: "pill", text: q.s2 }));
    const bd = $("badges");
    bd.textContent = "";
    for (const b of q[sc.key]) {
      bd.append(el("button", {
        class: "bdg", title: "Filtrar por este bloque", onclick: () => { S.blocks = [String(b)]; S.topics = []; recompute(q.id); },
      }, el("span", { class: "dot", style: `background:var(--b-${b})` }), `${sc.prefix}${b} · ${sc.names[b]}`));
    }
    for (const t of q.tp) {
      bd.append(el("button", {
        class: "bdg topic", title: "Filtrar por este tema", onclick: () => { S.topics = [t]; S.blocks = []; expanded.add(S.scheme + M.topics[t][sc.topicKey]); recompute(q.id); },
        text: M.topics[t].label,
      }));
    }
    const img = $("qimg");
    img.src = q.i;
    img.width = q.wh[0]; img.height = q.wh[1];
    img.alt = `Enunciado: ${q.tx.slice(0, 300)}`;
    // criterios
    const crit = $("crit");
    crit.hidden = !openCrit;
    $("btnCrit").setAttribute("aria-expanded", openCrit);
    crit.textContent = "";
    if (openCrit) {
      crit.append(el("h3", { text: "Criterios de corrección" }));
      if (!q.cr.length) crit.append(el("p", { class: "muted", text: "Los archivos originales no incluyen criterios para esta pregunta." }));
      q.cr.forEach((src, k) => crit.append(el("figure", {}, el("img", { src, alt: "Criterios de corrección", loading: "lazy", onclick: () => openLB(k + 1) }))));
    }
    // texto
    const tx = $("txt");
    tx.hidden = !openText;
    $("btnText").setAttribute("aria-expanded", openText);
    tx.textContent = "";
    if (openText) {
      tx.append(el("h3", { text: q.o ? "Texto (obtenido por OCR, puede contener errores)" : "Texto del enunciado" }), el("p", {}, ...(HL.length ? highlight(q.tx) : [q.tx])));
    }
    // repeticiones
    const dp = $("dups");
    dp.textContent = "";
    dp.hidden = !q.d.length;
    if (q.d.length) {
      const ul = el("ul");
      for (const id of q.d) {
        const o = Q.find((x) => x.id === id);
        if (!o) continue;
        ul.append(el("li", {}, el("a", { onclick: () => jumpTo(id), text: `${o.y} · ${o.l}${o.c ? " · " + (/^[AB]$/.test(o.c) ? "Examen " + o.c : o.c) : ""} · ${o.s1} · ${o.s2}` })));
      }
      dp.append(el("h3", { text: `También apareció en (${q.d.length})` }), ul);
    }
    markList();
    const h = "#" + q.id;
    if (location.hash !== h) history.replaceState(null, "", h);
    // precarga de las vecinas
    for (const d of [1, -1]) {
      const n = LIST[(POS + d + LIST.length) % LIST.length];
      if (n != null) { const im = new Image(); im.src = Q[n].i; }
    }
    $("main").scrollTop = 0;
  }

  function go(k) {
    if (!LIST.length) return;
    POS = (k + LIST.length) % LIST.length;
    renderCard();
  }
  function jumpTo(id) {
    let k = LIST.findIndex((i) => Q[i].id === id);
    if (k < 0) {
      Object.assign(S, { blocks: [], topics: [], tipos: [], convs: [], y0: Y0, y1: Y1, fig: false, dup: false, q: "" });
      recompute(id);
      toast("Filtros quitados para mostrar la pregunta");
      return;
    }
    go(k);
  }
  function random() {
    if (LIST.length < 2) return;
    let k;
    do { k = Math.floor(Math.random() * LIST.length); } while (k === POS);
    go(k);
  }

  /* ---------------- lightbox ---------------- */
  const LB = { imgs: [], k: 0, s: 1, x: 0, y: 0, fit: 1, ptrs: new Map(), last: null };
  function lbImages() {
    const q = Q[LIST[POS]];
    const out = [{ src: q.i, cap: `${q.y} · ${q.l} · ${q.s2} · Enunciado`, name: niceName(q) }];
    q.cr.forEach((src, k) => out.push({ src, cap: `${q.y} · ${q.l} · ${q.s2} · Criterios${q.cr.length > 1 ? " " + (k + 1) : ""}`, name: niceName(q, "-criterios" + (q.cr.length > 1 ? k + 1 : "")) }));
    return out;
  }
  function openLB(k) {
    if (!LIST.length) return;
    LB.imgs = lbImages();
    LB.k = Math.max(0, Math.min(k || 0, LB.imgs.length - 1));
    $("lb").hidden = false;
    document.body.style.overflow = "hidden";
    loadLB();
  }
  function loadLB() {
    const it = LB.imgs[LB.k];
    const im = $("lbImg");
    $("lbCap").textContent = it.cap;
    $("lbPrev").disabled = $("lbNext").disabled = LB.imgs.length < 2;
    im.onload = () => fitLB();
    im.src = it.src;
    if (im.complete && im.naturalWidth) fitLB();
  }
  function applyLB() {
    $("lbImg").style.transform = `translate(${LB.x}px,${LB.y}px) scale(${LB.s})`;
    $("lbFit").textContent = Math.round(LB.s * 100 / 2) * 2 + "%";
  }
  function fitLB() {
    const im = $("lbImg"), st = $("lbStage").getBoundingClientRect();
    const w = im.naturalWidth, h = im.naturalHeight;
    if (!w) return;
    LB.fit = Math.min((st.width - 24) / w, (st.height - 24) / h, 3);
    LB.s = LB.fit;
    LB.x = (st.width - w * LB.s) / 2;
    LB.y = Math.max(12, (st.height - h * LB.s) / 2);
    applyLB();
  }
  function zoomAt(f, px, py) {
    const ns = Math.max(0.1, Math.min(8, LB.s * f));
    LB.x = px - (px - LB.x) * (ns / LB.s);
    LB.y = py - (py - LB.y) * (ns / LB.s);
    LB.s = ns;
    applyLB();
  }
  function zoomCenter(f) { const r = $("lbStage").getBoundingClientRect(); zoomAt(f, r.width / 2, r.height / 2); }
  function closeLB() { $("lb").hidden = true; document.body.style.overflow = ""; $("lbImg").src = ""; }
  function stepLB(d) { if (LB.imgs.length < 2) return; LB.k = (LB.k + d + LB.imgs.length) % LB.imgs.length; loadLB(); }

  function download(src, name) {
    const a = el("a", { href: src, download: name });
    document.body.append(a); a.click(); a.remove();
  }
  function downloadPng() {
    const it = LB.imgs[LB.k];
    const im = new Image();
    im.onload = () => {
      try {
        const c = document.createElement("canvas");
        c.width = im.naturalWidth; c.height = im.naturalHeight;
        const g = c.getContext("2d");
        g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0);
        c.toBlob((b) => {
          if (!b) throw new Error("toBlob");
          const u = URL.createObjectURL(b);
          download(u, it.name.replace(/\.webp$/, ".png"));
          setTimeout(() => URL.revokeObjectURL(u), 4000);
        }, "image/png");
      } catch (e) {
        toast("El navegador no permite convertir a PNG abriendo el visor como archivo local; se descarga en WebP.");
        download(it.src, it.name);
      }
    };
    im.onerror = () => download(it.src, it.name);
    im.src = it.src;
  }

  function bindLB() {
    const st = $("lbStage");
    st.addEventListener("wheel", (e) => {
      e.preventDefault();
      const r = st.getBoundingClientRect();
      zoomAt(Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0018)), e.clientX - r.left, e.clientY - r.top);
    }, { passive: false });
    st.addEventListener("pointerdown", (e) => {
      st.setPointerCapture(e.pointerId);
      LB.ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
      st.classList.add("drag");
      LB.last = null;
    });
    st.addEventListener("pointermove", (e) => {
      if (!LB.ptrs.has(e.pointerId)) return;
      const prev = LB.ptrs.get(e.pointerId);
      LB.ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (LB.ptrs.size === 1) {
        LB.x += e.clientX - prev.x; LB.y += e.clientY - prev.y; applyLB();
      } else if (LB.ptrs.size === 2) {
        const [a, b] = [...LB.ptrs.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        const r = st.getBoundingClientRect();
        const cx = (a.x + b.x) / 2 - r.left, cy = (a.y + b.y) / 2 - r.top;
        if (LB.last) { zoomAt(d / LB.last.d, cx, cy); LB.x += cx - LB.last.cx; LB.y += cy - LB.last.cy; applyLB(); }
        LB.last = { d, cx, cy };
      }
    });
    const up = (e) => { LB.ptrs.delete(e.pointerId); if (LB.ptrs.size < 2) LB.last = null; if (!LB.ptrs.size) st.classList.remove("drag"); };
    st.addEventListener("pointerup", up);
    st.addEventListener("pointercancel", up);
    st.addEventListener("dblclick", (e) => {
      const r = st.getBoundingClientRect();
      if (Math.abs(LB.s - LB.fit) < 0.01) zoomAt(Math.max(1, LB.fit * 2) / LB.s, e.clientX - r.left, e.clientY - r.top);
      else fitLB();
    });
    $("lbIn").onclick = () => zoomCenter(1.25);
    $("lbOut").onclick = () => zoomCenter(0.8);
    $("lbFit").onclick = fitLB;
    $("lbClose").onclick = closeLB;
    $("lbPrev").onclick = () => stepLB(-1);
    $("lbNext").onclick = () => stepLB(1);
    $("lbDl").onclick = () => { const it = LB.imgs[LB.k]; download(it.src, it.name); };
    $("lbPng").onclick = downloadPng;
    window.addEventListener("resize", () => { if (!$("lb").hidden) fitLB(); });
  }

  /* ---------------- utilidades UI ---------------- */
  let toastT;
  function toast(msg) {
    const t = $("toast");
    t.textContent = msg; t.classList.add("show");
    clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 2600);
  }
  function setTheme(v) {
    if (v) document.documentElement.setAttribute("data-theme", v); else document.documentElement.removeAttribute("data-theme");
    store.set("theme", v);
  }
  const wide = () => window.matchMedia("(min-width: 1181px)").matches;
  function toggleList() {
    const L = document.querySelector(".layout");
    if (wide()) { L.classList.toggle("no-list"); store.set("noList", L.classList.contains("no-list")); }
    else L.classList.toggle("show-list");
    markList();
  }

  /* ---------------- eventos ---------------- */
  function bind() {
    let t;
    $("q").addEventListener("input", (e) => { clearTimeout(t); t = setTimeout(() => { S.q = e.target.value; POS = 0; recompute(null); }, 160); });
    $("q").addEventListener("keydown", (e) => { if (e.key === "Enter") { clearTimeout(t); S.q = e.target.value; recompute(null); e.target.blur(); } });
    $("qClear").onclick = () => { $("q").value = ""; S.q = ""; recompute(curId()); $("q").focus(); };
    $("inCrit").onchange = (e) => { S.crit = e.target.checked; recompute(curId()); };
    document.querySelectorAll(".seg button").forEach((b) => b.addEventListener("click", () => {
      if (S.scheme === b.dataset.scheme) return;
      S.scheme = b.dataset.scheme; S.blocks = []; recompute(curId());
    }));
    const yr = () => {
      let a = +$("yMin").value, b = +$("yMax").value;
      if (a > b) [a, b] = [b, a];
      S.y0 = a; S.y1 = b; recompute(curId());
    };
    $("yMin").addEventListener("input", yr);
    $("yMax").addEventListener("input", yr);
    $("fFig").onchange = (e) => { S.fig = e.target.checked; recompute(curId()); };
    $("fDup").onchange = (e) => { S.dup = e.target.checked; recompute(curId()); };
    const reset = () => { Object.assign(S, { blocks: [], topics: [], tipos: [], convs: [], y0: Y0, y1: Y1, fig: false, dup: false, q: "" }); $("q").value = ""; recompute(curId()); };
    $("btnReset").onclick = reset;
    $("btnReset2").onclick = reset;
    $("order").onchange = (e) => { S.order = e.target.value; recompute(curId()); };
    $("more").onclick = () => { listLimit += 150; renderList(); markList(); };
    $("prev").onclick = () => go(POS - 1);
    $("next").onclick = () => go(POS + 1);
    $("rand").onclick = random;
    $("toggleList").onclick = toggleList;
    $("posIn").addEventListener("change", (e) => { const v = parseInt(e.target.value, 10); if (v >= 1 && v <= LIST.length) go(v - 1); else renderCard(); });
    $("btnCrit").onclick = () => { openCrit = !openCrit; store.set("openCrit", openCrit); renderCard(); };
    $("btnText").onclick = () => { openText = !openText; renderCard(); };
    $("qimg").onclick = () => openLB(0);
    $("zoomHint").onclick = () => openLB(0);
    $("btnDl").onclick = () => { const q = Q[LIST[POS]]; download(q.i, niceName(q)); };
    $("btnLink").onclick = () => {
      const url = location.href;
      (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(() => toast("Enlace copiado")).catch(() => { window.prompt("Copia el enlace:", url); });
    };
    $("btnTheme").onclick = () => {
      const cur = document.documentElement.getAttribute("data-theme");
      const dark = cur ? cur === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
      setTheme(dark ? "light" : "dark");
    };
    $("btnHelp").onclick = () => { $("help").hidden = false; };
    $("helpClose").onclick = () => { $("help").hidden = true; };
    $("help").addEventListener("click", (e) => { if (e.target === $("help")) $("help").hidden = true; });
    $("btnFilters").onclick = (e) => { e.stopPropagation(); $("filters").classList.toggle("open"); };
    document.addEventListener("click", (e) => {
      const f = $("filters");
      if (f.classList.contains("open") && !f.contains(e.target) && e.target !== $("btnFilters")) f.classList.remove("open");
      const L = document.querySelector(".layout");
      if (L.classList.contains("show-list") && !$("list").contains(e.target) && !$("toggleList").contains(e.target)) L.classList.remove("show-list");
    });
    window.addEventListener("hashchange", () => { const id = location.hash.slice(1); if (id && id !== curId()) jumpTo(id); });
    document.addEventListener("keydown", (e) => {
      const lbOpen = !$("lb").hidden;
      if (e.key === "Escape") {
        if (lbOpen) closeLB(); else if (!$("help").hidden) $("help").hidden = true;
        else { $("filters").classList.remove("open"); document.querySelector(".layout").classList.remove("show-list"); }
        return;
      }
      const tag = (e.target.tagName || "").toLowerCase();
      if (tag === "input" || tag === "select" || tag === "textarea" || e.ctrlKey || e.metaKey || e.altKey) return;
      if (lbOpen) {
        if (e.key === "+" || e.key === "=") zoomCenter(1.25);
        else if (e.key === "-") zoomCenter(0.8);
        else if (e.key === "0") fitLB();
        else if (e.key === "ArrowRight") stepLB(1);
        else if (e.key === "ArrowLeft") stepLB(-1);
        else return;
        e.preventDefault();
        return;
      }
      const k = e.key.toLowerCase();
      if (e.key === "ArrowRight" || k === "j") go(POS + 1);
      else if (e.key === "ArrowLeft" || k === "k") go(POS - 1);
      else if (k === "r") random();
      else if (k === "c") $("btnCrit").click();
      else if (k === "t") $("btnText").click();
      else if (k === "z" || e.key === " ") openLB(0);
      else if (k === "l") toggleList();
      else if (e.key === "/") $("q").focus();
      else if (e.key === "?") $("help").hidden = false;
      else return;
      e.preventDefault();
    });
  }

  /* ---------------- inicio ---------------- */
  setTheme(store.get("theme", null));
  if (store.get("noList", false) && wide()) document.querySelector(".layout").classList.add("no-list");
  $("yearSpan").textContent = `${Y0}–${Y1} · ${Q.length} preguntas`;
  bind();
  bindLB();
  const hashId = location.hash.slice(1);
  if (hashId && Q.some((q) => q.id === hashId)) {
    recompute(hashId);
    if (curId() !== hashId) jumpTo(hashId);
  } else {
    recompute(store.get("last", null));
  }
  window.addEventListener("beforeunload", () => store.set("last", curId()));
})();
