#!/usr/bin/env bash
# Validate all papers referenced in study/architecture_value_research.md
# Usage: ./tools/refcheck/check-architecture-papers.sh [--rate-limit N]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CHECK="uv run python ${SCRIPT_DIR}/check_reference.py"
RATE="${1:---rate-limit}"
RATE_VAL="${2:-0.5}"

echo "=== Architecture Value Research — Reference Validation ==="
echo ""

# Track results
pass=0
fail=0
total=0

check() {
    local label="$1"
    shift
    total=$((total + 1))
    echo -n "[$total] $label ... "
    result=$($CHECK "$@" 2>&1) && {
        echo "$result"
        pass=$((pass + 1))
    } || {
        echo "✗ NOT FOUND"
        fail=$((fail + 1))
    }
    sleep 1
}

echo "--- Track 1: Architecture MORE important ---"
check "Boeckeler 2023 (Fowler/ThoughtWorks)" --title "Exploring Generative AI" --author "Boeckeler" --year 2023
check "Ford/Parsons/Kua 2023 (Evolutionary Architectures)" --title "Building Evolutionary Architectures" --author "Ford" --year 2023

echo ""
echo "--- Track 2: Evaluation methods ---"
check "Kazman/ATAM 2000" --title "ATAM Method for Architecture Evaluation" --author "Kazman" --year 2000
check "Claessen/Hughes 2000 (QuickCheck)" --title "QuickCheck Lightweight Tool Random Testing" --author "Claessen" --year 2000
check "Verdecchia/Kruchten/Lago 2020 (Arch Tech Debt)" --title "Architectural Technical Debt Grounded Theory" --author "Verdecchia" --year 2020

echo ""
echo "--- Track 3: Architecture + Trust/Safety ---"
check "Parnas 1972" --title "Criteria To Be Used in Decomposing Systems into Modules" --author "Parnas" --year 1972
check "Laprie/Avizienis 2004 (Dependability)" --title "Basic Concepts Taxonomy Dependable Secure Computing" --author "Avizienis" --year 2004
check "Kelly/Weaver 2004 (GSN)" --title "Goal Structuring Notation Safety Argument" --author "Kelly" --year 2004
check "MacCormack/Baldwin 2012 (Conway's Law)" --title "Exploring Duality Product Organizational Architectures" --author "MacCormack" --year 2012
check "Abadi/Lamport 1995 (Assume-Guarantee)" --title "Conjoining Specifications" --author "Abadi" --year 1995

echo ""
echo "--- Track 4: Obsolescence ---"
check "Welsh 2023 (End of Programming)" --title "The End of Programming" --author "Welsh" --year 2023
check "Storey 2026 (Intent Debt)" --doi "10.48550/arXiv.2603.22106"

echo ""
echo "--- Track 5: Recent papers (2025-2026) ---"
check "Konrad 2026 (Architecture Without Architects)" --doi "10.48550/arXiv.2604.04990"
check "Amasanti/Jahic 2025 (AI Impact on Architecture)" --doi "10.48550/arXiv.2506.17833"
check "Esposito et al 2025 (GenAI for Architecture MLR)" --doi "10.48550/arXiv.2503.13310"
check "Su et al 2026 (ADR Violation Detection)" --doi "10.48550/arXiv.2602.07609"
check "Schmid et al 2025 (Architecture Meets LLMs SLR)" --doi "10.48550/arXiv.2505.16697"
check "Khati et al 2025 (Trust Terrain)" --doi "10.48550/arXiv.2503.13793"

echo ""
echo "=== Results: ${pass}/${total} validated, ${fail} failed ==="
