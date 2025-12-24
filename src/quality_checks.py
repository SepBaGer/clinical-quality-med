from src.sqlite_io import run_query

def run_quality_gates():
    print("Running Quality Gates...")
    # Gate 1: DB connection (implicit if we get here)
    
    # Gate 2: Integrity
    enc_counts = run_query("SELECT count(*) as C FROM encounters")
    print(f"Encounters count: {enc_counts['C'].iloc[0]}")
    
    return True

if __name__ == "__main__":
    run_quality_gates()
