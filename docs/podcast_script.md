# 🎙️ ML Leakage Detector Podcast Script

## "How to Pass the Mercor Domain Expert Assessment"

---

### INTRODUCTION

**[Speaker 1]:** Hey there! Welcome to another episode. Today, we're going to break down a technical project that can help you land high-paying AI evaluation contracts - specifically, the Mercor Domain Expert assessment.

**[Speaker 2]:** That's right! We're talking about the ML Leakage Detector - a production-grade tool that detects data leakage in Machine Learning pipelines using Python's Abstract Syntax Tree, or AST.

**[Speaker 1]:** And more importantly, we're going to teach you how to explain this project in a job interview, specifically answering the three hardest questions they'll throw at you.

**[Speaker 2]:** Let's dive in!

---

### PART 1: What is ML Leakage?

**[Speaker 1]:** Before we get to the interview questions, let's make sure we understand the core concept.

**[Speaker 2]:** Data Leakage in ML is when information from the test set accidentally "leaks" into the training process. It's like a student seeing the exam answers before taking the test - they'll look smart in practice but fail in the real world.

**[Speaker 1]:** Exactly! The ML Leakage Detector acts like an automated proctor that scans your code to make sure the "answer key" (the test data) is properly hidden.

**[Speaker 2]:** The project uses AST parsing - which is a fancy way of saying it converts code into a logical tree structure and analyzes the intent, not just keywords.

---

### PART 2: The Three Interview Questions

**[Speaker 1]:** Now, let's break down the three hardest questions from the Mercor Domain Expert assessment.

---

#### QUESTION 1: AST Robustness

**[Speaker 2]:** **The Question:** "How would you modify your LeakageDetector to distinguish between a dangerous imputation and a safe imputation that happens AFTER the train/test split is defined?"

**[Speaker 1]:** **Why They Ask This:** They want to see if you understand the difference between simple pattern matching and semantic analysis. Your current detector finds keywords like `fillna()` anywhere in the code - it doesn't understand when the operation happens.

**[Speaker 2]:** **The Approach:**

1. Acknowledge the current limitation
2. Explain the concept of Control Flow Analysis
3. Describe Variable Tracking

**[Speaker 1]:** **The Model Answer:**

> "My current detector uses pattern matching - it finds keywords like fillna() anywhere in the code. To fix this, I would implement Control Flow Analysis with Variable Tracking.
>
> Essentially, I would track when train_test_split() is called and mark those variables (X_train, X_test). Then, I would only flag imputation as dangerous if it happens BEFORE those variables are created.
>
> This transforms the detector from a simple keyword scanner into a semantic analyzer that understands WHEN operations happen, not just WHAT operations exist."

**[Speaker 2]:** **Key Talking Point:** The phrase "semantic analyzer" shows depth. They're looking for engineers who don't just write code - they understand program flow.

---

#### QUESTION 2: False Positive Handling

**[Speaker 1]:** **The Question:** "Walk me through how you would modify your AST visitor to detect if a transformer is encapsulated within a Pipeline, and why this matters for developer trust."

**[Speaker 2]:** **Why They Ask This:** Because false positives cause "alert fatigue." If your tool always cries wolf, developers stop listening. They want to see if you understand sklearn's security model.

**[Speaker 1]:** **The Approach:**

1. Identify the problem: Pipeline contains transformers but detector flags them anyway
2. Explain the "Safe List" concept
3. Show understanding of domain (sklearn)

**[Speaker 2]:** **The Model Answer:**

> "The detector currently flags SimpleImputer or StandardScaler without checking if they're protected inside sklearn.Pipeline.
>
> To fix this, I would implement a Safe List in my AST visitor. When the visitor encounters a Pipeline() call, it would extract the 'steps' argument, identify the transformer calls inside, and mark their AST node IDs as 'safe.'
>
> Later, when checking for leakage, the visitor would skip any transformer with an ID in the Safe List.
>
> This matters because static analysis is only as good as its false positive rate. By showing we understand sklearn's security model, we prove we're building production-grade tools, not just academic exercises."

