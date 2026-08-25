"""
Route handlers for ChurnGuard.
Defines all endpoints: dashboard, prediction, data explorer, and API.
"""

from flask import Blueprint, render_template, request, jsonify, Response
import app as application

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    """Analytics dashboard with KPIs and chart data."""
    stats = application.data_service.get_summary_stats()
    feature_importance = application.churn_model.get_feature_importance(8)
    return render_template(
        "dashboard.html",
        stats=stats,
        feature_importance=feature_importance,
    )


@main_bp.route("/predict", methods=["GET", "POST"])
def predict():
    """Customer churn prediction form and results."""
    result = None
    errors = None
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()

        # Validate input
        cleaned_data, validation_errors = application.churn_model.validate_input(
            form_data
        )

        if validation_errors:
            errors = validation_errors
        else:
            try:
                result = application.churn_model.predict(cleaned_data)
            except Exception as e:
                errors = [f"Prediction failed: {str(e)}"]

    return render_template(
        "predict.html",
        result=result,
        errors=errors,
        form_data=form_data,
        valid_options=application.churn_model.VALID_OPTIONS,
        numeric_fields=application.churn_model.NUMERIC_FIELDS,
    )


@main_bp.route("/explorer")
def explorer():
    """Data explorer with filtering, sorting, and pagination."""
    # Collect filter parameters
    filters = {}
    filter_options = application.data_service.get_filter_options()

    for col in filter_options:
        value = request.args.get(col, "")
        if value:
            filters[col] = value

    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by", "")
    sort_order = request.args.get("sort_order", "asc")

    data = application.data_service.get_filtered_data(
        filters=filters,
        page=page,
        sort_by=sort_by if sort_by else None,
        sort_order=sort_order,
    )

    return render_template(
        "explorer.html",
        data=data,
        filters=filters,
        filter_options=filter_options,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# --- API Endpoints ---


@main_bp.route("/api/chart-data/<chart_type>")
def chart_data(chart_type):
    """Return JSON data for dashboard charts."""
    ds = application.data_service

    chart_handlers = {
        "churn-by-contract": lambda: ds.get_churn_by_column("Contract"),
        "churn-by-internet": lambda: ds.get_churn_by_column("InternetService"),
        "churn-by-tenure": lambda: ds.get_churn_by_column("tenure_group"),
        "churn-by-payment": lambda: ds.get_churn_by_column("PaymentMethod"),
        "churn-distribution": lambda: ds.get_churn_distribution(),
        "charges-distribution": lambda: ds.get_monthly_charges_distribution(),
    }

    handler = chart_handlers.get(chart_type)
    if not handler:
        return jsonify({"error": "Unknown chart type"}), 404

    return jsonify(handler())


@main_bp.route("/api/export")
def export_data():
    """Export filtered customer data as CSV."""
    filters = {}
    filter_options = application.data_service.get_filter_options()

    for col in filter_options:
        value = request.args.get(col, "")
        if value:
            filters[col] = value

    csv_content = application.data_service.export_csv(filters=filters if filters else None)

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=churn_data_export.csv"},
    )


@main_bp.route("/models")
def models():
    """Model comparison page — metrics for LR, DT, and Random Forest."""
    comparison = application.churn_model.get_model_comparison()
    return render_template("models.html", comparison=comparison)


@main_bp.route("/api/model-metrics")
def model_metrics():
    """Return model comparison metrics as JSON for Chart.js."""
    comparison = application.churn_model.get_model_comparison()
    if not comparison:
        return jsonify({"error": "model_metrics.json not found — run train_model.py first"}), 404
    return jsonify(comparison)

