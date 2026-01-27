from src.detector import LeakageDetector

def run_demo():
    detector = LeakageDetector()
    
    # 1. Test Imputation Leak
    code_1 = "df = df.fillna(0)\nX_train = df[:100]"
    print(f"Testing Scenario 1:\n{code_1}")
    print(detector.generate_report(detector.detect(code_1)))
    print("-" * 30)

    # 2. Test Correct Pipeline
    code_2 = "from sklearn.model_selection import train_test_split\nX_train, X_test = train_test_split(X)"
    print(f"Testing Scenario 2:\n{code_2}")
    print(detector.generate_report(detector.detect(code_2)))

if __name__ == "__main__":
    run_demo()
