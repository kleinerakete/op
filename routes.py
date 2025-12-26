from flask import session, request, jsonify, render_template, redirect, url_for
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from flask_login import current_user
import uuid
from models import Problem, Flow, Operator, RevenueEntry
from engine import select_flow_for_problem, compute_price, execute_problem

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def example_index():
    if current_user.is_authenticated:
        return render_template('dashboard.html', user=current_user)
    return render_template('landing.html')

@app.route('/problems', methods=['POST'])
@require_login
def create_problem_route():
    data = request.json
    try:
        flow = select_flow_for_problem(data['type'])
        price = compute_price(flow, data['payload'])
        
        problem = Problem(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            type=data['type'],
            payload=data['payload'],
            status='PRICED',
            price=price,
            payment_status='REQUIRED',
            flow_name=flow.name
        )
        db.session.add(problem)
        db.session.commit()
        return jsonify({"problem_id": problem.id, "price": price})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/payments/confirm', methods=['POST'])
@require_login
def confirm_payment_route():
    data = request.json
    problem = Problem.query.get(data['problem_id'])
    if not problem or problem.user_id != current_user.id:
        return jsonify({"error": "Problem not found"}), 404
    
    problem.payment_status = 'CONFIRMED'
    problem.status = 'PAID'
    db.session.commit()
    
    # Run execution in background (or synchronous for now)
    execute_problem(problem.id)
    return jsonify({"status": "Execution started", "problem_id": problem.id})

@app.route('/admin/bootstrap', methods=['POST'])
def bootstrap():
    # Only for initial setup, normally protected
    if Operator.query.count() == 0:
        op = Operator(name="AI_Analyzer", description="Analyzes complex data using GPT-5")
        db.session.add(op)
        flow = Flow(
            name="General_AI_Flow",
            problem_type="ai_task",
            base_price=5.0,
            price_per_complexity=0.1,
            steps=[{"operator_name": "AI_Analyzer"}]
        )
        db.session.add(flow)
        db.session.commit()
    return jsonify({"status": "Bootstrapped"})

@app.route('/revenue/summary')
@require_login
def revenue_summary():
    total = db.session.query(db.func.sum(RevenueEntry.amount)).scalar() or 0.0
    return jsonify({"total_revenue": total})
