from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, cast


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        PageBreak,
        PageTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.pdfgen.canvas import Canvas
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: reportlab. Install it from backend with "
        "`uv add reportlab`, then rerun `uv run python seed/generate_plot_documents.py`."
    ) from exc

from app.database import SessionLocal
from app.models import Plot


DOCUMENTS_ROOT = Path("uploads/documents")
DOCUMENT_SPECS: list[tuple[str, str, Callable[[Plot], list[tuple[str, list[str]]]]]] = []

BRAND_COLOR = colors.HexColor("#C66F57")
INK = colors.HexColor("#111827")
MUTED = colors.HexColor("#5B6B84")
SOFT_BG = colors.HexColor("#F5EEE8")
LINE = colors.HexColor("#E8DCD4")


def yes_no(value: bool | None) -> str:
    return "Available" if value else "Not confirmed"


def money(value: float | None) -> str:
    if value is None:
        return "Not provided"
    return f"${value:,.0f}"


def text(value: object) -> str:
    return str(value) if value not in (None, "") else "Not provided"


def sentence(*parts: object) -> str:
    return " ".join(str(part).strip() for part in parts if str(part).strip())


def base_snapshot(plot: Plot) -> list[list[str]]:
    return [
        ["Price", money(cast(float, plot.price)), "Area", f"{cast(float, plot.area_acres):g} acres"],
        ["City", f"{plot.city}, {plot.state}", "ZIP", text(plot.zip_code)],
        ["Zoning", text(plot.zoning_type), "Listing", f"{plot.listing_type} / {plot.status}"],
    ]


def utility_snapshot(plot: Plot) -> list[list[str]]:
    return [
        ["Road access", yes_no(cast(bool, plot.road_access)), "Water", yes_no(cast(bool, plot.water_access))],
        ["Electricity", yes_no(cast(bool, plot.electricity)), "Sewer", yes_no(cast(bool, plot.sewer))],
    ]


def brochure_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    return [
        (
            "Property Positioning",
            [
                sentence(
                    plot.description,
                    "SmartPlots highlights this parcel for",
                    text(plot.ideal_for).lower() + ".",
                ),
                f"Located near {text(plot.nearby_landmarks)}, the site offers a demo-ready example of how buyers can evaluate land based on lifestyle, utility readiness, and long-term value.",
            ],
        ),
        (
            "Buyer Fit",
            [
                f"Primary goals: {text(plot.ideal_for)}.",
                f"Current status: {text(plot.status)} for {text(plot.listing_type)} with an asking price of {money(cast(float, plot.price))}.",
            ],
        ),
        ("Risk Context", [text(plot.risk_notes)]),
    ]


def fact_sheet_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    return [
        (
            "At-a-Glance Summary",
            [
                f"{plot.title} is a {cast(float, plot.area_acres):g}-acre {text(plot.zoning_type)} parcel in {plot.city}, {plot.state} {text(plot.zip_code)}.",
                f"Recommended SmartPlots goals: {text(plot.ideal_for)}.",
            ],
        ),
        (
            "Location Notes",
            [
                f"Nearby landmarks and demand drivers include {text(plot.nearby_landmarks)}.",
                "This mix of location signals helps SmartPlots compare lifestyle fit, liquidity, and appreciation potential.",
            ],
        ),
        ("Known Considerations", [text(plot.risk_notes)]),
    ]


def zoning_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    return [
        (
            "Zoning Overview",
            [
                f"Recorded zoning type: {text(plot.zoning_type)}.",
                "This report is a demo planning summary and should be paired with city or county confirmation before acquisition.",
            ],
        ),
        (
            "Likely Use Alignment",
            [
                f"The parcel is most aligned with: {text(plot.ideal_for)}.",
                f"Landmark context: {text(plot.nearby_landmarks)}.",
            ],
        ),
        (
            "Review Items",
            [
                "Confirm setbacks, lot coverage, height limits, parking requirements, and any overlay districts.",
                text(plot.risk_notes),
            ],
        ),
    ]


