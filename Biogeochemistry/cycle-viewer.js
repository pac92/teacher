// CycleViewer — Vue 2 component
// Requires: window.Vue (CDN 2.7), window.katex (CDN 0.16.9)
// Loaded as a regular <script> tag; exposes window.BGQ_CycleViewer

(function () {

  const PANEL_W = 400;

  // ── KaTeX helpers ──────────────────────────────────────────────────────────

  function katexStr(tex, display) {
    return window.katex.renderToString(tex, { throwOnError: false, displayMode: !!display });
  }

  function escHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function renderSections(sections, color) {
    return sections.map(function (s) {
      if (s.p) {
        var parts = s.p.split(/(\$[^$]+\$)/g);
        var inner = parts.map(function (p) {
          return p.startsWith('$') ? katexStr(p.slice(1, -1), false) : escHtml(p);
        }).join('');
        return '<p>' + inner + '</p>';
      }
      if (s.h) return '<h3 style="color:' + color + '">' + escHtml(s.h) + '</h3>';
      if (s.eq) {
        return s.display
          ? '<div class="katex-block">' + katexStr(s.eq, true) + '</div>'
          : '<p>' + katexStr(s.eq, false) + '</p>';
      }
      return '';
    }).join('');
  }

  function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  // ── Component ──────────────────────────────────────────────────────────────

  window.BGQ_CycleViewer = {
    name: 'CycleViewer',
    props: ['cycle'],

    data: function () {
      return {
        imgW: this.cycle.imgW || 1688,
        imgH: this.cycle.imgH || 1125,
        zoom: 1,
        pan: { x: 0, y: 0 },
        selectedId: null,
        panelOpen: false,
        animating: false,
        _isDragging: false,
        level: 'normal',
        editMode: false,
        editableElements: deepClone(this.cycle.elements),
      };
    },

    computed: {
      elements: function () { return this.editableElements; },
      typeColors: function () { return this.cycle.typeColors; },
      typeLabels: function () { return this.cycle.typeLabels; },

      selectedEl: function () {
        return this.editableElements.find(function (e) { return e.id === this.selectedId; }, this) || null;
      },
      selectedIdx: function () {
        return this.editableElements.findIndex(function (e) { return e.id === this.selectedId; }, this);
      },
      isMobile: function () { return window.innerWidth < 768; },

      wrapperStyle: function () {
        return {
          position: 'absolute', top: 0, left: 0,
          width: this.imgW + 'px', height: this.imgH + 'px',
          transform: 'translate(' + this.pan.x + 'px,' + this.pan.y + 'px) scale(' + this.zoom + ')',
          transformOrigin: '0 0',
          transition: this.animating ? 'transform .65s cubic-bezier(.4,0,.2,1)' : 'none',
          willChange: 'transform',
        };
      },

      panelStyle: function () {
        var open = this.panelOpen;
        return {
          position: 'fixed', top: 0, right: 0,
          width: PANEL_W + 'px', height: '100vh',
          background: '#0f172a',
          borderLeft: '1px solid #1e293b',
          display: 'flex', flexDirection: 'column',
          transition: 'transform .4s cubic-bezier(.4,0,.2,1)',
          transform: open ? 'translateX(0)' : 'translateX(' + (PANEL_W + 4) + 'px)',
          zIndex: 100,
          boxShadow: open ? '-12px 0 40px #00000066' : 'none',
        };
      },

      panelColor: function () {
        var el = this.selectedEl;
        return el ? this.typeColors[el.type] : '#94a3b8';
      },

      panelContent: function () {
        var el = this.selectedEl;
        if (!el) return '';
        var sections = this.level === 'normal' ? el.content.simple : el.content.sections;
        return renderSections(sections, this.panelColor);
      },

      legendEntries: function () {
        return Object.entries(this.typeColors).map(function (pair) {
          return { type: pair[0], color: pair[1], label: this.typeLabels[pair[0]] };
        }, this);
      },
    },

    mounted: function () {
      this.fitView();
      this._onResize = this.fitView.bind(this);
      window.addEventListener('resize', this._onResize);

      // Non-reactive drag state
      this._isDragging = false;
      this._hasMoved = false;
      this._lastMouse = { x: 0, y: 0 };
      this._lastDist = null;
      this._draggingHotspot = null; // { el, clientX, clientY, elX, elY }

      // Register wheel and touchmove as non-passive so preventDefault works
      this._wheelHandler = this.onWheel.bind(this);
      this._touchMoveHandler = this.onTouchMove.bind(this);
      this.$el.addEventListener('wheel', this._wheelHandler, { passive: false });
      this.$el.addEventListener('touchmove', this._touchMoveHandler, { passive: false });
    },

    beforeDestroy: function () {
      window.removeEventListener('resize', this._onResize);
      this.$el.removeEventListener('wheel', this._wheelHandler);
      this.$el.removeEventListener('touchmove', this._touchMoveHandler);
    },

    watch: {
      cycle: function (newCycle) {
        this.imgW = newCycle.imgW || 1688;
        this.imgH = newCycle.imgH || 1125;
        this.editableElements = deepClone(newCycle.elements);
        this.editMode = false;
        this.selectedId = null;
        this.panelOpen = false;
        this.level = 'normal';
        var self = this;
        this.$nextTick(function () { self.fitView(); });
      },
    },

    methods: {

      // ── Fit / zoom ───────────────────────────────────────────────────────

      onImgLoad: function (e) {
        var img = e.target;
        if (img.naturalWidth && img.naturalHeight) {
          this.imgW = img.naturalWidth;
          this.imgH = img.naturalHeight;
          this.fitView();
        }
      },

      fitView: function () {
        var vw = window.innerWidth, vh = window.innerHeight;
        var z = Math.min(vw / this.imgW, vh / this.imgH) * 0.97;
        this.zoom = z;
        this.pan = { x: (vw - this.imgW * z) / 2, y: (vh - this.imgH * z) / 2 };
      },

      zoomToElement: function (el) {
        var vw = window.innerWidth, vh = window.innerHeight;
        var mobile = this.isMobile;
        var availW = mobile ? vw : vw - PANEL_W;
        var availH = mobile ? vh * 0.3 : vh;
        var ix = (el.x / 100) * this.imgW;
        var iy = (el.y / 100) * this.imgH;
        var targetZoom = Math.max(1.6, Math.min(2.4, availW / (this.imgW * 0.55)));
        var cx = mobile ? vw / 2 : availW / 2;
        var cy = mobile ? availH / 2 : vh / 2;
        this.zoom = targetZoom;
        this.pan = { x: cx - ix * targetZoom, y: cy - iy * targetZoom };
        this.animating = true;
        var self = this;
        setTimeout(function () { self.animating = false; }, 700);
      },

      // ── Selection / panel ────────────────────────────────────────────────

      selectElement: function (el) {
        var isReselect = el.id === this.selectedId;
        this.selectedId = el.id;
        this.panelOpen = true;
        if (!isReselect) this.zoomToElement(el);
      },

      closePanel: function () {
        this.panelOpen = false;
        this.selectedId = null;
      },

      goNext: function () {
        var next = this.editableElements[(this.selectedIdx + 1) % this.editableElements.length];
        this.selectedId = next.id;
        this.zoomToElement(next);
      },

      goPrev: function () {
        var prev = this.editableElements[(this.selectedIdx - 1 + this.editableElements.length) % this.editableElements.length];
        this.selectedId = prev.id;
        this.zoomToElement(prev);
      },

      // ── Mouse / touch (pan & zoom) ───────────────────────────────────────

      onMouseDown: function (e) {
        if (e.target.closest && e.target.closest('.hs')) return;
        this._isDragging = true;
        this._hasMoved = false;
        this._lastMouse = { x: e.clientX, y: e.clientY };
      },

      onMouseMove: function (e) {
        if (!this._isDragging) return;
        var dx = e.clientX - this._lastMouse.x;
        var dy = e.clientY - this._lastMouse.y;
        if (Math.abs(dx) + Math.abs(dy) > 3) this._hasMoved = true;
        this._lastMouse = { x: e.clientX, y: e.clientY };
        this.pan = { x: this.pan.x + dx, y: this.pan.y + dy };
        this.animating = false;
      },

      onMouseUp: function () {
        this._isDragging = false;
      },

      onWheel: function (e) {
        e.preventDefault();
        var rect = this.$el.getBoundingClientRect();
        var mx = e.clientX - rect.left, my = e.clientY - rect.top;
        var factor = e.deltaY > 0 ? 0.9 : 1.11;
        var nz = Math.max(0.2, Math.min(6, this.zoom * factor));
        this.pan = {
          x: mx - (mx - this.pan.x) * (nz / this.zoom),
          y: my - (my - this.pan.y) * (nz / this.zoom),
        };
        this.zoom = nz;
        this.animating = false;
      },

      onTouchStart: function (e) {
        if (e.touches.length === 1) {
          this._isDragging = true;
          this._hasMoved = false;
          this._lastMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
        } else if (e.touches.length === 2) {
          this._isDragging = false;
          var dx = e.touches[0].clientX - e.touches[1].clientX;
          var dy = e.touches[0].clientY - e.touches[1].clientY;
          this._lastDist = Math.hypot(dx, dy);
        }
      },

      onTouchMove: function (e) {
        e.preventDefault();
        if (e.touches.length === 1 && this._isDragging) {
          var dx = e.touches[0].clientX - this._lastMouse.x;
          var dy = e.touches[0].clientY - this._lastMouse.y;
          if (Math.abs(dx) + Math.abs(dy) > 4) this._hasMoved = true;
          this._lastMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
          this.pan = { x: this.pan.x + dx, y: this.pan.y + dy };
          this.animating = false;
        } else if (e.touches.length === 2 && this._lastDist) {
          var dx2 = e.touches[0].clientX - e.touches[1].clientX;
          var dy2 = e.touches[0].clientY - e.touches[1].clientY;
          var dist = Math.hypot(dx2, dy2);
          var mx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
          var my = (e.touches[0].clientY + e.touches[1].clientY) / 2;
          var factor = dist / this._lastDist;
          this._lastDist = dist;
          var nz = Math.max(0.2, Math.min(6, this.zoom * factor));
          this.pan = {
            x: mx - (mx - this.pan.x) * (nz / this.zoom),
            y: my - (my - this.pan.y) * (nz / this.zoom),
          };
          this.zoom = nz;
          this.animating = false;
        }
      },

      onTouchEnd: function () {
        this._isDragging = false;
        this._lastDist = null;
      },

      // ── Hotspot styles ───────────────────────────────────────────────────

      hotspotStyle: function (el) {
        var color = this.typeColors[el.type];
        var isRes = el.kind === 'reservoir';
        var dotSize = isRes ? 26 : 19;
        var ringSize = dotSize * 2.2;
        return {
          position: 'absolute',
          left: el.x + '%', top: el.y + '%',
          transform: 'translate(-50%,-50%)',
          cursor: this.editMode ? 'move' : 'pointer',
          zIndex: this.selectedId === el.id ? 30 : 10,
          width: Math.max(ringSize * 2, 48) + 'px',
          height: Math.max(ringSize * 2, 48) + 'px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexDirection: 'column',
          userSelect: 'none',
        };
      },

      ring1Style: function (el) {
        var color = this.typeColors[el.type];
        var isRes = el.kind === 'reservoir';
        var dotSize = isRes ? 26 : 19;
        var ringSize = dotSize * 2.2;
        return {
          position: 'absolute', left: '50%', top: '50%',
          width: ringSize + 'px', height: ringSize + 'px',
          borderRadius: '50%',
          border: this.editMode ? '2px dashed ' + color : '2px solid ' + color,
          animation: this.editMode ? 'none' : 'pulse 2.2s ease-out infinite',
          animationDelay: (el.id.length * 0.13) + 's',
          opacity: this.editMode ? 0.5 : 1,
        };
      },

      ring2Style: function (el) {
        var color = this.typeColors[el.type];
        var isRes = el.kind === 'reservoir';
        var dotSize = isRes ? 26 : 19;
        var ringSize = dotSize * 2.2;
        return {
          position: 'absolute', left: '50%', top: '50%',
          width: (ringSize * 0.75) + 'px', height: (ringSize * 0.75) + 'px',
          borderRadius: '50%',
          border: '1.5px solid ' + color,
          animation: this.editMode ? 'none' : 'pulse2 2.2s ease-out infinite',
          animationDelay: (el.id.length * 0.13 + 0.5) + 's',
          display: this.editMode ? 'none' : 'block',
        };
      },

      dotStyle: function (el) {
        var color = this.typeColors[el.type];
        var isRes = el.kind === 'reservoir';
        var dotSize = isRes ? 26 : 19;
        var sel = this.selectedId === el.id;
        var isDragging = this._draggingHotspot && this._draggingHotspot.el === el;
        return {
          position: 'relative', zIndex: 2,
          width: dotSize + 'px', height: dotSize + 'px',
          borderRadius: '50%',
          background: (sel || isDragging) ? color : color + 'cc',
          boxShadow: this.editMode
            ? '0 0 0 2px #fff4, 0 0 8px ' + color
            : (sel ? '0 0 0 3px ' + color + '55, 0 0 14px ' + color + '88' : '0 0 6px ' + color + '66'),
          transition: 'all .15s',
          border: (sel || this.editMode) ? '2px solid #fff' : '1.5px solid ' + color,
        };
      },

      coordBadgeStyle: function () {
        return {
          position: 'absolute',
          bottom: '-22px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#0f172aee',
          border: '1px solid #334155',
          borderRadius: '4px',
          padding: '2px 6px',
          fontSize: '10px',
          fontFamily: 'monospace',
          color: '#94a3b8',
          whiteSpace: 'nowrap',
          pointerEvents: 'none',
          zIndex: 5,
        };
      },

      // ── Edit mode ────────────────────────────────────────────────────────

      toggleEditMode: function () {
        this.editMode = !this.editMode;
        if (this.editMode) this.closePanel();
      },

      onHotspotPointerDown: function (el, e) {
        if (!this.editMode) return;
        e.stopPropagation();
        e.currentTarget.setPointerCapture(e.pointerId);
        this._draggingHotspot = { el: el, clientX: e.clientX, clientY: e.clientY, elX: el.x, elY: el.y };
      },

      onHotspotPointerMove: function (el, e) {
        if (!this._draggingHotspot || this._draggingHotspot.el !== el) return;
        e.stopPropagation();
        var dx = (e.clientX - this._draggingHotspot.clientX) / this.zoom;
        var dy = (e.clientY - this._draggingHotspot.clientY) / this.zoom;
        var newX = this._draggingHotspot.elX + (dx / this.imgW) * 100;
        var newY = this._draggingHotspot.elY + (dy / this.imgH) * 100;
        el.x = Math.round(Math.max(0, Math.min(100, newX)) * 10) / 10;
        el.y = Math.round(Math.max(0, Math.min(100, newY)) * 10) / 10;
      },

      onHotspotPointerUp: function (e) {
        if (!this._draggingHotspot) return;
        e.stopPropagation();
        this._draggingHotspot = null;
      },

      onHotspotClick: function (el, e) {
        if (this.editMode) return;
        e.stopPropagation();
        this.selectElement(el);
      },

      exportData: function () {
        var allCycles = window.BGQ_CYCLES;
        if (!allCycles) {
          alert('window.BGQ_CYCLES no encontrado');
          return;
        }
        var updated = {};
        var self = this;
        Object.keys(allCycles).forEach(function (id) {
          if (id === self.cycle.id) {
            updated[id] = Object.assign({}, allCycles[id], { elements: self.editableElements });
          } else {
            updated[id] = allCycles[id];
          }
        });
        var js = [
          '// Ciclos biogeoquímicos — datos completos con hotspots incluidos\n',
          '// Cargado como <script> regular; expone window.BGQ_CYCLES\n\n',
          'const CYCLES = ',
          JSON.stringify(updated, null, 2),
          ';\n\nwindow.BGQ_CYCLES = CYCLES;\n',
        ].join('');
        var blob = new Blob([js], { type: 'text/javascript' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url; a.download = 'data.js'; a.click();
        URL.revokeObjectURL(url);
      },

      resetCoords: function () {
        this.editableElements = deepClone(this.cycle.elements);
      },
    },

    template: `
<div
  style="position:fixed;inset:0;overflow:hidden;background:#0b0f1c;touch-action:none;"
  :style="{cursor: (typeof _isDragging === 'Boolean') && _isDragging ? 'grabbing' : 'grab'}"
  @mousedown="onMouseDown"
  @mousemove="onMouseMove"
  @mouseup="onMouseUp"
  @mouseleave="onMouseUp"
  @touchstart="onTouchStart"
  @touchend="onTouchEnd"
>
  <!-- Edit mode banner -->
  <div v-if="editMode" style="position:fixed;top:0;left:0;right:0;height:3px;z-index:200;background:linear-gradient(90deg,#f59e0b,#ef4444,#f59e0b);background-size:200%;animation:editBanner 2s linear infinite;"></div>

  <!-- Zoom/pan wrapper -->
  <div :style="wrapperStyle" ref="wrapper">
    <img
      class="map-img"
      :src="cycle.image"
      :width="imgW"
      :height="imgH"
      draggable="false"
      @load="onImgLoad"
      :alt="'Diagrama del ' + cycle.title"
    />
    <!-- Hotspots -->
    <div
      v-for="el in editableElements"
      :key="el.id"
      class="hs"
      :style="hotspotStyle(el)"
      @click="onHotspotClick(el, $event)"
      @pointerdown="onHotspotPointerDown(el, $event)"
      @pointermove="onHotspotPointerMove(el, $event)"
      @pointerup="onHotspotPointerUp($event)"
      @pointercancel="onHotspotPointerUp($event)"
    >
      <div :style="ring1Style(el)"></div>
      <div :style="ring2Style(el)"></div>
      <div :style="dotStyle(el)"></div>
      <!-- Coordinate badge (edit mode only) -->
      <div v-if="editMode" :style="coordBadgeStyle()">
        x:{{ el.x.toFixed(1) }} y:{{ el.y.toFixed(1) }}
      </div>
    </div>
  </div>

  <!-- Header -->
  <div style="position:fixed;top:0;left:0;right:0;z-index:50;pointer-events:none;padding:14px 20px;display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
    <!-- Left: title + back -->
    <div style="background:#0f172acc;backdrop-filter:blur(12px);border:1px solid #1e293b;border-radius:10px;padding:8px 16px;pointer-events:auto;display:flex;align-items:center;gap:12px;flex-shrink:0;">
      <button
        @click="$emit('back')"
        style="background:none;border:none;cursor:pointer;color:#475569;font-size:.85em;font-family:inherit;padding:0;transition:color .2s;"
        onmouseenter="this.style.color='#f1f5f9'"
        onmouseleave="this.style.color='#475569'"
      >← Ciclos</button>
      <div style="width:1px;height:16px;background:#1e293b;"></div>
      <div>
        <div style="font-size:.68em;letter-spacing:.1em;text-transform:uppercase;color:#4a5568;margin-bottom:2px;">Biogeoquímica</div>
        <div style="font-size:1.05em;font-weight:700;color:#e2e8f0;letter-spacing:-.01em;">{{ cycle.title }}</div>
      </div>
    </div>

    <!-- Center: edit mode toolbar -->
    <div style="display:flex;align-items:center;gap:8px;pointer-events:auto;flex:1;justify-content:center;">
      <button
        @click="toggleEditMode"
        :style="{
          background: editMode ? '#f59e0b22' : '#0f172acc',
          border: editMode ? '1px solid #f59e0b88' : '1px solid #1e293b',
          borderRadius: '8px', padding: '6px 14px',
          color: editMode ? '#fbbf24' : '#64748b',
          fontFamily: 'inherit', fontWeight: 600, fontSize: '.8em',
          cursor: 'pointer', transition: 'all .2s',
          backdropFilter: 'blur(12px)',
        }"
      >{{ editMode ? '✓ Fin editar' : '✎ Editar hotspots' }}</button>
      <template v-if="editMode">
        <button
          @click="exportData"
          style="background:#0f172acc;backdrop-filter:blur(12px);border:1px solid #22d3ee44;border-radius:8px;padding:6px 14px;color:#22d3ee;font-family:inherit;font-weight:600;font-size:.8em;cursor:pointer;transition:all .2s;"
          onmouseenter="this.style.borderColor='#22d3ee88';this.style.background='#22d3ee11'"
          onmouseleave="this.style.borderColor='#22d3ee44';this.style.background='#0f172acc'"
        >↓ Exportar data.js</button>
        <button
          @click="resetCoords"
          style="background:#0f172acc;backdrop-filter:blur(12px);border:1px solid #47556944;border-radius:8px;padding:6px 14px;color:#64748b;font-family:inherit;font-weight:600;font-size:.8em;cursor:pointer;transition:all .2s;"
          onmouseenter="this.style.color='#94a3b8'"
          onmouseleave="this.style.color='#64748b'"
        >↺ Resetear</button>
      </template>
    </div>

    <!-- Right: legend -->
    <div style="background:#0f172acc;backdrop-filter:blur(12px);border:1px solid #1e293b;border-radius:10px;padding:8px 12px;pointer-events:auto;display:flex;flex-direction:column;gap:5px;flex-shrink:0;">
      <div v-for="e in legendEntries" :key="e.type" style="display:flex;align-items:center;gap:7px;font-size:.72em;color:#94a3b8;">
        <div :style="{width:'8px',height:'8px',borderRadius:'50%',background:e.color,boxShadow:'0 0 6px '+e.color}"></div>
        {{ e.label }}
      </div>
    </div>
  </div>

  <!-- Side panel -->
  <div
    :class="['side-panel', panelOpen ? '' : 'closed']"
    :style="panelStyle"
    @wheel.stop
    @touchstart.stop
    @touchmove.stop
    @touchend.stop
  >
    <div :style="{height:'3px',background: selectedEl ? 'linear-gradient(90deg,'+panelColor+',transparent)' : '#1e293b',flexShrink:0}"></div>
    <div style="padding:18px 20px 14px;border-bottom:1px solid #1e293b;flex-shrink:0;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div style="flex:1;min-width:0;">
          <div v-if="selectedEl"
            :style="{display:'inline-block',fontSize:'.68em',fontWeight:600,letterSpacing:'.07em',textTransform:'uppercase',color:panelColor,background:panelColor+'18',border:'1px solid '+panelColor+'44',borderRadius:'4px',padding:'2px 8px',marginBottom:'8px'}"
          >{{ typeLabels[selectedEl.type] }}</div>
          <h2 :style="{fontSize: selectedEl && selectedEl.label.length > 20 ? '1.15em' : '1.35em',fontWeight:700,lineHeight:1.25,color:'#f8fafc',letterSpacing:'-.01em'}">
            {{ selectedEl ? selectedEl.label : 'Selecciona un elemento' }}
          </h2>
          <div v-if="selectedEl && selectedEl.content.stock" style="font-size:.8em;color:#64748b;margin-top:5px;font-variant-numeric:tabular-nums;">
            {{ selectedEl.content.stock }}
          </div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex-shrink:0;margin-left:8px;">
          <button @click="closePanel" style="background:none;border:none;cursor:pointer;color:#475569;font-size:1.4em;line-height:1;padding:2px 4px;transition:color .2s;"
            onmouseenter="this.style.color='#f1f5f9'"
            onmouseleave="this.style.color='#475569'"
          >×</button>
          <div style="display:flex;align-items:center;gap:0;background:#1e293b;border-radius:8px;padding:2px;border:1px solid #334155;">
            <button v-for="l in ['normal','avanzado']" :key="l" @click="level = l"
              :style="{background: level===l ? '#334155' : 'transparent',border:'none',borderRadius:'6px',color: level===l ? '#f1f5f9' : '#475569',padding:'4px 10px',fontSize:'.72em',fontWeight:600,cursor:'pointer',fontFamily:'inherit',textTransform:'capitalize',transition:'all .2s'}"
            >{{ l.charAt(0).toUpperCase() + l.slice(1) }}</button>
          </div>
        </div>
      </div>
    </div>
    <div class="panel-body" style="flex:1;overflow-y:auto;padding:16px 20px 8px;">
      <div v-if="selectedEl" v-html="panelContent"></div>
      <p v-else style="color:#475569;font-style:italic;font-family:'Lora',serif;">
        Haz clic sobre cualquier punto brillante del diagrama para explorar ese reservorio o flujo del ciclo.
      </p>
    </div>
    <div style="border-top:1px solid #1e293b;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;">
      <button @click="goPrev" :disabled="!selectedEl" class="nav-btn"
        :style="{background:'#1e293b',border:'none',borderRadius:'8px',color: selectedEl ? '#94a3b8' : '#2d3748',cursor: selectedEl ? 'pointer' : 'default',padding:'8px 14px',fontSize:'.82em',fontWeight:500,fontFamily:'inherit',transition:'all .2s'}"
      >‹ Anterior</button>
      <span style="font-size:.78em;color:#334155;font-variant-numeric:tabular-nums;">
        {{ selectedEl ? (selectedIdx + 1) + ' / ' + editableElements.length : '– / ' + editableElements.length }}
      </span>
      <button @click="goNext" :disabled="!selectedEl" class="nav-btn"
        :style="{background:'#1e293b',border:'none',borderRadius:'8px',color: selectedEl ? '#94a3b8' : '#2d3748',cursor: selectedEl ? 'pointer' : 'default',padding:'8px 14px',fontSize:'.82em',fontWeight:500,fontFamily:'inherit',transition:'all .2s'}"
      >Siguiente ›</button>
    </div>
  </div>

  <!-- Mobile bottom toggle -->
  <button
    v-if="selectedEl && !panelOpen && !editMode"
    @click="panelOpen = true"
    :style="{position:'fixed',bottom:'20px',right:'20px',zIndex:90,background:'#0f172a',border:'1px solid '+panelColor+'66',borderRadius:'24px',padding:'10px 18px',color:'#f1f5f9',fontFamily:'inherit',fontWeight:600,fontSize:'.85em',cursor:'pointer',boxShadow:'0 4px 20px #00000088, 0 0 16px '+panelColor+'33'}"
  >Ver: {{ selectedEl.label }}</button>

  <!-- Hint -->
  <div v-if="!editMode" style="position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:#0f172aaa;backdrop-filter:blur(8px);border:1px solid #1e293b;border-radius:20px;padding:5px 14px;font-size:.72em;color:#475569;pointer-events:none;white-space:nowrap;z-index:40;">
    Rueda para zoom · Arrastra para mover · Clic en los puntos para explorar
  </div>
  <div v-else style="position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:#f59e0b18;backdrop-filter:blur(8px);border:1px solid #f59e0b44;border-radius:20px;padding:5px 14px;font-size:.72em;color:#fbbf24;pointer-events:none;white-space:nowrap;z-index:40;">
    Modo edición — arrastra los puntos para reposicionarlos
  </div>
</div>
  `,
  };

})();
