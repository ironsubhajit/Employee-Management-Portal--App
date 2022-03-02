import logging
from flask import (
    render_template, Blueprint, request
)

main_bp = Blueprint('main', __name__)

main_logger = logging.getLogger()


@main_bp.route("/")
@main_bp.route("/home")
def home():
    # print(request.headers)
    main_logger.info(msg="Home page request made")
    return render_template("main/home_page.html")


@main_bp.route("/page-not-found")
def page_not_found():
    main_logger.warning(msg="Bad page request made !")
    return render_template("main/404.html")


@main_bp.route("/server-error")
def server_error_page():
    main_logger.warning(msg="Server error occurred")
    return render_template("main/500.html")
