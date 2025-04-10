
# Production Planner

Веб-приложение для расчета оптимального графика загрузки бригад по плану производства с учетом:

- серийного и несерийного выпуска,
- квалификации бригад,
- ограничения по рабочему времени,
- слесарного участка с двумя бригадами и равномерной загрузкой.

---

## 🔧 Установка и запуск

### 1. Клонировать проект

```
git clone https://github.com/your/repo.git
cd production-planner
```

### 2. Установить и запустить **бэкенд** (Python + Pyomo)

#### 2.1 Установить зависимости

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2.2 Установить решатель CBC

**Через Conda (рекомендуется):**

```bash
conda install -c conda-forge coincbc
```

**Или вручную (Windows):**
- Скачать из: https://github.com/coin-or/Cbc/releases
- Распаковать и добавить путь к `cbc.exe` в `PATH`.

#### 2.3 Запуск сервера

```bash
python server_full_model_fixed.py
```

Сервер будет доступен на `http://localhost:5000`.

---

### 3. Установить и запустить **фронтенд** (React)

#### 3.1 Установка

```bash
cd frontend
npm install
```

#### 3.2 Запуск

```bash
npm start
```

Фронтенд запустится на `http://localhost:3000`.

---

## 📦 Структура проекта

```
backend/
  └── server_full_model_fixed.py   # Flask + Pyomo + CBC модель
  └── requirements.txt

frontend/
  └── src/
      └── components/
          └── BrigadesForm.js
          └── ProductsForm.js
          └── ResultView.js
      └── style.css
      └── App.js
```

---