def utility_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    missing = [
        label
        for label, available in [
            ("road access", plot.road_access),
            ("water service", plot.water_access),
            ("electricity", plot.electricity),
            ("sewer service", plot.sewer),
        ]
        if not available
    ]
    return [
        (
            "Utility Readiness",
            [
                f"Road access: {yes_no(cast(bool, plot.road_access))}. Water: {yes_no(cast(bool, plot.water_access))}. Electricity: {yes_no(cast(bool, plot.electricity))}. Sewer: {yes_no(cast(bool, plot.sewer))}.",
                "Utility readiness improves development feasibility, financing confidence, and buyer liquidity.",
            ],
        ),
        (
            "Potential Gaps",
            [
                "No major utility gaps are indicated in the demo record."
                if not missing
                else f"Items requiring confirmation: {', '.join(missing)}.",
                text(plot.risk_notes),
            ],
        ),
    ]


def soil_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    return [
        (
            "Preliminary Site Conditions",
            [
                f"This {cast(float, plot.area_acres):g}-acre parcel should receive normal soil, drainage, and buildability review before design work.",
                "SmartPlots flags soil diligence as especially important where septic, slope, floodplain, or retaining wall issues may affect cost.",
            ],
        ),
        (
            "Recommended Studies",
            [
                "Order a geotechnical review for bearing capacity, drainage behavior, and foundation recommendations.",
                "Confirm septic feasibility where public sewer is not available.",
                text(plot.risk_notes),
            ],
        ),
    ]


def investment_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    return [
        (
            "Investment Thesis",
            [
                f"At {money(cast(float, plot.price))} for {cast(float, plot.area_acres):g} acres, this parcel supports the following SmartPlots goals: {text(plot.ideal_for)}.",
                f"Demand signals include proximity to {text(plot.nearby_landmarks)}.",
            ],
        ),
        (
            "Value Drivers",
            [
                f"Zoning: {text(plot.zoning_type)}. Utilities: road {yes_no(cast(bool, plot.road_access)).lower()}, water {yes_no(cast(bool, plot.water_access)).lower()}, electricity {yes_no(cast(bool, plot.electricity)).lower()}, sewer {yes_no(cast(bool, plot.sewer)).lower()}.",
                "Strong utility readiness and recognizable location anchors can improve resale depth and reduce diligence friction.",
            ],
        ),
        ("Risk Notes", [text(plot.risk_notes)]),
    ]


def growth_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    return [
        (
            "County and Market Context",
            [
                f"{plot.city}, {plot.state} land demand is influenced by nearby civic, employment, recreation, and transportation anchors.",
                f"For this parcel, SmartPlots references: {text(plot.nearby_landmarks)}.",
            ],
        ),
        (
            "Growth Signals",
            [
                f"Best-fit goals: {text(plot.ideal_for)}.",
                "Buyers should compare local permitting activity, infrastructure plans, school or employment trends, and recent land sales.",
            ],
        ),
        ("Planning Caveat", [text(plot.risk_notes)]),
    ]


def neighborhood_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    return [
        (
            "Area Guide",
            [
                f"The parcel is located in {plot.city}, {plot.state} {text(plot.zip_code)}, near {text(plot.nearby_landmarks)}.",
                "This location profile helps buyers understand commute, lifestyle, recreation, and resale demand drivers.",
            ],
        ),
        (
            "Lifestyle Fit",
            [
                f"SmartPlots goal alignment: {text(plot.ideal_for)}.",
                f"The parcel size of {cast(float, plot.area_acres):g} acres supports a focused evaluation of privacy, access, build scale, and outdoor use.",
            ],
        ),
    ]


