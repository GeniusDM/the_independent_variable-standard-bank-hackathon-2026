"""Document builders for scripts/build_submission.py — one-pager and deck."""

from __future__ import annotations

from pathlib import Path

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED = "#0b0b0b", "#52514e"

TEAM = "The Independent Variable"
MEMBERS = "Daniel Mataranyika · Herton Mabongue"


def zar(v: float) -> str:
    v = float(v)
    if abs(v) >= 1e12:
        return f"R{v / 1e12:.2f}tn"
    if abs(v) >= 1e9:
        return f"R{v / 1e9:.2f}bn"
    if abs(v) >= 1e6:
        return f"R{v / 1e6:,.0f}M"
    return f"R{v:,.0f}"


# --------------------------------------------------------------------------
# one-pager
# --------------------------------------------------------------------------

def build_onepager(docs: Path, figs: dict, f: dict, old_shares) -> Path:
    rows = "\n".join(
        f"<tr><td>{int(r['rank'])}</td><td><b>{r['client_name']}</b></td>"
        f"<td>{r['sector_display']}</td>"
        f"<td class='n'>{r['syn_share'] * 100:.1f}%</td>"
        f"<td class='n'>R{r['revenue_opportunity'] / 1e6:,.0f}M</td>"
        f"<td>{r['top_pillar']}</td></tr>"
        for _, r in f["top"].iterrows()
    )

    old_spread = (old_shares.max() - old_shares.min()) * 100
    new_spread = (f["share_max"] - f["share_min"]) * 100

    html = f"""<!doctype html>
<meta charset="utf-8">
<title>Share of Wallet Intelligence Engine — {TEAM}</title>
<style>
  /* Tuned so the whole summary lands on exactly one A4 page, as the brief
     requires. Check the page count after any copy change. */
  @page {{ size: A4; margin: 9mm 11mm; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Segoe UI", system-ui, sans-serif;
    color: {INK}; margin: 0; font-size: 8.3pt; line-height: 1.36;
  }}
  h1 {{ font-size: 15pt; margin: 0 0 1mm; letter-spacing: -0.2pt; }}
  h2 {{
    font-size: 8.2pt; text-transform: uppercase; letter-spacing: 0.8pt;
    color: {BLUE}; margin: 0 0 1.4mm; font-weight: 700;
  }}
  p {{ margin: 0 0 2mm; }}
  .sub {{ color: {MUTED}; font-size: 8.6pt; margin-bottom: 3mm; }}
  header {{ border-bottom: 1.6pt solid {BLUE}; padding-bottom: 2mm; margin-bottom: 3mm; }}
  .cols {{ display: grid; grid-template-columns: 1.05fr 1fr; gap: 5mm; }}
  section {{ margin-bottom: 3.4mm; }}
  .kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 2mm; margin-bottom: 3mm; }}
  .kpi {{ border: 0.7pt solid #dcdcd8; border-radius: 1.6mm; padding: 1.8mm 2mm; }}
  .kpi .v {{ font-size: 13pt; font-weight: 700; color: {BLUE}; letter-spacing: -0.3pt; }}
  .kpi .l {{ font-size: 6.6pt; text-transform: uppercase; letter-spacing: 0.5pt; color: {MUTED}; }}
  .kpi.accent .v {{ color: {ORANGE}; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 7.6pt; }}
  th {{
    text-align: left; font-size: 6.6pt; text-transform: uppercase; letter-spacing: 0.5pt;
    color: {MUTED}; border-bottom: 0.7pt solid #dcdcd8; padding: 1mm 1.2mm;
  }}
  td {{ padding: 1mm 1.2mm; border-bottom: 0.5pt solid #efefec; }}
  td.n {{ text-align: right; font-variant-numeric: tabular-nums; }}
  img {{ width: 100%; display: block; }}
  .eq {{
    font-family: Consolas, monospace; font-size: 7.4pt; background: #f6f6f4;
    border-left: 1.6pt solid {BLUE}; padding: 1.4mm 2mm; margin: 1.4mm 0;
  }}
  ol, ul {{ margin: 0 0 2mm; padding-left: 4mm; }}
  li {{ margin-bottom: 0.7mm; }}
  .foot {{ border-top: 0.7pt solid #dcdcd8; padding-top: 1.6mm; margin-top: 1mm;
           color: {MUTED}; font-size: 7pt; }}
  b.hl {{ color: {ORANGE}; }}
</style>

<header>
  <h1>Share of Wallet Intelligence Engine — Syn Bank</h1>
  <div class="sub"><b>Team {TEAM}</b> · {MEMBERS} · Standard Bank × Data School Hackathon 2026</div>
</header>

<div class="kpis">
  <div class="kpi"><div class="v">{f['share'] * 100:.1f}%</div><div class="l">Syn Bank share</div></div>
  <div class="kpi"><div class="v">{zar(f['addressable'])}</div><div class="l">Addressable flow</div></div>
  <div class="kpi accent"><div class="v">{zar(f['gap'])}</div><div class="l">Uncaptured gap</div></div>
  <div class="kpi accent"><div class="v">{zar(f['oppty'])}</div><div class="l">Fee opportunity / yr</div></div>
</div>

<div class="cols">
  <div>
    <section>
      <h2>The problem, and the trap in it</h2>
      <p>Syn Bank sees every transaction that flows through Syn Bank — and none of the
      ones that flow through its competitors. Share of wallet therefore cannot be read
      off the internal data; it must be estimated from outside.</p>
      <p>Our first model missed this. It sized the wallet from internal flow, then took
      captured volume as a fraction of that wallet:</p>
      <div class="eq">share = (wallet × capture_ratio) / wallet = capture_ratio</div>
      <p>The wallet term cancels. Share was identical to the assumed capture rate and
      could not depend on the data. It passed every obvious check — values between 0
      and 1, a plausible ranking — while giving <b>{len(old_shares)} very different companies
      the same answer</b>: {old_spread:.1f} points of spread across a portfolio whose
      wallets differ by {f['size_ratio']:,.0f}×.</p>
      <img src="figures/before_after.png" alt="Share distribution, original versus two-sided model">
    </section>

    <section>
      <h2>The two-sided model</h2>
      <p>The two sides of the ratio are now computed from independent sources.</p>
      <div class="eq">share = captured flow (measured) / addressable flow (estimated)</div>
      <ul>
        <li><b>Top-down</b> — addressable flow sized from each client's published FY2025
        statements: revenue drives transactional, foreign revenue drives FX, cost of
        sales plus inventory drives trade finance. Each scaled by an explicit
        SA-attribution share, since Syn Bank is a South African bank.</li>
        <li><b>Bottom-up</b> — captured flow summed over the trailing 12 months of the
        internal datasets. No assumption enters this side.</li>
      </ul>
      <p>Share now spans <b>{f['share_min'] * 100:.1f}% to {f['share_max'] * 100:.1f}%</b>
      ({new_spread:.1f} points). Every external figure is cited per client in
      <code>data/external/company_financials.csv</code>.</p>
    </section>

    <section>
      <h2>Generative AI, doing real work</h2>
      <p>The model never supplies a number. Figures are computed by the engine, passed in
      as an evidence block, and reused verbatim — the model does language, not arithmetic.
      Every output is then re-read by a grounding check that flags any rand amount or
      percentage absent from the evidence. It writes pre-meeting briefings and answers
      open questions over the portfolio, and degrades to deterministic text if the API is
      unavailable, so a demo never breaks. Prompts and outputs: <code>prompts/logs/</code>.</p>
    </section>
  </div>

  <div>
    <section>
      <h2>What a coverage banker does with it</h2>
      <table>
        <tr><th>#</th><th>Client</th><th>Sector</th><th class="n">Share</th>
            <th class="n">Fee oppty/yr</th><th>Lead with</th></tr>
        {rows}
      </table>
      <p style="margin-top:1.6mm">Ranking blends gap size (50%) with ease of conversion,
      relationship depth and 90-day urgency, so the list is ordered by winnable value
      rather than client size. <b class="hl">{f['lead_pillar']} banking is the lead pillar for
      {f['lead_pillar_n']} of {f['clients']} clients</b> — cash-management consolidation is the
      repeatable conversation.</p>
      <img src="figures/opportunity.png" alt="Top opportunities by annual fee revenue">
    </section>
    </section>

    <section>
      <h2>How much do the assumptions matter?</h2>
      <p>Shifting every flow multiple by ±25% moves the <b>portfolio-wide average</b> share
      only between <b>{f['sens_min'] * 100:.1f}% and {f['sens_max'] * 100:.1f}%</b> (not the
      {f['share_min'] * 100:.1f}%–{f['share_max'] * 100:.1f}% per-client range above); the
      captured side cannot move, because it is measured. Our multiples imply banking fees of
      ~0.47% of revenue, inside the 0.4–0.7% range the brief itself cites.</p>
    </section>

    <section>
      <h2>Limitations</h2>
      <p>20 clients supplied, not the 50 described. Flow multiples are benchmarks, not
      observations, and SA-attribution is the most judgmental input. Revenue basis differs
      by industry and is recorded per client; cost of sales and inventory are imputed from
      sector margins where not disclosed, and flagged. Gaps are attributed to competitors,
      assuming internal records are complete. Lending and DCM are out of scope.</p>
    </section>
  </div>
</div>

<div class="foot">
  Public financial statements are used only to size an addressable benchmark. No synthetic
  record is linked to a real entity or event, and Syn Bank is treated throughout as
  fictional. Full method and citations: <code>docs/methodology.md</code>.
</div>
"""
    path = docs / "executive_summary.html"
    path.write_text(html, encoding="utf-8")
    print(f"  one-pager -> {path.name}")
    return path


