from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    open_robot_order_website()
    download()
    get_orders()
    archive_receipts()


def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def close_modal():
    """Closes the modal"""
    page = browser.page()
    page.click("button:text('OK')")


def download():
    """Downloads orders from given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)


def get_orders():
    """CSV files into tables"""
    table = Tables()
    orders = table.read_table_from_csv("orders.csv")

    for order in orders:
        fill_the_form(order)


def fill_the_form(order):
    """Fills the order form with given details"""
    page = browser.page()
    close_modal()

    page.select_option("#head", order["Head"])
    page.check(f"#id-body-" + order["Body"])
    page.fill(".form-control", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#preview")
    page.click("#order")

    while not page.query_selector("#order-another"):
        page.click("#order")

    store_receipt_as_pdf(order["Order number"])

    page.click("#order-another")


def store_receipt_as_pdf(order_number):
    """Stores receipts to PDF and takes a screenshot of ordered robots"""
    page = browser.page()

    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_file = f"output/{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, pdf_file)

    # screenshot
    robo = page.query_selector("#robot-preview-image")
    screenshot = f"output/{order_number}.png"
    robo.screenshot(path=screenshot)

    embed_screenshot_to_receipt(screenshot, pdf_file)


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds the screenshot to thge receipt PDF"""
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)


def archive_receipts():
    """Archives the receipts"""
    folder = Archive()
    folder.archive_folder_with_zip("output", "output/ordes.zip", include="*.pdf")