def disclosure_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    return [
        (
            "Demo Disclosure Summary",
            [
                "This SmartPlots demo disclosure summarizes known data fields and is not a substitute for seller disclosures or municipal records.",
                f"Recorded risk notes: {text(plot.risk_notes)}",
            ],
        ),
        (
            "Items to Confirm",
            [
                f"Confirm zoning type listed as {text(plot.zoning_type)} with the relevant city or county office.",
                "Verify access, utility availability, easements, environmental history, title exceptions, and any construction constraints.",
            ],
        ),
    ]


def checklist_sections(plot: Plot) -> list[tuple[str, list[str]]]:
    return [
        (
            "Due Diligence Checklist",
            [
                "Confirm title, legal access, survey boundaries, and recorded easements.",
                f"Verify zoning and permitted uses for {text(plot.zoning_type)} land.",
                "Confirm utility taps, extension costs, and capacity for water, power, and sewer or septic.",
                "Review soil, drainage, flood, slope, environmental, and permitting conditions.",
            ],
        ),
        (
            "SmartPlots Priority Notes",
            [
                f"Buyer goals to preserve: {text(plot.ideal_for)}.",
                f"Location anchors to compare in valuation: {text(plot.nearby_landmarks)}.",
                f"Known risk notes: {text(plot.risk_notes)}",
            ],
        ),
    ]


DOCUMENT_SPECS = [
    ("brochure.pdf", "SmartPlots Property Brochure", brochure_sections),
    ("property_fact_sheet.pdf", "Property Fact Sheet", fact_sheet_sections),
    ("zoning_report.pdf", "Zoning Report", zoning_sections),
    ("utility_report.pdf", "Utility Report", utility_sections),
    ("soil_report.pdf", "Soil and Site Conditions Report", soil_sections),
    ("investment_report.pdf", "Investment Report", investment_sections),
    ("county_growth_report.pdf", "County Growth Report", growth_sections),
    ("neighborhood_guide.pdf", "Neighborhood Guide", neighborhood_sections),
    ("property_disclosure.pdf", "Property Disclosure Summary", disclosure_sections),
    ("due_diligence_checklist.pdf", "Due Diligence Checklist", checklist_sections),
]


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "SmartPlotsTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=INK,
            spaceAfter=8,
        ),
        "section": ParagraphStyle(
            "SmartPlotsSection",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=INK,
            spaceBefore=10,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "SmartPlotsBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#243047"),
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "SmartPlotsSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9,
            textColor=MUTED,
        ),
        "cell": ParagraphStyle(
            "SmartPlotsCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#243047"),
        ),
    }