# --------------------------------------------------------------------------
# deck
# --------------------------------------------------------------------------

def build_deck(docs: Path, figs: dict, f: dict) -> Path:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Emu, Inches, Pt

    rgb = lambda h: RGBColor.from_string(h.lstrip("#").upper())
    C_BLUE, C_ORANGE, C_INK, C_MUTED = rgb(BLUE), rgb(ORANGE), rgb(INK), rgb(MUTED)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    W, H = prs.slide_width, prs.slide_height
    blank = prs.slide_layouts[6]

    def textbox(slide, x, y, w, h, text, size, *, bold=False, color=C_INK,
                align=PP_ALIGN.LEFT, spacing=1.0):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        for i, line in enumerate(text.split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = line
            p.alignment = align
            p.line_spacing = spacing
            for run in p.runs:
                run.font.size = Pt(size)
                run.font.bold = bold
                run.font.color.rgb = color
                run.font.name = "Segoe UI"
        return box

    def rule(slide, x, y, w, color=C_BLUE, h=0.035):
        from pptx.enum.shapes import MSO_SHAPE

        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        s.fill.solid()
        s.fill.fore_color.rgb = color
        s.line.fill.background()
        s.shadow.inherit = False
        return s

    def new(title: str, eyebrow: str = "") -> object:
        slide = prs.slides.add_slide(blank)
        if eyebrow:
            textbox(slide, 0.7, 0.42, 11, 0.3, eyebrow.upper(), 11, bold=True, color=C_BLUE)
        textbox(slide, 0.7, 0.72, 12, 0.7, title, 27, bold=True)
        rule(slide, 0.7, 1.46, 1.5)
        return slide

    def picture(slide, key, x, y, w):
        slide.shapes.add_picture(str(figs[key]), Inches(x), Inches(y), width=Inches(w))

    def stat(slide, x, y, value, label, color=C_BLUE, w=2.7):
        textbox(slide, x, y, w, 0.7, value, 30, bold=True, color=color)
        textbox(slide, x, y + 0.62, w, 0.4, label.upper(), 10, color=C_MUTED)

    # 1 — title
    s = prs.slides.add_slide(blank)
    rule(s, 0, 0, 13.333, C_BLUE, h=0.22)
    textbox(s, 0.9, 2.3, 11.5, 1.0, "Share of Wallet Intelligence Engine", 42, bold=True)
    textbox(s, 0.9, 3.35, 11.5, 0.6, "How much of each client's banking does Syn Bank actually hold?",
            18, color=C_MUTED)
    rule(s, 0.9, 4.25, 1.8, C_ORANGE)
    textbox(s, 0.9, 4.6, 11.5, 0.9, f"Team {TEAM}\n{MEMBERS}", 15, spacing=1.35)
    textbox(s, 0.9, 6.6, 11.5, 0.4, "Standard Bank × Data School Hackathon 2026", 11, color=C_MUTED)

    # 2 — the problem
    s = new("You cannot measure what you cannot see", "The problem")
    textbox(s, 0.7, 1.85, 11.9, 1.4,
            "Syn Bank sees every transaction that flows through Syn Bank — and none of the ones\n"
            "that flow through its competitors.", 19, spacing=1.3)
    textbox(s, 0.7, 3.0, 11.9, 1.6,
            "So share of wallet cannot be read off the internal data. It has to be estimated from\n"
            "outside, and the estimate has to be independent of what we already hold.",
            16, color=C_MUTED, spacing=1.35)
    rule(s, 0.7, 4.95, 11.9, rgb("#e6e6e3"), h=0.02)
    textbox(s, 0.7, 5.25, 11.9, 0.9,
            "Getting that independence wrong is subtle — and we got it wrong first.",
            18, bold=True, color=C_ORANGE)

    # 3 — the trap
    s = new("Our first model could not see the data", "What we found")
    textbox(s, 0.7, 1.8, 6.2, 1.6,
            "We sized the wallet from internal flow, then took captured\nvolume as a fraction of it:",
            15, spacing=1.3)
    box = textbox(s, 0.7, 2.85, 6.2, 0.6,
                  "share = (wallet × capture_ratio) / wallet", 15, bold=True, color=C_BLUE)
    textbox(s, 0.7, 3.45, 6.2, 1.9,
            "The wallet term cancels. Share was identical to the\nassumed capture rate — the data never entered it.\n\n"
            "It passed every obvious check: values between 0 and 1,\na plausible-looking ranking.",
            15, color=C_MUTED, spacing=1.3)
    stat(s, 0.7, 5.5, f"{f['size_ratio']:,.0f}×", "difference in client size", C_MUTED)
    stat(s, 3.6, 5.5, f"{f['old_spread'] * 100:.1f} pts", "difference in share", C_ORANGE)
    picture(s, "before_after", 7.3, 2.3, 5.4)

    # 4 — the fix
    s = new("Two sides, two independent sources", "The model")
    textbox(s, 0.7, 1.8, 5.9, 0.5, "TOP-DOWN — estimated", 12, bold=True, color=C_BLUE)
    textbox(s, 0.7, 2.25, 5.9, 2.6,
            "Addressable flow, from published FY2025 statements:\n\n"
            "•  Revenue  →  transactional banking\n"
            "•  Foreign revenue  →  cross-border / FX\n"
            "•  Cost of sales + inventory  →  trade finance\n\n"
            "Each scaled by an explicit SA-attribution share.",
            14, color=C_MUTED, spacing=1.3)
    textbox(s, 7.0, 1.8, 5.6, 0.5, "BOTTOM-UP — measured", 12, bold=True, color=C_ORANGE)
    textbox(s, 7.0, 2.25, 5.6, 2.6,
            "Captured flow, summed over the trailing 12 months\nof Syn Bank's own datasets.\n\n"
            "No assumption enters this side at all.\n\n"
            "That is what makes the sensitivity test in a\nlater slide meaningful.",
            14, color=C_MUTED, spacing=1.3)
    rule(s, 0.7, 5.05, 11.9, rgb("#e6e6e3"), h=0.02)
    textbox(s, 0.7, 5.35, 11.9, 0.6, "share  =  captured flow  ÷  addressable flow", 22, bold=True)
    textbox(s, 0.7, 6.1, 11.9, 0.5,
            f"Share now spans {f['share_min'] * 100:.1f}% to {f['share_max'] * 100:.1f}% across the portfolio.",
            15, color=C_MUTED)

    # 5 — headline
    s = new(f"Syn Bank holds {f['share'] * 100:.1f}% of its clients' banking flow", "The finding")
    stat(s, 0.7, 1.95, f"{f['share'] * 100:.1f}%", "share of wallet")
    stat(s, 3.7, 1.95, zar(f["addressable"]), "addressable flow")
    stat(s, 6.7, 1.95, zar(f["gap"]), "uncaptured gap", C_ORANGE)
    stat(s, 9.7, 1.95, zar(f["oppty"]), "fee opportunity / yr", C_ORANGE)
    picture(s, "pillars", 0.7, 3.3, 6.1)
    textbox(s, 7.3, 3.35, 5.4, 0.5, f"{f['lead_pillar']} is the gap", 15, bold=True)
    textbox(s, 7.3, 3.85, 5.4, 2.6,
            "It is the largest uncaptured pillar in absolute terms\n"
            f"and the lead pillar for {f['lead_pillar_n']} of {f['clients']} clients.\n\n"
            "That makes cash-management consolidation the\n"
            "repeatable conversation across the whole book —\n"
            "one proposition, twenty meetings.",
            14, color=C_MUTED, spacing=1.35)

    # 6 — who to call
    s = new("Where a banker should start on Monday", "Prioritisation")
    picture(s, "oppty", 0.7, 1.85, 7.4)
    textbox(s, 8.4, 1.9, 4.3, 0.5, "Ranked by winnable value", 14, bold=True)
    textbox(s, 8.4, 2.45, 4.3, 3.4,
            "The composite score blends:\n\n"
            "50%  gap size\n"
            "20%  ease of conversion\n"
            "15%  relationship depth\n"
            "15%  90-day urgency\n\n"
            "So the list is ordered by what is realistically\nwinnable, not simply by client size.",
            13, color=C_MUTED, spacing=1.32)

    # 7 — GenAI
    s = new("The model writes the briefing; the engine owns the numbers", "Generative AI")
    textbox(s, 0.7, 1.85, 5.9, 0.5, "How it is grounded", 14, bold=True)
    textbox(s, 0.7, 2.35, 5.9, 3.2,
            "Every figure is computed by the wallet engine and\npassed in as an evidence block. The model is told to\n"
            "reuse those figures verbatim — it does language,\nnot arithmetic.\n\n"
            "Each output is then re-read by a grounding check\nthat flags any rand amount or percentage that did\n"
            "not appear in the evidence.\n\n"
            "Currently zero unsupported figures across all\ngenerated briefings.",
            13.5, color=C_MUTED, spacing=1.32)
    textbox(s, 7.0, 1.85, 5.6, 0.5, "Why it survives a live demo", 14, bold=True)
    textbox(s, 7.0, 2.35, 5.6, 3.2,
            "•  Falls back to deterministic text, section by\n   section, if the API is unavailable\n\n"
            "•  Responses cached to disk, so it runs offline\n   and costs no quota to repeat\n\n"
            "•  One call, not an agent hierarchy — answers\n   land in about three seconds\n\n"
            "•  /ai-status reports which model answered",
            13.5, color=C_MUTED, spacing=1.32)
    rule(s, 0.7, 5.75, 11.9, rgb("#e6e6e3"), h=0.02)
    textbox(s, 0.7, 6.0, 11.9, 0.5,
            "It writes pre-meeting briefings and answers open questions over the portfolio in natural language.",
            14, color=C_MUTED)

    # 8 — sensitivity
    s = new("The conclusion survives our assumptions being wrong", "Rigour")
    picture(s, "sensitivity", 0.7, 1.9, 7.0)
    textbox(s, 8.1, 2.0, 4.6, 0.5, "±25% on every multiple", 14, bold=True)
    textbox(s, 8.1, 2.55, 4.6, 3.2,
            f"Portfolio-wide average share moves only\nbetween {f['sens_min'] * 100:.1f}% and {f['sens_max'] * 100:.1f}% "
            f"(not the\n{f['share_min'] * 100:.1f}%-{f['share_max'] * 100:.1f}% per-client range).\n\n"
            "The captured side does not move at all —\nit is measured, not assumed. If it did, the\n"
            "model would still be circular.\n\n"
            "Cross-check: our multiples imply banking\nfees of ~0.47% of revenue, inside the\n"
            "0.4–0.7% range the brief itself cites.",
            13.5, color=C_MUTED, spacing=1.32)

    # 9 — limitations
    s = new("What we would fix next", "Limitations")
    textbox(s, 0.7, 1.85, 5.9, 0.5, "Known limitations", 14, bold=True)
    textbox(s, 0.7, 2.35, 5.9, 3.4,
            "•  20 clients supplied, not the 50 described.\n   We modelled what we were given.\n\n"
            "•  Flow multiples are benchmarks, not\n   observations.\n\n"
            "•  SA-attribution is the most judgmental input.\n\n"
            "•  Revenue basis differs by industry and is\n   recorded per client.\n\n"
            "•  Gaps assume our records are complete.",
            13.5, color=C_MUTED, spacing=1.3)
    textbox(s, 7.0, 1.85, 5.6, 0.5, "Next steps", 14, bold=True)
    textbox(s, 7.0, 2.35, 5.6, 3.4,
            "•  Replace SA-attribution with disclosed\n   segment data from the statements.\n\n"
            "•  Extend to lending and DCM using the debt\n   schedules already collected.\n\n"
            "•  Forecast cash cycles from three years of\n   daily flow to time the engagement, not just\n   target it.\n\n"
            "•  Back-test share estimates against any\n   mandate wins that follow.",
            13.5, color=C_MUTED, spacing=1.3)

    # 10 — close
    s = prs.slides.add_slide(blank)
    rule(s, 0, 0, 13.333, C_BLUE, h=0.22)
    textbox(s, 0.9, 1.5, 11.5, 0.5, "IN ONE LINE", 12, bold=True, color=C_BLUE)
    textbox(s, 0.9, 2.0, 11.6, 2.2,
            f"Syn Bank holds {f['share'] * 100:.1f}% of a {zar(f['addressable']).replace('tn', ' trillion')} flow.\n"
            f"The other {100 - f['share'] * 100:.1f}% is worth {zar(f['oppty'])} a year in fees —\n"
            "and we can name who to call first.",
            32, bold=True, spacing=1.28)
    rule(s, 0.9, 4.6, 1.8, C_ORANGE)
    textbox(s, 0.9, 5.0, 11.5, 1.2,
            "Every number traceable to a computed field.\nEvery external figure cited. Every assumption tested.",
            16, color=C_MUTED, spacing=1.35)
    textbox(s, 0.9, 6.5, 11.5, 0.5, f"Team {TEAM} · {MEMBERS}", 12, color=C_MUTED)

    path = docs / "presentation_deck.pptx"
    prs.save(str(path))
    print(f"  deck -> {path.name} ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
    return path
