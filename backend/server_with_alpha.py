
from flask import Flask, request, jsonify
from flask_cors import CORS
from pyomo.environ import *
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    brigades = data['brigades']
    products = data['products']
    start_date_str = data.get('startDate')
    alpha = float(data.get('alpha', 1.0))  # теперь alpha приходит от пользователя

    if not start_date_str:
        return jsonify({"error": "Дата начала не указана"}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    except:
        return jsonify({"error": "Неверный формат даты"}), 400

    brigade_names = [b['name'] for b in brigades]
    product_names = [p['name'] for p in products]
    sl_brigades = brigade_names[:2]

    if len(sl_brigades) < 2:
        return jsonify({"error": "Для расчета слесарного участка необходимо минимум 2 бригады."}), 400

    prod_rate = {(p['name'], b['name']): float(p['productionRates'].get(b['name'], 0)) for p in products for b in brigades}
    qualification = {(p['name'], b['name']): int(p['qualifications'].get(b['name'], 0)) for p in products for b in brigades}
    load = {b['name']: float(b.get('load', 0)) * 3 for b in brigades}
    serial_plan = {p['name']: float(p.get('serialPlan', 0)) for p in products}
    nonserial_plan = {p['name']: float(p.get('nonSerialPlan', 0)) for p in products}
    assembly_rate = {p['name']: float(p.get('assemblyRate', 1)) for p in products}

    model = ConcreteModel()
    model.P = Set(initialize=product_names)
    model.B = Set(initialize=brigade_names)
    model.SL = Set(initialize=sl_brigades)

    model.xs = Var(model.P, model.B, domain=NonNegativeReals)
    model.xns = Var(model.P, model.B, domain=NonNegativeReals)
    model.xa = Var(model.P, model.SL, domain=NonNegativeReals)

    model.r = Var(model.P, domain=NonNegativeReals)
    model.u = Var(model.B, domain=NonNegativeReals)

    model.obj = Objective(
        expr=sum(model.r[p] for p in model.P) + alpha * sum(model.u[b] for b in model.B),
        sense=minimize
    )

    def plan_rule(m, p):
        qty = sum((m.xs[p, b] + m.xns[p, b]) * prod_rate[p, b] for b in m.B if (p, b) in prod_rate)
        return qty + m.r[p] >= serial_plan[p] + nonserial_plan[p]
    model.plan = Constraint(model.P, rule=plan_rule)

    def capacity_rule(m, b):
        base = sum((m.xs[p, b] + m.xns[p, b]) for p in m.P if (p, b) in prod_rate)
        sl = sum(m.xa[p, b] for p in m.P if b in sl_brigades)
        return base + sl + m.u[b] <= load[b]
    model.cap = Constraint(model.B, rule=capacity_rule)

    def qual_serial(m, p, b):
        return m.xs[p, b] <= 1000 * (1 if qualification[p, b] in [1, 2] else 0)
    def qual_nonserial(m, p, b):
        return m.xns[p, b] <= 1000 * (1 if qualification[p, b] == 2 else 0)
    model.qual_s = Constraint(model.P, model.B, rule=qual_serial)
    model.qual_ns = Constraint(model.P, model.B, rule=qual_nonserial)

    def sl_equal_load1(m, p):
        b1, b2 = list(m.SL)
        return m.xa[p, b1] - m.xa[p, b2] <= 0.01
    def sl_equal_load2(m, p):
        b1, b2 = list(m.SL)
        return m.xa[p, b2] - m.xa[p, b1] <= 0.01
    model.sl_balance1 = Constraint(model.P, rule=sl_equal_load1)
    model.sl_balance2 = Constraint(model.P, rule=sl_equal_load2)

    def sl_required(m, p):
        total_output = sum((m.xs[p, b] + m.xns[p, b]) * prod_rate[p, b] for b in m.B if (p, b) in prod_rate)
        return sum(m.xa[p, b] for b in m.SL) >= total_output / assembly_rate[p]
    model.sl_qty = Constraint(model.P, rule=sl_required)

    solver = SolverFactory('cbc')
    solver.solve(model)

    по_бригадам = {}
    загрузка = {b: {'часы': 0, 'лимит': load[b]} for b in brigade_names}
    производство = {}
    task_hours_by_brigade = {b: [] for b in brigade_names}

    for p in product_names:
        производство[p] = {'план': serial_plan[p] + nonserial_plan[p], 'факт': 0}
        for b in brigade_names:
            val_s = model.xs[p, b].value if (p, b) in model.xs else 0
            val_ns = model.xns[p, b].value if (p, b) in model.xns else 0
            rate = prod_rate.get((p, b), 0)
            qty = (val_s + val_ns) * rate
            часы = val_s + val_ns
            if часы > 0:
                по_бригадам.setdefault(b, []).append({'product': p, 'тип': 'осн.', 'объем': round(qty, 2), 'часы': round(часы, 2)})
                task_hours_by_brigade[b].append({'product': p, 'hours': часы})
                загрузка[b]['часы'] += часы
                производство[p]['факт'] += qty

        for b in sl_brigades:
            val = model.xa[p, b].value
            if val and val > 0:
                по_бригадам.setdefault(b, []).append({'product': p, 'тип': 'сборка', 'объем': round(val * assembly_rate[p], 2), 'часы': round(val, 2)})
                task_hours_by_brigade[b].append({'product': p + " (сборка)", 'hours': val})
                загрузка[b]['часы'] += val

    for b in загрузка:
        lim = загрузка[b]['лимит']
        часы = загрузка[b]['часы']
        загрузка[b]['загрузка_%'] = round(100 * часы / lim, 1) if lim > 0 else 0

    for p in производство:
        f = производство[p]['факт']
        производство[p]['факт'] = round(f, 2)
        производство[p]['отклонение'] = round(план := производство[p]['план'] - f, 2)

    days = [start_date + timedelta(days=i) for i in range(90)]
    schedule_matrix = {b: [] for b in brigade_names}
    for b_index, b in enumerate(brigade_names):
        for i, day in enumerate(days):
            cycle = (i + b_index * 2) % 4
            if cycle < 2:
                schedule_matrix[b].append(day.strftime("%Y-%m-%d"))

    schedule_output = {b: [] for b in brigade_names}
    max_hours_per_day = 8
    for b in brigade_names:
        remaining_tasks = task_hours_by_brigade[b][:]
        for date in schedule_matrix[b]:
            remaining_day = max_hours_per_day
            i = 0
            while i < len(remaining_tasks) and remaining_day > 0:
                task = remaining_tasks[i]
                assign = min(task['hours'], remaining_day)
                schedule_output[b].append({'date': date, 'product': task['product'], 'hours': assign})
                task['hours'] -= assign
                remaining_day -= assign
                if task['hours'] <= 0:
                    remaining_tasks.pop(i)
                else:
                    i += 1

    return jsonify({
        'по_бригадам': по_бригадам,
        'загрузка': загрузка,
        'по_производству': производство,
        'график': schedule_output
    })

if __name__ == '__main__':
    app.run(debug=True)