def draw_header_footer(canvas, doc, report_title: str, plot: Plot, generated_date: str) -> None:
    canvas.saveState()
    width, height = letter

    canvas.setFillColor(SOFT_BG)
    canvas.rect(0, height - 1.05 * inch, width, 1.05 * inch, fill=1, stroke=0)
    canvas.setFillColor(BRAND_COLOR)
    canvas.rect(0, height - 1.05 * inch, width, 0.08 * inch, fill=1, stroke=0)

    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(0.55 * inch, height - 0.38 * inch, "SmartPlots")
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.55 * inch, height - 0.56 * inch, "AI-Powered Land Intelligence")

    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(INK)
    canvas.drawRightString(width - 0.55 * inch, height - 0.34 * inch, report_title)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - 0.55 * inch, height - 0.51 * inch, plot.title[:72])
    canvas.drawRightString(
        width - 0.55 * inch,
        height - 0.68 * inch,
        f"{plot.city}, {plot.state} | Generated {generated_date}",
    )

    canvas.setStrokeColor(LINE)
    canvas.line(0.55 * inch, 0.55 * inch, width - 0.55 * inch, 0.55 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(
        0.55 * inch,
        0.35 * inch,
        "Generated by SmartPlots - AI-Powered Land Intelligence",
    )
    canvas.restoreState()


class NumberedCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()  # type: ignore[attr-defined]

    def save(self) -> None:
        total_pages = len(self._saved_page_states)
        width, _ = letter

        for page_number, state in enumerate(self._saved_page_states, start=1):
            self.__dict__.update(state)
            self.setFont("Helvetica", 7.5)
            self.setFillColor(MUTED)
            self.drawRightString(
                width - 0.55 * inch,
                0.35 * inch,
                f"Page {page_number} of {total_pages}",
            )
            Canvas.showPage(self)

        Canvas.save(self)


def build_table(rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> Table:
    table_rows = [[Paragraph(str(cell), styles["cell"]) for cell in row] for row in rows]
    table = Table(table_rows, colWidths=[1.0 * inch, 1.65 * inch, 1.0 * inch, 1.65 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
                ("TEXTCOLOR", (2, 0), (2, -1), MUTED),
            ]
        )
    )
    return table


def build_story(
    plot: Plot,
    report_title: str,
    sections: list[tuple[str, list[str]]],
    styles: dict[str, ParagraphStyle],
) -> list:
    story = [
        Paragraph(report_title, styles["title"]),
        Paragraph(
            f"{plot.title} | {plot.city}, {plot.state} {text(plot.zip_code)}",
            styles["body"],
        ),
        Spacer(1, 0.06 * inch),
        build_table(base_snapshot(plot), styles),
        Spacer(1, 0.08 * inch),
        build_table(utility_snapshot(plot), styles),
        Spacer(1, 0.08 * inch),
    ]

    for heading, paragraphs in sections:
        story.append(Paragraph(heading, styles["section"]))
        for paragraph in paragraphs[:4]:
            story.append(Paragraph(str(paragraph), styles["body"]))

    story.append(Spacer(1, 0.05 * inch))
    story.append(Paragraph("SmartPlots Demo Note", styles["section"]))
    story.append(
        Paragraph(
            "This document is generated from SmartPlots demo data for product demonstration, "
            "RAG ingestion, and land-discovery workflow testing.",
            styles["small"],
        )
    )
    return story


def generate_pdf(plot: Plot, file_path: Path, report_title: str, sections: list[tuple[str, list[str]]]) -> None:
    styles = make_styles()
    generated_date = datetime.now().strftime("%B %d, %Y")

    doc = BaseDocTemplate(
        str(file_path),
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=1.25 * inch,
        bottomMargin=0.75 * inch,
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="main",
        showBoundary=0,
    )
    template = PageTemplate(
        id="smartplots",
        frames=[frame],
        onPage=lambda canvas, doc_obj: draw_header_footer(
            canvas,
            doc_obj,
            report_title,
            plot,
            generated_date,
        ),
    )
    doc.addPageTemplates([template])

    story = build_story(plot, report_title, sections, styles)
    doc.build(story, canvasmaker=NumberedCanvas)


def generate_documents_for_plot(plot: Plot) -> None:
    plot_dir = DOCUMENTS_ROOT / f"plot-{plot.id}"
    plot_dir.mkdir(parents=True, exist_ok=True)

    generated_count = 0
    for filename, report_title, section_builder in DOCUMENT_SPECS:
        file_path = plot_dir / filename
        try:
            generate_pdf(plot, file_path, report_title, section_builder(plot))
            generated_count += 1
        except Exception as exc:
            print(f"Failed to generate {file_path} for plot {plot.id}: {exc}")

    if generated_count == len(DOCUMENT_SPECS):
        print(f"Generated 10 documents for plot {plot.id}: {plot.title}")
    else:
        print(
            f"Generated {generated_count} documents for plot {plot.id}: "
            f"{plot.title} ({len(DOCUMENT_SPECS) - generated_count} failed)"
        )


def main() -> None:
    db = SessionLocal()
    try:
        plots = db.query(Plot).order_by(Plot.id).all()
        if not plots:
            print("No plots found. Run seed/seed_plots.py before generating documents.")
            return

        DOCUMENTS_ROOT.mkdir(parents=True, exist_ok=True)
        for plot in plots:
            generate_documents_for_plot(plot)
    finally:
        db.close()


if __name__ == "__main__":
    main()
