import uuid
import time
from datetime import datetime
from app import db, openai_client
from models import Problem, Flow, Operator, RevenueEntry
import logging

def select_flow_for_problem(problem_type):
    flow = Flow.query.filter_by(problem_type=problem_type).first()
    if not flow:
        raise ValueError(f"No flow found for problem type: {problem_type}")
    return flow

def compute_price(flow, payload):
    base_complexity = len(str(payload))
    extra_complexity = payload.get("complexity", 0)
    complexity = base_complexity + extra_complexity
    price = flow.base_price + flow.price_per_complexity * complexity
    return round(price, 2)

def execute_problem(problem_id):
    problem = Problem.query.get(problem_id)
    if not problem:
        logging.error(f"Problem {problem_id} not found")
        return

    if problem.payment_status != 'CONFIRMED':
        logging.warning(f"Problem {problem_id} is not paid")
        return

    flow = Flow.query.filter_by(name=problem.flow_name).first()
    if not flow:
        problem.status = 'FAILED'
        problem.error = "Flow not found"
        db.session.commit()
        return

    problem.status = 'EXECUTING'
    problem.updated_at = datetime.utcnow()
    db.session.commit()

    current_payload = problem.payload
    try:
        for step in flow.steps:
            op_name = step['operator_name']
            operator = Operator.query.get(op_name)
            if not operator:
                raise RuntimeError(f"Operator {op_name} not found")

            # In a real system, we'd call the operator implementation here.
            # Since the user wants "all official active", we'll use OpenAI for the logic.
            # newest OpenAI model is "gpt-5" released August 7, 2025
            response = openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": f"You are an AI operator performing step: {operator.name}. Description: {operator.description}. Return output in JSON format."},
                    {"role": "user", "content": f"Input data: {current_payload}"}
                ],
                response_format={ "type": "json_object" }
            )
            current_payload = response.choices[0].message.content
            operator.success_count += 1

        problem.status = 'COMPLETED'
        problem.result = {"output": current_payload}
        problem.updated_at = datetime.utcnow()
        
        # Book revenue
        rev = RevenueEntry()
        rev.id = str(uuid.uuid4())
        rev.problem_id = problem.id
        rev.amount = problem.price
        db.session.add(rev)
        db.session.commit()

    except Exception as e:
        logging.error(f"Execution error: {e}")
        problem.status = 'FAILED'
        problem.error = str(e)
        db.session.commit()
