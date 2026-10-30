// plotkit.js: dynamic SVG line plots in the plotkit style (page colour, hairline axes, left bold
// title, categorical colours with a dash cue). `plotkit.style` is appended by plotkit.web.export().
//
//   plotkit.line(el, {xlabel, ylabel, title, series: [{label, x, y}], legendTitle,
//                     xlim, ylim, vlines: [{x, label}], hlines: [{y, label}],
//                     points: [{x, y, label, side: 1|-1, dy}]})
const plotkit = (() => {
  const NS = "http://www.w3.org/2000/svg";

  function ticks(lo, hi, n = 5) {
    const raw = (hi - lo) / n, mag = 10 ** Math.floor(Math.log10(raw)), f = raw / mag;
    const step = (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * mag, out = [];
    for (let v = Math.ceil(lo / step - 1e-9) * step; v <= hi + step * 1e-9; v += step) out.push(+v.toPrecision(12));
    return out;
  }

  // "Time (days)" -> "TIME (days)": uppercase the name, never the unit
  const caption = (t, upper) => {
    const [name, ...unit] = t.split(" (");
    return (upper ? name.toUpperCase() : name) + (unit.length ? " (" + unit.join(" (") : "");
  };

  function line(el, spec) {
    const st = plotkit.style, k = Math.min(2.2, Math.max(1.6, el.clientWidth / 518));
    const W = el.clientWidth || 518, H = W / 1.6;
    const lab = st.fontsize * k, tick = st.tick * k, ttl = st.title_size * k, hair = st.hairline * k;
    const series = spec.series;
    const L = 5 * lab, B = 4 * lab, T = ttl * 2.4, R = series.length > 1 ? 11 * lab : lab;
    const w = W - L - R, h = H - T - B;
    const all = (key) => series.flatMap((s) => s[key]);
    const [x0, x1] = spec.xlim ?? [Math.min(...all("x")), Math.max(...all("x"))];
    const [y0, y1] = spec.ylim ?? [Math.min(...all("y")), Math.max(...all("y"))];
    const X = (v) => L + ((v - x0) / (x1 - x0)) * w, Y = (v) => T + h - ((v - y0) / (y1 - y0)) * h;

    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", spec.title);
    svg.style.cssText = `display:block;width:100%;height:auto;font-family:${st.font}`;
    const add = (tag, attrs, text, parent = svg) => {
      const n = document.createElementNS(NS, tag);
      for (const [a, v] of Object.entries(attrs)) n.setAttribute(a, v);
      if (text !== undefined) n.textContent = text;
      parent.append(n);
      return n;
    };
    const txt = (x, y, s, size, fill, extra = {}) => add("text", { x, y, "font-size": size, fill, ...extra }, s);
    const halo = { "paint-order": "stroke", stroke: st.bg, "stroke-width": 3 * k, "stroke-linejoin": "round" };

    add("rect", { width: W, height: H, fill: st.bg });
    const clip = "clip" + Math.random().toString(36).slice(2);
    add("rect", { x: L, y: T, width: w, height: h }, undefined, add("clipPath", { id: clip }));

    // axes: left and bottom hairlines, outward ticks, muted tick labels
    add("path", { d: `M${L},${T}V${T + h}H${L + w}`, fill: "none", stroke: st.fg, "stroke-width": hair });
    const tl = st.tick_length * k, pad = st.tick_pad * k;
    for (const v of ticks(x0, x1)) {
      add("path", { d: `M${X(v)},${T + h}v${tl}`, stroke: st.fg, "stroke-width": hair });
      txt(X(v), T + h + tl + pad + tick * 0.8, v, tick, st.muted, { "text-anchor": "middle" });
    }
    for (const v of ticks(y0, y1)) {
      add("path", { d: `M${L},${Y(v)}h${-tl}`, stroke: st.fg, "stroke-width": hair });
      txt(L - tl - pad, Y(v) + tick * 0.35, v, tick, st.muted, { "text-anchor": "end" });
    }
    txt(L + w / 2, H - lab * 0.6, caption(spec.xlabel, st.upper_labels), lab, st.fg, { "text-anchor": "middle" });
    txt(0, 0, caption(spec.ylabel, st.upper_labels), lab, st.fg, {
      "text-anchor": "middle",
      transform: `translate(${lab * 1.2},${T + h / 2}) rotate(-90)`,
    });
    txt(L, ttl * 1.3, spec.title, ttl, st.fg, { "font-weight": "bold" });

    // annotations sit under the data so the curves stay on top
    const note = add("g", { "clip-path": `url(#${clip})` });
    const dash = { stroke: st.muted, "stroke-width": hair, "stroke-dasharray": `${4 * k} ${3 * k}` };
    for (const m of spec.vlines ?? []) {
      add("path", { d: `M${X(m.x)},${T}V${T + h}`, ...dash }, undefined, note);
      txt(X(m.x) + 4 * k, T + tick * 1.2, m.label, tick, st.muted, halo).setAttribute("clip-path", "none");
    }
    for (const m of spec.hlines ?? []) {
      add("path", { d: `M${L},${Y(m.y)}H${L + w}`, ...dash }, undefined, note);
      txt(L + w - 4 * k, Y(m.y) - 4 * k, m.label, tick, st.muted, { ...halo, "text-anchor": "end" });
    }

    series.forEach((s, i) => {
      const d = s.x.map((x, j) => `${j ? "L" : "M"}${X(x).toFixed(1)},${Y(s.y[j]).toFixed(1)}`).join("");
      const dashes = st.dashes[i % st.dashes.length].map((u) => u * st.data_lw * k).join(" ");
      add("path", {
        d, fill: "none", stroke: st.categorical[i % st.categorical.length], "stroke-width": st.data_lw * k,
        "stroke-dasharray": dashes, "stroke-linejoin": "round", "clip-path": `url(#${clip})`,
      });
    });

    for (const p of spec.points ?? []) {
      add("circle", { cx: X(p.x), cy: Y(p.y), r: 2.6 * k, fill: st.fg, stroke: st.bg, "stroke-width": k });
      const side = p.side ?? 1; // 1: label right of the point, -1: left
      txt(X(p.x) + side * 6 * k, Y(p.y) + (p.dy ?? -5) * k, p.label, tick, st.fg, {
        ...halo, "text-anchor": side > 0 ? "start" : "end",
      });
    }

    if (series.length > 1) {
      const lx = L + w + lab, ly = T + lab;
      if (spec.legendTitle) txt(lx, ly, caption(spec.legendTitle, st.upper_labels), lab, st.fg);
      series.forEach((s, i) => {
        const y = ly + lab * 1.6 * (i + (spec.legendTitle ? 1 : 0.4));
        add("path", {
          d: `M${lx},${y}h${2 * lab}`, stroke: st.categorical[i % st.categorical.length],
          "stroke-width": st.data_lw * k, "stroke-dasharray": st.dashes[i % st.dashes.length].map((u) => u * st.data_lw * k).join(" "),
        });
        txt(lx + 2.6 * lab, y + tick * 0.35, s.label, tick, st.fg);
      });
    }
    el.replaceChildren(svg);
  }

  return { line, style: null };
})();
