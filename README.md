
# 📘 **BOM Comparison Tool — User Guide**

Welcome!
This tool helps you compare one **Master BOM** with up to **five Target BOMs** — even if they’re in **different formats**.
The goal: make BOM checking simple, visual, and fast.

Below is a **clean step-by-step guide with screenshots**, just like a real user manual.

---

# 🧭 **1. Start at the Dashboard**

When you open the tool, you land on the Upload & Compare page.

This screen shows the upload rules and lets you begin your comparison.

### 📸 Screenshot — Home Page

<img width="1910" height="908" alt="image" src="https://github.com/user-attachments/assets/1f7d8b58-533a-4085-8df5-52d44b3fee69" />


---

# 📤 **2. Upload Your Master & Target Files**

A Master BOM must be `.xlsx`.
Target BOMs can be:

* XLSX
* CSV
* PDF
* DOCX
* TXT

You can upload **1 to 5** target files at once.

---

# 🖱️ **3. Select Files and Click "Compare"**

Once files are selected, they show up below the upload boxes.
Press **Compare BOMs** to process them.

### 📸 Screenshot — Files Selected

<img width="1911" height="904" alt="image" src="https://github.com/user-attachments/assets/9f1c5428-1a3e-4f4f-9ae8-0ebe480ec521" />

---

# 📊 **4. View Comparison Results**

After processing, you're redirected to the results.

You will see:

* Total Master Parts
* Total Target Parts
* Missing parts
* Extra parts
* Quantity mismatches

Tab headers show each target file separately.

### 📸 Screenshot — Comparison Summary (Table View)

<img width="1893" height="909" alt="image" src="https://github.com/user-attachments/assets/6e5d50cb-ad0b-494d-bd05-1471ace9b6bb" />

---

# 🔍 **5. Table-Style Comparison (Default)**

The classic table is shown first:

* Each row is one MPN
* Side-by-side Master vs Target values
* Rows are highlighted by status:

  * 🔴 Missing
  * 🟢 Extra
  * 🟡 Mismatch

---

# 🧩 **6. Switch to Diff View**

Use the toggle in the upper-right corner to switch to **Diff View**.

This layout is similar to VS Code or Git diffs — clean left vs right panels.

You get a very clear breakdown per MPN.

### 📸 Screenshot — Diff View

<img width="1895" height="912" alt="image" src="https://github.com/user-attachments/assets/c996adf7-deb6-48c4-b07d-9b0f045502fe" />

---

# 🔁 **7. Compare Multiple Targets Easily**

Each target file gets its own **tab**:

* Target 1 — bom.xlsx
* Target 2 — bom.pdf
* Target 3 — bom.docx
* etc.

Switch between tabs to compare each one.

---

# 💾 **8. Download Results**

You can export your results:

* **JSON Download** → Raw structured data

---

# 🗂️ **9. View Past Comparisons**

Every comparison is stored automatically.

The history page displays:

* Comparison ID
* Created date
* Master BOM file
* Number of target files
* Quick actions (View / JSON / Excel)

### 📸 Screenshot — Comparison History

<img width="1912" height="909" alt="image" src="https://github.com/user-attachments/assets/76b0b198-7796-4029-bbfc-0a90f650db96" />

---

# ⭐ Features at a Glance

* Works with **mixed formats**
* Auto-detects columns (MPN, Quantity, Ref_Des, Description)
* Highlights missing, extra, and mismatched items
* Two UI modes: **Table** + **Diff**
* Compare **1 master → many targets**
* Export to JSON & Excel
* Keeps full comparison history

---

# 📦 Installation (Quick)

```bash
git clone <your-repo-url>
cd bom_comparison_tool
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
