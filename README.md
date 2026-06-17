# 🎓 Student Peer Review System (SPRS)

[![Live Site](https://img.shields.io/badge/Live%20Website-sprs.tail28f96f.ts.net-blue?style=for-the-badge&logo=google-cloud)](https://sprs.tail28f96f.ts.net/)

The **Student Peer Review System (SPRS)** is a modern, lightweight web application built with Ruby on Rails 8.1 designed for higher education courses. It automates and streamlines team-based peer assessments, helping educators handle grading fairly while shielding courses against collusion, free-riders, and grade inflation.

---

## 🔍 Concept & Purpose

In university courses, group projects are highly effective for learning but notoriously difficult to grade fairly. A single team grade can reward "free-riders" who contributed nothing, or penalize students who did the majority of the work.

SPRS solves this by integrating **student-led peer evaluations** with **lecturer grading**. Students rate their teammates and reflect on their own contributions. The system's grading engine then automatically normalizes these raw ratings and applies a mathematically sound, three-part formula to calculate final individual marks.

### Key Benefits
*   **Zero Grade Inflation:** Peer ratings are mathematically normalized so that the average score given by any student is fixed, preventing teams from colluding to give everyone maximum scores.
*   **Active Peer Incentivization:** Students are required to evaluate their teammates. A strict penalty rules out final marks for students who fail to submit reviews.
*   **Custom Evaluation Criteria:** Lecturers can customize the self-review questions for different course needs.
*   **Seamless LMS Integration:** Roster setups and final grades can be imported/exported using standard CSV structures compatible with learning management systems like Moodle.

---

## ⚙️ The Grading Engine (Formulas)

The core value of SPRS lies in its grading calculations, which run within a single transaction during grade generation.

### 1. Peer Rating Normalization
To avoid collusion or grade inflation, students cannot simply give all their teammates a $5/5$. When a student submits ratings for their group, the raw scores $R_i \in [1, 5]$ are normalized. 

The formula for the **Adjusted Rating ($\text{AdjR}_i$)** for teammate $i$ is:

$$\text{Adjusted Rating}_i = \left( \frac{\text{Raw Rating given to Student } i}{\text{Total Raw Ratings given to Group}} \right) \times 3 \times \text{Number of Students in Group}$$

#### Why this works:
*   This makes peer reviews a zero-sum game. The sum of adjusted ratings given by a reviewer is always exactly $3.0 \times \text{Group Size}$, which forces the average adjusted rating given to be exactly **$3.0$**.
*   If a student rates someone higher than average, they must rate someone else (or themselves) lower than average.

### 2. Average Peer Rating (APR)
The **Average Peer Rating ($\text{APR}$)** for a student is the average of all adjusted ratings ($\text{AdjR}$) they received from their teammates (excluding their own self-review rating):

$$\text{APR} = \frac{\sum \text{Adjusted Ratings Received}}{\text{Count of Teammates who Reviewed}}$$

*Range: $0.0$ to $3.0$ (values higher than 3.0 are mathematically possible if a student is highly favored by peers, but capped/normalized overall).*

### 3. Lecturer Evaluation (LE)
The **Lecturer Evaluation ($\text{LE}$)** is an individual score from $0.0$ to $3.0$ given directly to a student by the lecturer. 
*   **Default Behavior:** If the lecturer does not provide an individual evaluation, it defaults to the student's own $\text{APR}$.

### 4. Final Mark Calculation
The final mark combines the group project mark, peer evaluations, and lecturer reviews. It is calculated as follows:

$$\text{Final Mark} = \text{AM} \times \left(0.5 + 0.25 \times \frac{\text{APR}}{3.0} + 0.25 \times \frac{\text{LE}}{3.0}\right)$$

Where:
*   **$\text{AM}$ (Assignment Mark):** The group mark (0–100%) given to the team's submission by the lecturer.
*   **$\text{APR}$:** The student's Average Peer Rating (0.0–3.0).
*   **$\text{LE}$:** The student's Lecturer Evaluation (0.0–3.0).

*This gives a weight of 50% to the overall team output, 25% to peer feedback, and 25% to lecturer assessment.*

### 5. Self-Review Penalty
Failing to submit peer evaluations results in an immediate penalty:
> [!WARNING]
> **If a student does not submit their peer evaluation form for a course, their Final Mark is automatically set to $0.0\%$, regardless of the team's project mark.**

---

## 📋 CSV Import & Export Workflows

SPRS features simple, robust CSV uploaders that allow lecturers to manage large classes easily.

### 1. Course Roster Import (New Course Setup)
When creating a course, lecturers upload a student roster. The system parses the CSV and automatically creates students, assigns them temporary secure passwords, and builds sections and groups.

*   **Template Download:** [Click to download example template](file:///home/jax/coding/Student-Peer-Review-Website/example.csv)
*   **Columns required:**
    ```csv
    email,studentId,name,section,group
    ali@student.mmu.edu.my,1001,Ali Bin Ahmad,TC1L,1
    abu@student.mmu.edu.my,1002,Abu Bakar,TC1L,1
    choong@student.mmu.edu.my,1003,Choong Wei,TC1L,1
    ```

### 2. Marks Import Template (Moodle Gradebook Compatibility)
Once a project is graded, the lecturer can download a pre-populated CSV template from the course page containing all students. The lecturer fills in the group project mark and individual evaluations, then uploads it back.

*   **Headers:**
    ```csv
    Student Email,Student Name,Section Code,Group Name,Group Mark,Lecturer Rating
    ali@student.mmu.edu.my,Ali Bin Ahmad,TC1L,1,85.0,2.8
    ```
    *   **Group Mark:** Decimal out of 100.
    *   **Lecturer Rating:** Decimal from 0.0 to 3.0 (optional, defaults to APR if blank).

### 3. Final Marks Export
After reviews close, lecturers can export the final calculated marks as a CSV. This file is formatted for easy mapping and importing into Moodle and other LMS platforms.

*   **Headers:**
    ```csv
    Student ID,Student Email,Student Name,Section,Group,Assignment Mark,Avg Peer Rating,Lecturer Evaluation,Penalty,Final Calculated Mark
    1001,ali@student.mmu.edu.my,Ali Bin Ahmad,TC1L,1,85.0,2.95,2.8,NO,84.22
    ```

---

## 🛠️ Customizable Self-Review Questions

SPRS allows lecturers to customize the questions students answer during the self-assessment phase (Part 1 of the peer review).

*   **Modular Layouts:** Lecturers can create reusable "Question Layouts" (e.g., *Technical Focus*, *Written Report Focus*, or *General Reflection*) and assign them to specific courses.
*   **System Defaults:** If no layout is selected, the course defaults to a system-wide layout containing:
    1. *Describe your communication skills and how they impacted the group.*
    2. *Describe your technical contribution to the project.*
    3. *Describe your teamwork and collaboration.*
    4. *Describe your overall contribution to the project.*
*   **Strict Validations:** To prevent low-effort answers, self-assessment inputs and peer review comments enforce a **minimum length of 30 characters**.

---

## 🚀 Quick Start Guide

### Prerequisites
*   **Ruby:** `3.3.11` (specified in [.ruby-version](file:///home/jax/coding/Student-Peer-Review-Website/.ruby-version))
*   **Database:** PostgreSQL
*   **Asset Compiler:** Tailwind CSS CLI (configured through `tailwindcss-rails`)

### Local Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Student-Peer-Review-Website.git
    cd Student-Peer-Review-Website
    ```

2.  **Install dependencies:**
    ```bash
    bundle install
    ```

3.  **Setup the database:**
    Make sure your PostgreSQL service is running and configure credentials in `.env` if necessary. Then run:
    ```bash
    rails db:create
    rails db:migrate
    ```

4.  **Seed Default Layouts and Questions:**
    Seed the database to establish the default question layouts and configuration items:
    ```bash
    rails db:seed
    ```

5.  **Run Development Server:**
    Run the application using `bin/dev` to run both the Rails server and Tailwind CSS compile watcher concurrently:
    ```bash
    bin/dev
    ```
    The application will be accessible locally at `http://localhost:3000`.

### Running the Test Suite
The codebase is covered by an RSpec test suite. Run tests using:
```bash
bundle exec rspec
```

---

## 🌐 Live Deployed Application

The system is deployed and fully operational at:
👉 **[https://sprs.tail28f96f.ts.net/](https://sprs.tail28f96f.ts.net/)**

You can register a Lecturer account, upload an enrollment roster CSV, customize question layouts, and test student review submissions live on the platform.
