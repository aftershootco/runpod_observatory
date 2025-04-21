from fpdf import FPDF
import datetime


def create_report_pdf():
    pdf = FPDF()

    # List of images in the order you want them placed in the PDF
    images = [
        "table.png",
        "bar_totalCostPerDay.png",
        "bar_totalCost.png",
        "bar_totalGPUs.png",
        "bar_numMachines.png",
        "bar_totalGPUhours.png",
    ]

    # Example: define margins (optional)
    left_margin = 10
    top_margin = 10
    pdf.set_margins(left=left_margin, top=top_margin, right=left_margin)

    for image_path in images:
        pdf.add_page()

        # Calculate a usable width (e.g., total page width minus left/right margin * 2)
        # pdf.w is the full page width; pdf.l_margin is the left margin
        usable_width = pdf.w - 2 * pdf.l_margin

        # Place the image on the page. Adjust x/y/w/h as needed.
        # Here, we place it at (x=left_margin, y=top_margin)
        # so that it respects the margin and fits horizontally.
        pdf.image(image_path, x=pdf.l_margin, y=pdf.t_margin, w=usable_width)

    # Generate a human-readable date/time, e.g. 20_March_2025_153045
    now = datetime.datetime.now()
    human_readable_date_time = now.strftime("%d_%B_%Y_%H%M%S")

    pdf_name = f"report-{human_readable_date_time}.pdf"
    pdf.output(pdf_name)
    print(f"PDF created: {pdf_name}")


if __name__ == "__main__":
    create_report_pdf()