**[Speaker 1]:** **Key Talking Point:** "Production-grade" is the magic phrase. They want engineers who ship real tools, not just proofs of concept.

---

#### QUESTION 3: Production Deployment

**[Speaker 2]:** **The Question:** "If a user runs your CLI on a 10,000-line legacy codebase and it returns 50 potential leaks, how would you prioritize which ones to fix first?"

**[Speaker 1]:** **Why They Ask This:** Because real-world codebases are messy. They want to see if you think about UX, prioritization, and business impact.

**[Speaker 2]:** **The Approach:**

1. Introduce a severity system
2. Explain the prioritization logic
3. Describe CLI output strategy

**[Speaker 1]:** **The Model Answer:**

> "I would implement a 3-Tier Severity System based on ML engineering risk:
>
> CRITICAL - Things like target encoding or feature selection before split. These make the model fundamentally broken.
>
> HIGH - Things like scaling before split or time-series shuffle. These cause performance inflation.
>
> MEDIUM - Manual sequential splits. Minor impact, might be intentional.
>
> The CLI would output a prioritized report, sorting by severity first. This turns static analysis into an actionable roadmap - developers don't need to know everything is wrong, they need to know what to fix FIRST."

**[Speaker 2]:** **Key Talking Point:** "Actionable roadmap" shows you think about the end-user experience, not just the technical solution.

---

### PART 3: How to Frame Your Answers

**[Speaker 1]:** Here's the secret to acing these interviews:

**[Speaker 2]:** **1. Start with the PROBLEM** - Before explaining your solution, state what limitation you're addressing.

**[Speaker 1]:** **2. Use the STAR method** - Situation (the bug), Task (fix it), Action (your solution), Result (improved detection).

**[Speaker 2]:** **3. Show domain knowledge** - Mention things like sklearn.Pipeline, train_test_split, and Cross-Validation to prove you understand ML workflows.

**[Speaker 1]:** **4. Emphasize production-readiness** - Always tie your answer back to real-world impact: "This reduces false positives by 40%" or "This helps developers prioritize their time."

---

### PART 4: The Project's Technical Stack

**[Speaker 2]:** Let me give you some quick facts about the ML Leakage Detector that will impress interviewers:

**[Speaker 1]:** **Detection Patterns (6 types):**

- Imputation before split
- Scaling before split  
- Target encoding before split
- Feature selection before split
- Sequential split (no shuffling)
- Time-series shuffle

**[Speaker 2]:** **Technical Features:**

- AST-based parsing (not just regex/keywords)
- Pipeline awareness (reduces false positives)
- CLI with JSON output for CI/CD
- GitHub Actions integration for automated checks
- 12 passing tests with 70% coverage

**[Speaker 1]:** **Why it matters for Mercor:**

- Demonstrates code validation skills
- Shows understanding of ML pitfalls
- Proves you can build production tools
- Portfolio piece for AI evaluation roles

---

### CONCLUSION

**[Speaker 2]:** And that's a wrap! You now have everything you need to explain the ML Leakage Detector in your Mercor Domain Expert interview.

**[Speaker 1]:** Remember: They're not just testing your technical skills - they're testing your ability to communicate complex concepts clearly and think about production implications.

**[Speaker 2]:** Good luck with your assessment! You've got this! 🎯

---

### 📝 QUICK REFERENCE - ANSWER FRAMEWORK

| Question | Problem | Solution | Key Phrase |
|----------|---------|----------|------------|
| AST Robustness | Can't distinguish WHEN operations happen | Variable Tracking + Control Flow | "Semantic analyzer" |
| False Positive Handling | Flags Pipeline transformers as leaks | Safe List using AST node IDs | "Production-grade" |
| Production Deployment | 50 leaks - where to start? | 3-tier severity system | "Actionable roadmap" |

---

*Generated for Mercor Domain Expert Assessment Prep*
*Project: ML Leakage Detector by Dennis Omboga*
