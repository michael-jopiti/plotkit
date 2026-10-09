# plotkit source layout

How the library is built. Arrows read "depends on" (imports).

```mermaid
graph TD
    user([user code]) --> init["__init__.py<br/>public exports"]
    init --> api["api.py<br/>bar, line, scatter, ... grid"]
    init --> synthetic["synthetic.py<br/>demo data"]

    api --> plots
    api --> themes

    subgraph plots["plots/"]
        pregistry["registry.py<br/>register_plot, plots"]
        pbase["base.py<br/>BasePlot, PlotResult"]
        kinds["bar, boxplot, continuous, dim_red,<br/>heatmap, line, scatter, survival, volcano"]
        pgrid["grid.py<br/>render_grid, Panel, GridResult"]
        kinds --> pbase
        kinds --> pregistry
        pgrid --> pbase
        pgrid --> pregistry
        pregistry --> pbase
    end

    subgraph themes["themes/"]
        tstyled["styled.py<br/>Variant, get_variant"]
        tpub["publication.py<br/>PublicationTheme"]
        tproportions["proportions.py"]
        tregistry["registry.py"]
        tvariants["variants.py<br/>built-in styles"]
        tcontext["context.py<br/>apply, reset"]
        tvariants --> tstyled
        tstyled --> tpub
        tstyled --> tregistry
        tpub --> tproportions
        tcontext --> tregistry
    end

    subgraph palettes["palettes/"]
        paregistry["registry.py"]
        pakinds["categorical, continuous, discrete"]
        pabase["base.py<br/>Palette"]
        paregistry --> pakinds
        pakinds --> pabase
    end

    subgraph components["components/"]
        comps["axes, colorbar, legend, marginals,<br/>title, size, layout"]
    end

    data["data/adapter.py<br/>DataAdapter, Normalized<br/>(only module touching polars)"]
    io["io/export.py<br/>save_figure"]
    registry["registry.py<br/>generic Registry + entry points"]
    exceptions["exceptions.py<br/>PlotkitError family"]

    kinds --> data
    pbase --> components
    pbase --> io
    pbase --> tstyled
    pgrid --> tstyled
    tpub --> pakinds
    tstyled --> paregistry
    pregistry --> registry
    tregistry --> registry
    paregistry --> registry
    registry --> exceptions
    data --> exceptions
    pakinds --> exceptions
    tpub --> exceptions
```

## Render pipeline

Every plot is a `BasePlot` subclass. `render()` runs the template inside `matplotlib.rc_context`, so plotkit never changes matplotlib global state.

```mermaid
sequenceDiagram
    participant U as user
    participant A as api.py
    participant R as plots registry
    participant P as BasePlot subclass
    participant T as Variant / Theme
    U->>A: plotkit.line(x, y, title, data)
    A->>R: look up "line"
    R-->>A: plot class
    A->>P: build with options
    P->>T: get_variant(style)
    P->>P: rc_context(theme rc params)
    P->>P: prepare_data (DataAdapter)
    P->>P: draw
    P->>P: style_axes, style_legend, finalize
    P-->>U: PlotResult (fig, ax, save)
```

## Rules of the layout

- `data/adapter.py` is the only module that touches polars. Everything else takes pandas.
- Importing plotkit never mutates matplotlib global state. Styling goes through `rc_context`.
- `registry.py` is the one generic `Registry`. Palettes, themes and plots each own an instance. Unknown names fall back to entry points.
- Extension = one new file plus one `register_*` call (`register_palette`, `register_theme`, `register_variant`, `register_plot`).
- All errors derive from `PlotkitError` (`exceptions.py`).
